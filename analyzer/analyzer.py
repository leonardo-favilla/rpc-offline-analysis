import ROOT
import sys
import optparse
import os
import pandas as pd
from tqdm.notebook import tqdm
import time
import json
from utils.openGeomFile import openGeomFile
from utils.fillsInfo import *
pd.set_option("display.max_colwidth", None)
ROOT.gStyle.SetOptStat(0)
sys.path.append('../')
from getUser import inituser, username, uid, workdir



############################
######### SETTINGS #########
############################
usage               = "python3 analyzer.py -f <fill_number> -r <runs_list> -d <detector_region> -c <collidingFile> -n <noisyStripsFile> -o <outJson_path>"
parser              = optparse.OptionParser(usage)
parser.add_option("-f", "--fill",               dest="fill",                                    type=int, help="Fill number")
parser.add_option("-r", "--runs",               dest="runs",                                    type=str, help="Runs list, in the form run1,run2,run3")
parser.add_option("-d", "--detector_region",    dest="detector_region",                         type=str, help="Detector region: Barrel_0, Barrel_1, Barrel_2, Barrel_3, Endcap_0, Endcap_1, Endcap_2, Endcap_3, Endcap_4, Endcap_5, Endcap_6, Endcap_7")
parser.add_option("-c", "--collidingFile",      dest="collidingFile",                           type=str, help="Colliding bunch-crossings file (.txt)")
parser.add_option("-o", "--outJson_path",       dest="outJson_path",                            type=str, help="Output json file path")
parser.add_option("-n", "--noisyStripsFile",    dest="noisyStripsFile",     default=None,                 help="Noisy strips file (.txt)")
(opt, args)         = parser.parse_args()
fill_number         = opt.fill
runs_list           = list(map(int, opt.runs.split(",")))
detector_region     = opt.detector_region # "Barrel_0","Barrel_1","Barrel_2","Barrel_3","Endcap_0","Endcap_1","Endcap_2","Endcap_3","Endcap_4","Endcap_5","Endcap_6","Endcap_7"
collidingFile       = opt.collidingFile
outJson_path        = opt.outJson_path
noisyStripsFile     = opt.noisyStripsFile


if fill_number in fillsDict:
    file_folders = fillsDict[fill_number].file_folders
    totalLumi    = sum([fillsDict[fill_number].totalLumi[run] if run in fillsDict[fill_number].runs else 0 for run in runs_list])
else:
    print("Missing file list for this fill number")
    sys.exit(1)





enable_MT           = True
dt                  = 25e-9 # 25ns
bxIds               = list(range(3564))
rpc_bx_windowFile   = "/afs/cern.ch/user/" + inituser + "/" + username + "/rpc-offline-analysis/analyzer/utils/rpc_bx_window.txt"
GeometryFile_path   = "/afs/cern.ch/user/" + inituser + "/" + username + "/rpc-offline-analysis/analyzer/utils/RPCGeometry.out"
file_list           = [f"{folder}{file}" for folder in file_folders for file in os.listdir(folder) if ".root" in file]
# Multi-Threading #
if enable_MT:
    ROOT.EnableImplicitMT()
else:
    ROOT.DisableImplicitMT()

# THIS FILE IS NOT FILLED PROPERLY #
file_to_remove    = "/eos/cms/store/group/upgrade/GEM/NanoAOD/ZeroBias/crab_ZeroBias_Run3_Fill9606_Run380466To380470_NanoAOD_v4/250207_160241/0000/nano_mu_bkg_RAW2DIGI_NANO_575.root"
if file_to_remove in file_list:
    file_list.remove(file_to_remove)

    
df          = ROOT.RDataFrame("Events", file_list)
print(f"Example file:    {file_list[0]}")
print(f"Number of files: {len(file_list)}")
print(f"Fill number:     {fill_number}")
print(f"Runs:            {runs_list}")
print(f"Detector region: {detector_region}")
print(f"Colliding file:  {collidingFile}")
print(f"Output json:     {outJson_path}")



