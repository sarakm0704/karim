import ROOT
import pandas as pd

import optparse

parser = optparse.OptionParser()
parser.add_option("-t",dest="trueInt",
    help = "histogram with true interactions")
parser.add_option("-d",dest="dataPU",
    help = "histogram with PU distribution in data")
parser.add_option("--dup",dest="dataPUup",
    help = "histogram with PU distribution in data varied up by 4.6%")
parser.add_option("--ddn",dest="dataPUdown",
    help = "histogram with PU distribution in data varied down by 4.6%")
(opts, args) = parser.parse_args()

fTrue = ROOT.TFile.Open(opts.trueInt)
hTrue = fTrue.Get("N_True")
hTrue.Scale(1./hTrue.Integral())

fData = ROOT.TFile.Open(opts.dataPU)
hData = fData.Get("pileup")
hData.Scale(1./hData.Integral())

fUp = ROOT.TFile.Open(opts.dataPUup)
hUp = fUp.Get("pileup")
hUp.Scale(1./hUp.Integral())

fDn = ROOT.TFile.Open(opts.dataPUdown)
hDn = fDn.Get("pileup")
hDn.Scale(1./hDn.Integral())

data = {}
data["nPU"] = []
data["central"] = []
data["up"] = []
data["down"] = []
for iBin in range(100):
    if hTrue.GetBinContent(hData.GetXaxis().FindBin(iBin)) > 0:
        rNom = hData.GetBinContent(hData.GetXaxis().FindBin(iBin))/\
            hTrue.GetBinContent(hTrue.GetXaxis().FindBin(iBin))
        rUp  = hUp.GetBinContent(hUp.GetXaxis().FindBin(iBin))/\
            hTrue.GetBinContent(hTrue.GetXaxis().FindBin(iBin))
        rDn  = hDn.GetBinContent(hDn.GetXaxis().FindBin(iBin))/\
            hTrue.GetBinContent(hTrue.GetXaxis().FindBin(iBin))
        data["nPU"].append(iBin)
        data["central"].append(rNom)
        data["up"].append(rUp)
        data["down"].append(rDn)

df = pd.DataFrame.from_dict(data)
df.set_index("nPU", inplace = True, drop = True)
df.to_csv("pileup.csv", index = True)

