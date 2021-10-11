import numpy as np
import common
import weightModules
from array import array
import os
import sys
from correctionlib import _core

filepath = os.path.abspath(__file__)
karimpath = os.path.dirname(os.path.dirname(filepath))

year = "18"
yearL = "2018"
sfDir = os.path.join(karimpath, "data", "UL_"+year)
sfDirLeg = os.path.join(karimpath, "data", "legacy_"+yearL)


btagSF = {}
btagEff = {}
for year in ["2017", "2018"]:
    sfDir = os.path.join(karimpath, "data", "UL_"+year[2:])
 
    btagSFjson = _core.CorrectionSet.from_file(os.path.join(sfDir, "bjets.json"))
    btagSF[year]   = btagSFjson["deepJet_106XUL"+year[2:]+"SF_wp"]   

    btagEffjson = _core.CorrectionSet.from_file(os.path.join(sfDir, "btagEff_ttbb_deepJet.json"))
    btagEff[year] = btagEffjson["btagEff"]

SFb_sys = ["up","down"]
SFl_sys = ["up","down"]

def get_additional_variables():
    '''
    get names of additional variables which are already defined in ntuples
    which are needed for the dnn inputs
    '''
    variables = [
        ]
    return variables

def base_selection(event):
    return True

def set_branches(wrapper, jec):
    suffix = "_"+jec

    if jec == "nom":
        for sys in SFb_sys:
            wrapper.SetFloatVar("fixedWPSFb_TM_"+sys+"_rel")
        for sys in SFl_sys:
            wrapper.SetFloatVar("fixedWPSFl_TM_"+sys+"_rel")

    wrapper.SetFloatVar("fixedWPSF_TM"+suffix)

# translate WPs into BTV internal name
wpDict = {"L": 0, "M": 1, "T": 2}
# translate flavor in to BTV internal name
flavDict = {5: 0, 4: 1, 0: 2}
def calculate_variables(event, wrapper, sample, jec, dataEra = None, genWeights = None):
    '''
    calculate weights
    '''

    suffix = "_"+jec

    P_MC_TM   = 1.
    P_DATA_TM = 1.
    if jec == "nom":
        Pb_DATA_TM = {}
        Pl_DATA_TM = {}
        for sys in SFb_sys:
            Pb_DATA_TM[sys] = 1.
        for sys in SFl_sys:
            Pl_DATA_TM[sys] = 1.

        sfb_M = {}
        sfb_T = {}
        sfl_M = {}
        sfl_T = {}

    for idx in range(getattr(event, "nJets"+suffix)):
        eta   = abs(getattr(event, "Jet_Eta"+suffix)[idx])
        pt    = getattr(event, "Jet_Pt"+suffix)[idx]
        ogflav = getattr(event, "Jet_Flav"+suffix)[idx]
        flav  = flavDict[ogflav]
        passes_M = getattr(event, "Jet_taggedM"+suffix)[idx]
        passes_T = getattr(event, "Jet_taggedM"+suffix)[idx]

        eff_M = btagEff[dataEra].evaluate("M", ogflav, eta, pt)
        eff_T = btagEff[dataEra].evaluate("T", ogflav, eta, pt)

        if flav == 2:
            sf_M = btagSF[dataEra].evaluate("central", "incl", 1, flav, eta, pt)
            sf_T = btagSF[dataEra].evaluate("central", "incl", 2, flav, eta, pt)
            if jec == "nom":
                for sys in SFl_sys:
                    sfl_M[sys] = btagSF[dataEra].evaluate(sys, "incl", 1, flav, eta, pt)
                    sfl_T[sys] = btagSF[dataEra].evaluate(sys, "incl", 2, flav, eta, pt)
        else:
            sf_M = btagSF[dataEra].evaluate("central", "comb", 1, flav, eta, pt)
            sf_T = btagSF[dataEra].evaluate("central", "comb", 2, flav, eta, pt)
            if jec == "nom":
                for sys in SFb_sys:
                    sfb_M[sys] = btagSF[dataEra].evaluate(sys, "comb", 1, flav, eta, pt)
                    sfb_T[sys] = btagSF[dataEra].evaluate(sys, "comb", 2, flav, eta, pt)

        if passes_T:
            P_MC_TM   *= eff_T
            P_DATA_TM *= eff_T*sf_T
            if jec == "nom":
                if flav == 2:
                    for sys in SFl_sys:
                        Pl_DATA_TM[sys] *= eff_T*sfl_T[sys]
                    for sys in SFb_sys:
                        Pb_DATA_TM[sys] *= eff_T*sf_T
                else:
                    for sys in SFb_sys:
                        Pb_DATA_TM[sys] *= eff_T*sfb_T[sys]
                    for sys in SFl_sys:
                        Pl_DATA_TM[sys] *= eff_T*sf_T
        elif passes_M:
            P_MC_TM   *= (eff_M      - eff_T)
            P_DATA_TM *= (eff_M*sf_M - eff_T*sf_T)
            if jec == "nom":
                if flav == 2:
                    for sys in SFl_sys:
                        Pl_DATA_TM[sys] *= (eff_M*sfl_M[sys] - eff_T*sfl_T[sys])
                    for sys in SFb_sys:
                        Pb_DATA_TM[sys] *= (eff_M*sf_M - eff_T*sf_T)
                else:
                    for sys in SFb_sys:
                        Pb_DATA_TM[sys] *= (eff_M*sfb_M[sys] - eff_T*sfb_T[sys])
                    for sys in SFl_sys:
                        Pl_DATA_TM[sys] *= (eff_M*sf_M - eff_T*sf_T)
        else:
            P_MC_TM   *= (1. - eff_M)
            P_DATA_TM *= (1. - eff_M*sf_M)  
            if jec == "nom":
                if flav == 2:
                    for sys in SFl_sys:
                        Pl_DATA_TM[sys] *= (1. - eff_M*sfl_M[sys])
                    for sys in SFb_sys:
                        Pb_DATA_TM[sys] *= (1. - eff_M*sf_M)
                else:
                    for sys in SFb_sys:
                        Pb_DATA_TM[sys] *= (1. - eff_M*sfb_M[sys])
                    for sys in SFl_sys:
                        Pl_DATA_TM[sys] *= (1. - eff_M*sf_M)


    wrapper.branchArrays["fixedWPSF_TM"+suffix][0] = P_DATA_TM/P_MC_TM
    if jec == "nom":
        for sys in SFl_sys:
            wrapper.branchArrays["fixedWPSFb_TM_"+sys+"_rel"][0] = Pl_DATA_TM[sys]/P_DATA_TM
        for sys in SFb_sys:
            wrapper.branchArrays["fixedWPSFl_TM_"+sys+"_rel"][0] = Pb_DATA_TM[sys]/P_DATA_TM
    return event