#### LOAD utils/funcs.h ####
text_file = open("/afs/cern.ch/user/" + inituser + "/" + username + "/rpc-offline-analysis/analyzer/utils/funcs.h", "r")
data      = text_file.read()
def my_initialization_function():
    print(ROOT.gInterpreter.ProcessLine(".O"))
    ROOT.gInterpreter.Declare('{}'.format(data))
    print("end of initialization")
my_initialization_function()


################################################################################
############ Get the list of ROLLS for the selected detector region ############
################################################################################
df_geometry = openGeomFile(GeometryFile_path) # Barrel = 1020, Endcap = 2088
Barrel_0 = df_geometry[df_geometry["rpc_name"].str.startswith("W")]["RPC_Id"].unique().tolist()[0:102]
Barrel_1 = df_geometry[df_geometry["rpc_name"].str.startswith("W")]["RPC_Id"].unique().tolist()[102:204]
Barrel_2 = df_geometry[df_geometry["rpc_name"].str.startswith("W")]["RPC_Id"].unique().tolist()[204:306]
Barrel_3 = df_geometry[df_geometry["rpc_name"].str.startswith("W")]["RPC_Id"].unique().tolist()[306:408]
Barrel_4 = df_geometry[df_geometry["rpc_name"].str.startswith("W")]["RPC_Id"].unique().tolist()[408:510]
Barrel_5 = df_geometry[df_geometry["rpc_name"].str.startswith("W")]["RPC_Id"].unique().tolist()[510:612]
Barrel_6 = df_geometry[df_geometry["rpc_name"].str.startswith("W")]["RPC_Id"].unique().tolist()[612:714]
Barrel_7 = df_geometry[df_geometry["rpc_name"].str.startswith("W")]["RPC_Id"].unique().tolist()[714:816]
Barrel_8 = df_geometry[df_geometry["rpc_name"].str.startswith("W")]["RPC_Id"].unique().tolist()[816:918]
Barrel_9 = df_geometry[df_geometry["rpc_name"].str.startswith("W")]["RPC_Id"].unique().tolist()[918:1020]

Endcap_0  = df_geometry[df_geometry["rpc_name"].str.startswith("RE")]["RPC_Id"].unique().tolist()[0:87]
Endcap_1  = df_geometry[df_geometry["rpc_name"].str.startswith("RE")]["RPC_Id"].unique().tolist()[87:174]
Endcap_2  = df_geometry[df_geometry["rpc_name"].str.startswith("RE")]["RPC_Id"].unique().tolist()[174:261]
Endcap_3  = df_geometry[df_geometry["rpc_name"].str.startswith("RE")]["RPC_Id"].unique().tolist()[261:348]
Endcap_4  = df_geometry[df_geometry["rpc_name"].str.startswith("RE")]["RPC_Id"].unique().tolist()[348:435]
Endcap_5  = df_geometry[df_geometry["rpc_name"].str.startswith("RE")]["RPC_Id"].unique().tolist()[435:522]
Endcap_6  = df_geometry[df_geometry["rpc_name"].str.startswith("RE")]["RPC_Id"].unique().tolist()[522:609]
Endcap_7  = df_geometry[df_geometry["rpc_name"].str.startswith("RE")]["RPC_Id"].unique().tolist()[609:696]
Endcap_8  = df_geometry[df_geometry["rpc_name"].str.startswith("RE")]["RPC_Id"].unique().tolist()[696:783]
Endcap_9  = df_geometry[df_geometry["rpc_name"].str.startswith("RE")]["RPC_Id"].unique().tolist()[783:870]
Endcap_10 = df_geometry[df_geometry["rpc_name"].str.startswith("RE")]["RPC_Id"].unique().tolist()[870:957]
Endcap_11 = df_geometry[df_geometry["rpc_name"].str.startswith("RE")]["RPC_Id"].unique().tolist()[957:1044]
Endcap_12 = df_geometry[df_geometry["rpc_name"].str.startswith("RE")]["RPC_Id"].unique().tolist()[1044:1131]
Endcap_13 = df_geometry[df_geometry["rpc_name"].str.startswith("RE")]["RPC_Id"].unique().tolist()[1131:1218]
Endcap_14 = df_geometry[df_geometry["rpc_name"].str.startswith("RE")]["RPC_Id"].unique().tolist()[1218:1305]
Endcap_15 = df_geometry[df_geometry["rpc_name"].str.startswith("RE")]["RPC_Id"].unique().tolist()[1305:1392]
Endcap_16 = df_geometry[df_geometry["rpc_name"].str.startswith("RE")]["RPC_Id"].unique().tolist()[1392:1479]
Endcap_17 = df_geometry[df_geometry["rpc_name"].str.startswith("RE")]["RPC_Id"].unique().tolist()[1479:1566]
Endcap_18 = df_geometry[df_geometry["rpc_name"].str.startswith("RE")]["RPC_Id"].unique().tolist()[1566:1653]
Endcap_19 = df_geometry[df_geometry["rpc_name"].str.startswith("RE")]["RPC_Id"].unique().tolist()[1653:1740]
Endcap_20 = df_geometry[df_geometry["rpc_name"].str.startswith("RE")]["RPC_Id"].unique().tolist()[1740:1827]
Endcap_21 = df_geometry[df_geometry["rpc_name"].str.startswith("RE")]["RPC_Id"].unique().tolist()[1827:1914]
Endcap_22 = df_geometry[df_geometry["rpc_name"].str.startswith("RE")]["RPC_Id"].unique().tolist()[1914:2001]
Endcap_23 = df_geometry[df_geometry["rpc_name"].str.startswith("RE")]["RPC_Id"].unique().tolist()[2001:2088]

