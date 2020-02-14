import itertools
import pandas as pd
import numpy as np
from array import array

class Hypotheses:
    maxJets = 10
    def __init__(self, config):
        '''
        initialize config settings and variable lists
        '''
        self.naming   = config.get_reco_naming()
        self.objects  = config.get_objects()
        self.features = config.get_features()
        print("list of objects for reconstruction: ")
        print(self.objects)
        print("list of features for reconstruction: ")
        print(self.features)
        self.template = "{name}_OBJECT_FEATURE".format(name = self.naming)
        print("naming template for variables:" )
        print(self.template)

        # load function to calculate variables for all hypotheses
        self.calculate_variables = config.calculate_variables


        # generate a variable list that needs to be filled from ntuple information
        self.variables = []
        for feat in self.features:
            for obj in self.objects:
                self.variables.append(
                    self.template.replace("OBJECT",obj).replace("FEATURE", feat))

        # add jet indices for all reconstructable objects
        for obj in self.objects:
            self.variables.append(
                self.template.replace("OBJECT",obj).replace("FEATURE", "idx"))

        self.baseVariables = len(self.variables)
        # add additional variables to variable list
        self.additional_variables = config.get_additional_variables()
        self.additional_variables+= ["Evt_ID", "Evt_Lumi", "Evt_Run"]
        self.additional_variables = list(set(self.additional_variables))
        for av in self.additional_variables:
            self.variables.append(av)

        self.hypothesisJets = len(self.objects)
        print("\nhypothesis requires {njets} jets\n".format(njets = self.hypothesisJets))

    def initPermutations(self):
        '''
        save permutations in a dictionary so is doesnt have to be created for every event
        all permutations for njets = [min required - max jets] are created
        '''
        self.permutations = {}
        for nJets in range(self.hypothesisJets,self.maxJets+1):
            self.permutations[nJets] = list(
                itertools.permutations(range(0,nJets), r = self.hypothesisJets)
                )
        print("\npermutation configurations initialized.")
        print("maximum number of jets set to {}\n".format(self.maxJets))

    def GetPermutations(self, event, nJets):
        '''
        get dataframe with all permutations for a single event with nJets
        returns error = True if e.g. number of jets is too low

        output: DataFrame, error
        '''
        error = False
        if nJets < self.hypothesisJets:
            # fill dummy entry if number of jets is not high enough
            error = True
            data = np.zeros(shape = (1, len(self.variables)))
            data[:,:self.baseVariables] = -99.
            idy = self.baseVariables
        else:
            # fill data matrix with permutations
            nJets = min(nJets, 10)
            data = np.zeros(shape = (len(self.permutations[nJets]), len(self.variables)))

            idy = 0
            for feat in self.features:
                variable = getattr(event, "Jet_{}".format(feat))
                for i, obj in enumerate(self.objects):
                    for idx, p in enumerate(self.permutations[nJets]):
                        data[idx,idy] = variable[p[i]]
                    idy += 1
            for i, obj in enumerate(self.objects):
                for idx, p in enumerate(self.permutations[nJets]):
                    data[idx, idy] = p[i]
                idy += 1

        for i, av in enumerate(self.additional_variables):
            data[:,idy] = getattr(event, self.additional_variables[i])
            idy += 1

        df = pd.DataFrame(data, columns = self.variables)
        return self.calculate_variables(df), error

