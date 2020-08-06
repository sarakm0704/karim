import numpy as np
import common

name = "RecoX"
def get_naming():
    '''
    define name for this reconstruction
    '''
    return name


def get_objects():
    '''
    define a list of objects considered for the reconstruction
    '''
    objects = [
        "B1", 
        "B2"       
        ]
    return objects


def get_features():
    '''
    define a list of features applicable for all objects defined in get_objects()
    '''
    features = [
        "btagValue", 
        "Pt", 
        "M", 
        "E", 
        "Eta", 
        "Phi"
        ]
    return features


def get_additional_objects():
    '''
    define dictionary of objects that are identified based on the reconstructed objects
    dictionary entries define the order by which the objects are defined.
    e.g. objects['Pt'] = [O1, O2] defiles O1 as the object with the highest Pt that is
    not part of the default reconstructed objects
    '''
    objects = {}
    return objects


def get_additional_variables():
    '''
    get names of additional variables which are already defined in ntuples
    which are needed for the dnn inputs
    '''
    variables = [
        "N_BTagsM",
        "N_Jets",

        "GenZ_B1_Phi",
        "GenZ_B2_Phi",
        "GenZ_B1_Eta",
        "GenZ_B2_Eta",


        "GenHiggs_B1_Phi",
        "GenHiggs_B2_Phi",
        "GenHiggs_B1_Eta",
        "GenHiggs_B2_Eta",
        ]
    return variables

def base_selection(event):
    return event.N_Jets>=2


def calculate_variables(df):
    '''
    calculate additional variables needed for DNN input
    '''

    # angular differences
    df[name+"_X_dPhi"]  = common.get_dPhi(df[name+"_B1_Phi"].values, df[name+"_B2_Phi"].values)
    df[name+"_X_dEta"]  = abs(df[name+"_B1_Eta"].values - df[name+"_B2_Eta"].values)
    df[name+"_X_dPt"]   = abs(df[name+"_B1_Pt"].values - df[name+"_B2_Pt"].values)
    df[name+"_X_dR"]    = np.sqrt(df[name+"_X_dEta"].values**2 + df[name+"_X_dPhi"].values**2)
    df[name+"_X_dKin"] = np.sqrt((df[name+"_X_dEta"].values/5.)**2 + \
                                (df[name+"_X_dPhi"].values/(2.*np.pi))**2 + \
                                (df[name+"_X_dPt"].values/1000.))

    # reconstruct X boson
    vectors = common.Vectors(df, name, ["B1", "B2"])
    vectors.add(["B1", "B2"], out = "X")

    df[name+"_X_Pt"]  = vectors.get("X", "Pt")
    df[name+"_X_Eta"] = vectors.get("X", "Eta")
    df[name+"_X_M"]   = vectors.get("X", "M")
    df[name+"_X_E"]   = vectors.get("X", "E")

    # log values
    for obj in ["B1", "B2", "X"]:
        df[name+"_"+obj+"_logPt"] = np.log(df[name+"_"+obj+"_Pt"].values)
        df[name+"_"+obj+"_logM"] = np.log(df[name+"_"+obj+"_M"].values)
        df[name+"_"+obj+"_logE"] = np.log(df[name+"_"+obj+"_E"].values)

    # 3D opening angle
    df[name+"_X_openingAngle"] = vectors.getOpeningAngle("B1", "B2")

    # boost
    vectors.boost(["B1", "B2", "X"], frame = "X")

    # add boosted variables
    for obj in ["B1", "B2", "X"]:
        df[name+"_"+obj+"_Pt_boosted"] = vectors.get(obj, "Pt", boostFrame = "X")
        df[name+"_"+obj+"_M_boosted"] = vectors.get(obj, "M", boostFrame = "X")
        df[name+"_"+obj+"_E_boosted"] = vectors.get(obj, "E", boostFrame = "X")
        df[name+"_"+obj+"_Eta_boosted"] = vectors.get(obj, "Eta", boostFrame = "X")
        df[name+"_"+obj+"_Phi_boosted"] = vectors.get(obj, "Phi", boostFrame = "X")

        df[name+"_"+obj+"_logPt_boosted"] = np.log(df[name+"_"+obj+"_Pt_boosted"])

    # boosted angular differences
    df[name+"_dPhi_boosted"] = common.get_dPhi(df[name+"_B1_Phi_boosted"].values, df[name+"_B2_Phi_boosted"].values)
    df[name+"_dEta_boosted"] = abs(df[name+"_B1_Eta_boosted"].values - df[name+"_B2_Eta_boosted"].values)
    df[name+"_dR_boosted"] = np.sqrt(df[name+"_dEta_boosted"].values**2 + df[name+"_dPhi_boosted"].values**2)

    df[name+"_dRGen_Z_genB1_recoB1"] = common.get_dR(
        eta1 = df["GenZ_B1_Eta"].values,
        phi1 = df["GenZ_B1_Phi"].values,
        eta2 = df[name+"_B1_Eta"].values,
        phi2 = df[name+"_B1_Phi"].values)

    df[name+"_dRGen_Z_genB2_recoB2"] = common.get_dR(
        eta1 = df["GenZ_B2_Eta"].values,
        phi1 = df["GenZ_B2_Phi"].values,
        eta2 = df[name+"_B2_Eta"].values,
        phi2 = df[name+"_B2_Phi"].values)

    df[name+"_dRGen_Z_genB1_recoB2"] = common.get_dR(
        eta1 = df["GenZ_B1_Eta"].values,
        phi1 = df["GenZ_B1_Phi"].values,
        eta2 = df[name+"_B2_Eta"].values,
        phi2 = df[name+"_B2_Phi"].values)

    df[name+"_dRGen_Z_genB2_recoB1"] = common.get_dR(
        eta1 = df["GenZ_B2_Eta"].values,
        phi1 = df["GenZ_B2_Phi"].values,
        eta2 = df[name+"_B1_Eta"].values,
        phi2 = df[name+"_B1_Phi"].values)



    df[name+"_dRGen_Higgs_genB1_recoB1"] = common.get_dR(
        eta1 = df["GenHiggs_B1_Eta"].values,
        phi1 = df["GenHiggs_B1_Phi"].values,
        eta2 = df[name+"_B1_Eta"].values,
        phi2 = df[name+"_B1_Phi"].values)

    df[name+"_dRGen_Higgs_genB2_recoB2"] = common.get_dR(
        eta1 = df["GenHiggs_B2_Eta"].values,
        phi1 = df["GenHiggs_B2_Phi"].values,
        eta2 = df[name+"_B2_Eta"].values,
        phi2 = df[name+"_B2_Phi"].values)

    df[name+"_dRGen_Higgs_genB1_recoB2"] = common.get_dR(
        eta1 = df["GenHiggs_B1_Eta"].values,
        phi1 = df["GenHiggs_B1_Phi"].values,
        eta2 = df[name+"_B2_Eta"].values,
        phi2 = df[name+"_B2_Phi"].values)

    df[name+"_dRGen_Higgs_genB2_recoB1"] = common.get_dR(
        eta1 = df["GenHiggs_B2_Eta"].values,
        phi1 = df["GenHiggs_B2_Phi"].values,
        eta2 = df[name+"_B1_Eta"].values,
        phi2 = df[name+"_B1_Phi"].values)

    return df