rawId_dict = {
    "Barrel_0": Barrel_0,
    "Barrel_1": Barrel_1,
    "Barrel_2": Barrel_2,
    "Barrel_3": Barrel_3,
    "Barrel_4": Barrel_4,
    "Barrel_5": Barrel_5,
    "Barrel_6": Barrel_6,
    "Barrel_7": Barrel_7,
    "Barrel_8": Barrel_8,
    "Barrel_9": Barrel_9,
    "Endcap_0": Endcap_0,
    
    "Endcap_1": Endcap_1,
    "Endcap_2": Endcap_2,
    "Endcap_3": Endcap_3,
    "Endcap_4": Endcap_4,
    "Endcap_5": Endcap_5,
    "Endcap_6": Endcap_6,
    "Endcap_7": Endcap_7,
    "Endcap_8": Endcap_8,
    "Endcap_9": Endcap_9,
    "Endcap_10": Endcap_10,
    "Endcap_11": Endcap_11,
    "Endcap_12": Endcap_12,
    "Endcap_13": Endcap_13,
    "Endcap_14": Endcap_14,
    "Endcap_15": Endcap_15,
    "Endcap_16": Endcap_16,
    "Endcap_17": Endcap_17,
    "Endcap_18": Endcap_18,
    "Endcap_19": Endcap_19,
    "Endcap_20": Endcap_20,
    "Endcap_21": Endcap_21,
    "Endcap_22": Endcap_22,
    "Endcap_23": Endcap_23
}

rawId_list = rawId_dict[detector_region]
# rawId_list = [637633405]
print(f"Number of ROLLS that will be analyzed: {len(rawId_list)}")


### Load colliding bunch-crossings for the specific fill_number ###
with open(collidingFile, "r") as f:
    collidingBunches   = [int(x) for x in f.read().split("\n") if x]
collidingBunches_rvec  = ROOT.RVec("int")(collidingBunches)
print(f"Number of Colliding bunch crossings in fill {fill_number} is {collidingBunches_rvec.size()}")


### Load noisy strips per each rawId ###
if noisyStripsFile is not None:
    noisy_strips                = {}
    with open(noisyStripsFile, "r") as f:
        for line in f:
            rawId, strips       = list(map(int, line.strip().split(",")))[0], list(map(int, line.strip().split(",")))[1:]
            noisy_strips[rawId] = strips
