import numpy as np
import common
import weightModules
from array import array
import os
filepath = os.path.abspath(__file__)
karimpath = os.path.dirname(os.path.dirname(filepath))
year  = "18"
yearL = "2018"
sfDir = os.path.join(karimpath, "data", "UL_"+year)

from correctionlib import _core

#Download the correct JSON files 
print(os.path.join(sfDir, "electron.json"))
evaluator_EG = _core.CorrectionSet.from_file(os.path.join(sfDir, "electron.json"))

muIDSFs_tight = weightModules.LeptonSFs(
    csv     = os.path.join(sfDir, "Efficiencies_muon_generalTracks_Z_Run2018_UL_ID.csv"),
    sfName  = "NUM_TightID_DEN_TrackerMuons_abseta_pt")

muIDSFs_loose = weightModules.LeptonSFs(
    csv     = os.path.join(sfDir, "Efficiencies_muon_generalTracks_Z_Run2018_UL_ID.csv"),
    sfName  = "NUM_LooseID_DEN_TrackerMuons_abseta_pt")

# initialize lepton Reco/Iso scale factors
muIsoSFs_tight  = weightModules.LeptonSFs(
    csv     = os.path.join(sfDir, "Efficiencies_muon_generalTracks_Z_Run2018_UL_ISO.csv"),
    sfName  = "NUM_TightRelIso_DEN_TightIDandIPCut_abseta_pt")
muIsoSFs_loose  = weightModules.LeptonSFs(
    csv     = os.path.join(sfDir, "Efficiencies_muon_generalTracks_Z_Run2018_UL_ISO.csv"),
    sfName  = "NUM_LooseRelIso_DEN_LooseID_abseta_pt")


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
    wrapper.SetIntVar("Evt_ID")   
    wrapper.SetIntVar("Evt_Run")   
    wrapper.SetIntVar("Evt_Lumi")   

    # electron scale factors
    wrapper.SetFloatVar("eleIDSF_tight")
    wrapper.SetFloatVar("eleIDSF_tight_up")
    wrapper.SetFloatVar("eleIDSF_tight_down")

    wrapper.SetFloatVar("eleIDSF_loose")
    wrapper.SetFloatVar("eleIDSF_loose_up")
    wrapper.SetFloatVar("eleIDSF_loose_down")

    wrapper.SetFloatVar("eleRecoSF_tight")
    wrapper.SetFloatVar("eleRecoSF_tight_up")
    wrapper.SetFloatVar("eleRecoSF_tight_down")

    wrapper.SetFloatVar("eleRecoSF_loose")
    wrapper.SetFloatVar("eleRecoSF_loose_up")
    wrapper.SetFloatVar("eleRecoSF_loose_down")

    # muon scale factors
    wrapper.SetFloatVar("muIDSF_tight")
    wrapper.SetFloatVar("muIDSF_tight_up")
    wrapper.SetFloatVar("muIDSF_tight_down")

    wrapper.SetFloatVar("muIDSF_loose")
    wrapper.SetFloatVar("muIDSF_loose_up")
    wrapper.SetFloatVar("muIDSF_loose_down")

    wrapper.SetFloatVar("muIsoSF_tight")
    wrapper.SetFloatVar("muIsoSF_tight_up")
    wrapper.SetFloatVar("muIsoSF_tight_down")
      
    wrapper.SetFloatVar("muIsoSF_loose")
    wrapper.SetFloatVar("muIsoSF_loose_up")
    wrapper.SetFloatVar("muIsoSF_loose_down")

    # photon scale factors
    wrapper.SetFloatVar("phoEffSF_tight")
    wrapper.SetFloatVar("phoEffSF_tight_up")
    wrapper.SetFloatVar("phoEffSF_tight_down")

    wrapper.SetFloatVar("phoEffSF_loose")
    wrapper.SetFloatVar("phoEffSF_loose_up")
    wrapper.SetFloatVar("phoEffSF_loose_down")