else:
    noisy_strips                = None

### Load bx-window width per each rawId ###
rpc_bx_windows                 = {}
with open(rpc_bx_windowFile, "r") as f:
    for line in f:
        rawId, bx_window_width = map(int, line.strip().split(","))
        rpc_bx_windows[rawId]  = bx_window_width


################################################
######### Functions used by RDataFrame #########
################################################
def add_occurrancies_rawId(df, rawId, noisy_strips):
    if (noisy_strips is not None) and (rawId in noisy_strips.keys()):
        noisy_strips_list = noisy_strips[rawId]
    else:
        noisy_strips_list = []
    noisy_strips_rvec = ROOT.RVec("int")(noisy_strips_list)
    df_out = df.Define("ids_rpcRecHit_rawId",            f"ids_rpcRecHit_rawId(rpcRecHit_rawId, {rawId})")\
               .Define("rpcRechHit_isNoisy",             f"rpcRechHit_isNoisy(ids_rpcRecHit_rawId, rpcRecHit_firstClusterStrip, rpcRecHit_clusterSize, {noisy_strips_rvec})")\
               .Define("n_rpcRecHit_rawId",              f"n_rpcRecHit_rawId(ids_rpcRecHit_rawId, rpcRechHit_isNoisy)")\
               .Define("bx_rawId",                       f"bx_rawId(rpcRecHit_rawId, rpcRecHit_bx, {rawId})")\
               .Define("n_rpcRecHit_rawId_Colliding",    f"n_rpcRecHit_rawId_SchemeRegion(ids_rpcRecHit_rawId, rpcRechHit_isNoisy, rpcRecHit_SchemeRegion, 1)")\
               .Define("n_rpcRecHit_rawId_NonColliding", f"n_rpcRecHit_rawId_SchemeRegion(ids_rpcRecHit_rawId, rpcRechHit_isNoisy, rpcRecHit_SchemeRegion, 2)")\
               .Define("n_rpcRecHit_rawId_PreBeam",      f"n_rpcRecHit_rawId_SchemeRegion(ids_rpcRecHit_rawId, rpcRechHit_isNoisy, rpcRecHit_SchemeRegion, 3)")\
               .Define("n_rpcRecHit_rawId_BeamAbort",    f"n_rpcRecHit_rawId_SchemeRegion(ids_rpcRecHit_rawId, rpcRechHit_isNoisy, rpcRecHit_SchemeRegion, 4)")
            #    .Define("n_rpcRecHit_rawId_Colliding",    f"n_rpcRecHit_rawId_SchemeRegion(rpcRecHit_rawId, {rawId}, rpcRecHit_SchemeRegion, 1)")\
            #    .Define("n_rpcRecHit_rawId_NonColliding", f"n_rpcRecHit_rawId_SchemeRegion(rpcRecHit_rawId, {rawId}, rpcRecHit_SchemeRegion, 2)")\
            #    .Define("n_rpcRecHit_rawId_PreBeam",      f"n_rpcRecHit_rawId_SchemeRegion(rpcRecHit_rawId, {rawId}, rpcRecHit_SchemeRegion, 3)")\
            #    .Define("n_rpcRecHit_rawId_BeamAbort",    f"n_rpcRecHit_rawId_SchemeRegion(rpcRecHit_rawId, {rawId}, rpcRecHit_SchemeRegion, 4)")
    return df_out


def select_runs(df, runs_list):
    df_out = df.Filter(" || ".join(f"run == {run}" for run in runs_list),       "select run number")\
               .Define("rpcRecHit_bxReal",                                      "rpcRecHit_bxReal(bunchCrossing, rpcRecHit_bx)")\
               .Define("rpcRecHit_SchemeRegion",                                f"rpcRecHit_SchemeRegion(rpcRecHit_bxReal, {collidingBunches_rvec})")\
               .Define("nEvents_5bx_Colliding",                                 f"nEvents_SchemeRegion(bunchCrossing, 5, {collidingBunches_rvec}, 1)")\
               .Define("nEvents_5bx_NonColliding",                              f"nEvents_SchemeRegion(bunchCrossing, 5, {collidingBunches_rvec}, 2)")\
               .Define("nEvents_5bx_PreBeam",                                   f"nEvents_SchemeRegion(bunchCrossing, 5, {collidingBunches_rvec}, 3)")\
               .Define("nEvents_5bx_BeamAbort",                                 f"nEvents_SchemeRegion(bunchCrossing, 5, {collidingBunches_rvec}, 4)")\
               .Define("nEvents_8bx_Colliding",                                 f"nEvents_SchemeRegion(bunchCrossing, 8, {collidingBunches_rvec}, 1)")\
               .Define("nEvents_8bx_NonColliding",                              f"nEvents_SchemeRegion(bunchCrossing, 8, {collidingBunches_rvec}, 2)")\
               .Define("nEvents_8bx_PreBeam",                                   f"nEvents_SchemeRegion(bunchCrossing, 8, {collidingBunches_rvec}, 3)")\
               .Define("nEvents_8bx_BeamAbort",                                 f"nEvents_SchemeRegion(bunchCrossing, 8, {collidingBunches_rvec}, 4)")
    return df_out
    
    
def select_lumi_interval(df, lumi_min, lumi_max):
    df_out = df.Filter(f"lumi_instLumi >= {lumi_min} & lumi_instLumi < {lumi_max}", "select lumi interval")
    return df_out


def effective_area(rawId, noisy_strips):
    n_strips                   = df_geometry[df_geometry["RPC_Id"]==rawId]["nStrips"].values[0]     # total number of strips
    if (noisy_strips is not None) and (rawId in noisy_strips.keys()):
        noisy_strips_list      = noisy_strips[rawId]
    else:
        noisy_strips_list      = []
    n_NS                       = len(noisy_strips_list)                                             # number of noisy strips
    eps_good_strips            = 1 - n_NS/n_strips                                                  # percentage of good strips
    strip_area                 = df_geometry[df_geometry["RPC_Id"]==rawId]["stripArea"].values[0]   # area of a single strip
    area_eff                   = strip_area * n_strips * eps_good_strips                            # effective area of the roll after noisy strips removal
    return area_eff







###############################################
############### FILL PROCESSING ###############
###############################################
t0 = time.time()

##### ACTIONS BOOKING #####
df_run                  = select_runs(df=df,runs_list=runs_list)
lumi_bins               = [[i, i + 1000] for i in range(0, 25000, 1000)]

# Define outJson structure - will contain the info on nEvents, nRecHits, effective area #
outJson                = {}
outJson["nEvents"]     = {}
outJson["nEvents_5bx"] = {}
outJson["nEvents_8bx"] = {}
outJson["nRecHits"]    = {}
outJson["Aeff"]        = {}


outJson["nEvents"]["Total"]             = []
outJson["nEvents_5bx"]["Colliding"]     = []
outJson["nEvents_5bx"]["NonColliding"]  = []
outJson["nEvents_5bx"]["PreBeam"]       = []
outJson["nEvents_5bx"]["BeamAbort"]     = []
outJson["nEvents_8bx"]["Colliding"]     = []
outJson["nEvents_8bx"]["NonColliding"]  = []
outJson["nEvents_8bx"]["PreBeam"]       = []
outJson["nEvents_8bx"]["BeamAbort"]     = []

outJson["nRecHits"]["Total"]            = {}
outJson["nRecHits"]["Colliding"]        = {}
outJson["nRecHits"]["NonColliding"]     = {}
outJson["nRecHits"]["PreBeam"]          = {}
outJson["nRecHits"]["BeamAbort"]        = {}

for rawId in rawId_list:
    outJson["Aeff"][rawId]                     = effective_area(rawId=rawId, noisy_strips=noisy_strips)
    
    outJson["nRecHits"]["Total"][rawId]        = []
    outJson["nRecHits"]["Colliding"][rawId]    = []
    outJson["nRecHits"]["NonColliding"][rawId] = []
    outJson["nRecHits"]["PreBeam"][rawId]      = []
    outJson["nRecHits"]["BeamAbort"][rawId]    = []