def calculate_variables(event, wrapper, sample, jec = None, genWeights = None):
    '''
    calculate weights
    '''
    isData = False
    if "SingleEl" in sample or "EGamma" in sample or "SingleMu" in sample or "MET" in sample:
        isData = True



    # add basic information for friend trees
    wrapper.branchArrays["Evt_ID"][0] = getattr(event, "Evt_ID")
    wrapper.branchArrays["Evt_Run"][0]   = getattr(event, "Evt_Run")
    wrapper.branchArrays["Evt_Lumi"][0]  = getattr(event, "Evt_Lumi")
    
    # electron scale factors
    # tight electrons
    elIDSF_tight = 1.
    elIDSF_tight_up = 1.
    elIDSF_tight_down = 1.

    elRecoSF_tight = 1.
    elRecoSF_tight_up = 1.
    elRecoSF_tight_down = 1.

    for iEl in range(getattr(event, "N_TightElectrons")):
        # TODO super cluster eta
        if getattr(event, "TightElectron_Pt")[iEl] < 500:
            pt = getattr(event, "TightElectron_Pt")[iEl]
        else:
            pt = 499.
        idsf = evaluator_EG["UL-Electron-ID-SF"].evaluate(yearL,"sf","Tight", getattr(event, "TightElectron_EtaSC")[iEl], pt)
        idsfErr = evaluator_EG["UL-Electron-ID-SF"].evaluate(yearL,"syst","Tight", getattr(event, "TightElectron_EtaSC")[iEl], pt)

        recosf    = evaluator_EG["UL-Electron-ID-SF"].evaluate(yearL,"sf","RecoAbove20", getattr(event, "TightElectron_EtaSC")[iEl], pt)
        recosfErr    = evaluator_EG["UL-Electron-ID-SF"].evaluate(yearL,"syst","RecoAbove20", getattr(event, "TightElectron_EtaSC")[iEl], pt)

        elIDSF_tight        *= idsf
        elIDSF_tight_up     *= (idsf + idsfErr)
        elIDSF_tight_down   *= (idsf - idsfErr)

        elRecoSF_tight      *= recosf
        elRecoSF_tight_up   *= (recosf + recosfErr)
        elRecoSF_tight_down *= (recosf - recosfErr)

    wrapper.branchArrays["eleIDSF_tight"][0]   = elIDSF_tight
    wrapper.branchArrays["eleIDSF_tight_up"][0]   = elIDSF_tight_up
    wrapper.branchArrays["eleIDSF_tight_down"][0]   = elIDSF_tight_down

    wrapper.branchArrays["eleRecoSF_tight"][0]   = elRecoSF_tight
    wrapper.branchArrays["eleRecoSF_tight_up"][0]   = elRecoSF_tight_up
    wrapper.branchArrays["eleRecoSF_tight_down"][0]   = elRecoSF_tight_down

    # loose electrons
    elIDSF_loose = 1.
    elIDSF_loose_up = 1.
    elIDSF_loose_down = 1.

    elRecoSF_loose = 1.
    elRecoSF_loose_up = 1.
    elRecoSF_loose_down = 1.

    for iEl in range(getattr(event, "N_LooseElectrons")):
        # TODO super cluster eta
        if getattr(event, "LooseElectron_Pt")[iEl] < 500:
            pt = getattr(event, "LooseElectron_Pt")[iEl]
        else:
            pt = 499.
        idsf = evaluator_EG["UL-Electron-ID-SF"].evaluate(yearL,"sf","Loose", getattr(event, "LooseElectron_EtaSC")[iEl], pt)
        idsfErr = evaluator_EG["UL-Electron-ID-SF"].evaluate(yearL,"syst","Loose", getattr(event, "LooseElectron_EtaSC")[iEl], pt)

        if pt >= 20.:
            recosf    = evaluator_EG["UL-Electron-ID-SF"].evaluate(yearL,"sf","RecoAbove20", getattr(event, "LooseElectron_EtaSC")[iEl], pt)
            recosfErr    = evaluator_EG["UL-Electron-ID-SF"].evaluate(yearL,"syst","RecoAbove20", getattr(event, "LooseElectron_EtaSC")[iEl], pt)
        else:
            recosf    = evaluator_EG["UL-Electron-ID-SF"].evaluate(yearL,"sf","RecoBelow20", getattr(event, "LooseElectron_EtaSC")[iEl], pt)
            recosfErr    = evaluator_EG["UL-Electron-ID-SF"].evaluate(yearL,"syst","RecoBelow20", getattr(event, "LooseElectron_EtaSC")[iEl], pt)

        elIDSF_loose        *= idsf
        elIDSF_loose_up     *= (idsf + idsfErr)
        elIDSF_loose_down   *= (idsf - idsfErr)

        elRecoSF_loose      *= recosf
        elRecoSF_loose_up   *= (recosf + recosfErr)
        elRecoSF_loose_down *= (recosf - recosfErr)

    wrapper.branchArrays["eleIDSF_loose"][0]   = elIDSF_loose
    wrapper.branchArrays["eleIDSF_loose_up"][0]   = elIDSF_loose_up
    wrapper.branchArrays["eleIDSF_loose_down"][0]   = elIDSF_loose_down

    wrapper.branchArrays["eleRecoSF_loose"][0]   = elRecoSF_loose
    wrapper.branchArrays["eleRecoSF_loose_up"][0]   = elRecoSF_loose_up
    wrapper.branchArrays["eleRecoSF_loose_down"][0]   = elRecoSF_loose_down

    # tight photons
    phoEffSF_tight = 1.
    phoEffSF_tight_up = 1.
    phoEffSF_tight_down = 1.

    for iPho in range(getattr(event, "N_TightPhotons")):
        if getattr(event, "TightPhoton_Pt")[iEl] < 500:
            pt = getattr(event, "TightPhoton_Pt")[iPho]
        else:
            pt = 499.
        sf = evaluator_EG["UL-Photon-ID-SF"].evaluate(yearL,"sf","Tight", getattr(event, "TightPhoton_Eta")[iPho], pt)
        sfErr = evaluator_EG["UL-Photon-ID-SF"].evaluate(yearL,"syst","Tight", getattr(event, "TightPhoton_Eta")[iPho], pt)

        phoEffSF_tight        *= sf
        phoEffSF_tight_up     *= (sf + sfErr)
        phoEffSF_tight_down   *= (sf - sfErr)

    wrapper.branchArrays["phoEffSF_tight"][0]   = phoEffSF_tight
    wrapper.branchArrays["phoEffSF_tight_up"][0]   = phoEffSF_tight_up
    wrapper.branchArrays["phoEffSF_tight_down"][0]   = phoEffSF_tight_down

    # loose photons
    phoEffSF_loose = 1.
    phoEffSF_loose_up = 1.
    phoEffSF_loose_down = 1.

    for iPho in range(getattr(event, "N_LoosePhotons")):
        # TODO super cluster eta
        if getattr(event, "TightPhoton_Pt")[iPho] < 500:
            pt = getattr(event, "TightPhoton_Pt")[iPho]
        else:
            pt = 499.
        pt = getattr(event, "LoosePhoton_Pt")[iPho]
        sf = evaluator_EG["UL-Photon-ID-SF"].evaluate(yearL,"sf","Loose", getattr(event, "LoosePhoton_Eta")[iPho], pt)
        sfErr = evaluator_EG["UL-Photon-ID-SF"].evaluate(yearL,"syst","Loose", getattr(event, "LoosePhoton_Eta")[iPho], pt)
        print("########")
        print(sf)
        print("########")
        phoEffSF_loose        *= sf
        phoEffSF_loose_up     *= (sf + sfErr)
        phoEffSF_loose_down   *= (sf - sfErr)

    wrapper.branchArrays["phoEffSF_loose"][0]   = phoEffSF_loose
    wrapper.branchArrays["phoEffSF_loose_up"][0]   = phoEffSF_loose_up
    wrapper.branchArrays["phoEffSF_loose_down"][0]   = phoEffSF_loose_down
            
    # tight muons
    muIDSF_tight = 1.
    muIDSF_tight_up = 1.
    muIDSF_tight_down = 1.

    muIsoSF_tight = 1.
    muIsoSF_tight_up = 1.
    muIsoSF_tight_down = 1.

    for iMu in range(getattr(event, "N_TightMuons")):
        idsf    = muIDSFs_tight.getSFs(  getattr(event, "TightMuon_Pt")[iMu], abs(getattr(event, "TightMuon_Eta")[iMu]))
        isosf   = muIsoSFs_tight.getSFs( getattr(event, "TightMuon_Pt")[iMu], abs(getattr(event, "TightMuon_Eta")[iMu]))

        muIDSF_tight        *= idsf.loc["central"]
        muIDSF_tight_up     *= idsf.loc["up"]
        muIDSF_tight_down   *= idsf.loc["down"]

        muIsoSF_tight       *= isosf.loc["central"]
        muIsoSF_tight_up    *= isosf.loc["up"]
        muIsoSF_tight_down  *= isosf.loc["down"]

    wrapper.branchArrays["muIDSF_tight"][0]   = muIDSF_tight
    wrapper.branchArrays["muIDSF_tight_up"][0]   = muIDSF_tight_up
    wrapper.branchArrays["muIDSF_tight_down"][0]   = muIDSF_tight_down
    wrapper.branchArrays["muIsoSF_tight"][0]  = muIsoSF_tight
    wrapper.branchArrays["muIsoSF_tight_up"][0]  = muIsoSF_tight_up
    wrapper.branchArrays["muIsoSF_tight_down"][0]  = muIsoSF_tight_down

    # loose muons
    muIDSF_loose = 1.
    muIDSF_loose_up = 1.
    muIDSF_loose_down = 1.
    
    muIsoSF_loose = 1.
    muIsoSF_loose_up = 1.
    muIsoSF_loose_down = 1.

    for iMu in range(getattr(event, "N_LooseMuons")):
        idsf    = muIDSFs_loose.getSFs(  getattr(event, "LooseMuon_Pt")[iMu], abs(getattr(event, "LooseMuon_Eta")[iMu]))
        isosf   = muIsoSFs_loose.getSFs( getattr(event, "LooseMuon_Pt")[iMu], abs(getattr(event, "LooseMuon_Eta")[iMu]))

        muIDSF_loose        *= idsf.loc["central"]
        muIDSF_loose_up     *= idsf.loc["up"]
        muIDSF_loose_down   *= idsf.loc["down"]

        muIsoSF_loose       *= isosf.loc["central"]
        muIsoSF_loose_up    *= isosf.loc["up"]
        muIsoSF_loose_down  *= isosf.loc["down"]

    wrapper.branchArrays["muIDSF_loose"][0]   = muIDSF_loose
    wrapper.branchArrays["muIDSF_loose_up"][0]   = muIDSF_loose_up
    wrapper.branchArrays["muIDSF_loose_down"][0]   = muIDSF_loose_down
    wrapper.branchArrays["muIsoSF_loose"][0]  = muIsoSF_loose
    wrapper.branchArrays["muIsoSF_loose_up"][0]  = muIsoSF_loose_up
    wrapper.branchArrays["muIsoSF_loose_down"][0]  = muIsoSF_loose_down

    return event