snapshot = {}
for lumi_min,lumi_max in lumi_bins:
    df_run_lumi                                = select_lumi_interval(df=df_run,lumi_min=lumi_min,lumi_max=lumi_max)
    # nEvents - Total #
    n_events_run_lumi                          = df_run_lumi.Count()
    outJson["nEvents"]["Total"].append(n_events_run_lumi)

    # nEvents - 5bx width chambers - Regions (no division in bx) #
    n_events_run_lumi_5bx_Colliding    = df_run_lumi.Sum("nEvents_5bx_Colliding")
    n_events_run_lumi_5bx_NonColliding = df_run_lumi.Sum("nEvents_5bx_NonColliding")
    n_events_run_lumi_5bx_PreBeam      = df_run_lumi.Sum("nEvents_5bx_PreBeam")
    n_events_run_lumi_5bx_BeamAbort    = df_run_lumi.Sum("nEvents_5bx_BeamAbort")
    outJson["nEvents_5bx"]["Colliding"].append(n_events_run_lumi_5bx_Colliding)
    outJson["nEvents_5bx"]["NonColliding"].append(n_events_run_lumi_5bx_NonColliding)
    outJson["nEvents_5bx"]["PreBeam"].append(n_events_run_lumi_5bx_PreBeam)
    outJson["nEvents_5bx"]["BeamAbort"].append(n_events_run_lumi_5bx_BeamAbort)
    
    # nEvents - 8bx width chambers - Regions (no division in bx) #
    n_events_run_lumi_8bx_Colliding    = df_run_lumi.Sum("nEvents_8bx_Colliding")
    n_events_run_lumi_8bx_NonColliding = df_run_lumi.Sum("nEvents_8bx_NonColliding")
    n_events_run_lumi_8bx_PreBeam      = df_run_lumi.Sum("nEvents_8bx_PreBeam")
    n_events_run_lumi_8bx_BeamAbort    = df_run_lumi.Sum("nEvents_8bx_BeamAbort")
    outJson["nEvents_8bx"]["Colliding"].append(n_events_run_lumi_8bx_Colliding)
    outJson["nEvents_8bx"]["NonColliding"].append(n_events_run_lumi_8bx_NonColliding)
    outJson["nEvents_8bx"]["PreBeam"].append(n_events_run_lumi_8bx_PreBeam)
    outJson["nEvents_8bx"]["BeamAbort"].append(n_events_run_lumi_8bx_BeamAbort)


    for rawId in rawId_list:
        df_run_lumi_rawId                       = add_occurrancies_rawId(df=df_run_lumi, rawId=rawId, noisy_strips=noisy_strips)
        
        # df_run_lumi_rawId.Display(["event","rpcRecHit_rawId","ids_rpcRecHit_rawId","rpcRechHit_isNoisy","n_rpcRecHit_rawId","rpcRecHit_firstClusterStrip","rpcRecHit_clusterSize"], 12).Print()
        # df_run_lumi_rawId.Display(["event","nEvents_Colliding","nEvents_NonColliding","nEvents_PreBeam","nEvents_BeamAbort"]).Print()
        # df_run_lumi_rawId.Display(["bunchCrossing","nEvents_Colliding","nEvents_NonColliding","nEvents_PreBeam","nEvents_BeamAbort"]).Print()
        
        # nRecHits - Inlcusive + Regions (no division in bx) #
        n_rpcRecHit_run_rawId_lumi              = df_run_lumi_rawId.Sum("n_rpcRecHit_rawId")
        n_rpcRecHit_run_rawId_lumi_Colliding    = df_run_lumi_rawId.Sum("n_rpcRecHit_rawId_Colliding")
        n_rpcRecHit_run_rawId_lumi_NonColliding = df_run_lumi_rawId.Sum("n_rpcRecHit_rawId_NonColliding")
        n_rpcRecHit_run_rawId_lumi_PreBeam      = df_run_lumi_rawId.Sum("n_rpcRecHit_rawId_PreBeam")
        n_rpcRecHit_run_rawId_lumi_BeamAbort    = df_run_lumi_rawId.Sum("n_rpcRecHit_rawId_BeamAbort")
        
        outJson["nRecHits"]["Total"][rawId].append(n_rpcRecHit_run_rawId_lumi)
        outJson["nRecHits"]["Colliding"][rawId].append(n_rpcRecHit_run_rawId_lumi_Colliding)
        outJson["nRecHits"]["NonColliding"][rawId].append(n_rpcRecHit_run_rawId_lumi_NonColliding)
        outJson["nRecHits"]["PreBeam"][rawId].append(n_rpcRecHit_run_rawId_lumi_PreBeam)
        outJson["nRecHits"]["BeamAbort"][rawId].append(n_rpcRecHit_run_rawId_lumi_BeamAbort)  

        # opts = ROOT.RDF.RSnapshotOptions()
        # opts.fLazy = True
        # snapshot[f"{rawId}_{lumi_min}"] = df_run_lumi_rawId.Snapshot("Events", f"trials_noNoisyFile/output_{rawId}_{lumi_min}.root", ["event","lumi_instLumi","ids_rpcRecHit_rawId","rpcRechHit_isNoisy","n_rpcRecHit_rawId","rpcRecHit_firstClusterStrip","rpcRecHit_clusterSize"])
        

tf = time.time()
print(f"Total time elapsed for BOOKING ACTIONS:     {tf-t0} seconds")


##### ACTIONS TRIGGERING #####
t0 = time.time()
for i in range(len(lumi_bins)):
    outJson["nEvents"]["Total"][i]            = outJson["nEvents"]["Total"][i].GetValue()
    outJson["nEvents_5bx"]["Colliding"][i]    = outJson["nEvents_5bx"]["Colliding"][i].GetValue()
    outJson["nEvents_5bx"]["NonColliding"][i] = outJson["nEvents_5bx"]["NonColliding"][i].GetValue()
    outJson["nEvents_5bx"]["PreBeam"][i]      = outJson["nEvents_5bx"]["PreBeam"][i].GetValue()
    outJson["nEvents_5bx"]["BeamAbort"][i]    = outJson["nEvents_5bx"]["BeamAbort"][i].GetValue()
    outJson["nEvents_8bx"]["Colliding"][i]    = outJson["nEvents_8bx"]["Colliding"][i].GetValue()
    outJson["nEvents_8bx"]["NonColliding"][i] = outJson["nEvents_8bx"]["NonColliding"][i].GetValue()
    outJson["nEvents_8bx"]["PreBeam"][i]      = outJson["nEvents_8bx"]["PreBeam"][i].GetValue()
    outJson["nEvents_8bx"]["BeamAbort"][i]    = outJson["nEvents_8bx"]["BeamAbort"][i].GetValue()
    
    
    for rawId in rawId_list:
        outJson["nRecHits"]["Total"][rawId][i]        = outJson["nRecHits"]["Total"][rawId][i].GetValue()
        outJson["nRecHits"]["Colliding"][rawId][i]    = outJson["nRecHits"]["Colliding"][rawId][i].GetValue()
        outJson["nRecHits"]["NonColliding"][rawId][i] = outJson["nRecHits"]["NonColliding"][rawId][i].GetValue()
        outJson["nRecHits"]["PreBeam"][rawId][i]      = outJson["nRecHits"]["PreBeam"][rawId][i].GetValue()
        outJson["nRecHits"]["BeamAbort"][rawId][i]    = outJson["nRecHits"]["BeamAbort"][rawId][i].GetValue()

        # snapshot[f"{rawId}_{lumi_min}"].GetValue()

tf = time.time()
print(f"Total time elapsed for TRIGGERING ACTIONS:  {tf-t0} seconds")


#### Save outJson to file ####
with open(outJson_path, "w") as f:
    json.dump(outJson, f, indent=4)