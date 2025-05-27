import ROOT
import os
import sys
sys.path.append('../')
import numpy as np
import pandas as pd
import json
from math import sqrt
from analyzer.utils.openGeomFile import openGeomFile
from analyzer.utils.fillsInfo import *
from rates_tools import calculateRates_regions, calculateRates_backgrounds
import array
import optparse
from getUser import inituser, username, uid, workdir
from select_rawIds_in_chamber import select_rawIds_in_chamber

############################
######### SETTINGS #########
############################
usage               = "python3 calculator.py -f <fill_number> -r <runs_list> -c <chamber>"
parser              = optparse.OptionParser(usage)
parser.add_option("-f", "--fill",       dest="fill",    type=int,                           help="Fill number")
parser.add_option("-r", "--runs",       dest="runs",    type=str,                           help="Runs")
parser.add_option("-c", "--chamber",    dest="chamber", type=str,                           help="Chamber tag (check 'rpc_name' from '/analyzer/utils/RPCGeometry.out', can also be a wide region). Example: 'RE+4_R3_CH13_C', 'RE+4_R3_CH13' or 'RE+4_R3'")
(opt, args)         = parser.parse_args()
fill_number         = opt.fill
runs_list           = list(map(int, opt.runs.split(",")))
chamber             = opt.chamber



dt                  = 25e-9 # 25ns
rpc_bx_windowFile   = "/afs/cern.ch/" + workdir + "/" + inituser + "/" + username + "/rpc-offline-analysis/analyzer/utils/rpc_bx_window.txt"
GeometryFile_path   = "/afs/cern.ch/" + workdir + "/" + inituser + "/" + username + "/rpc-offline-analysis/analyzer/utils/RPCGeometry.out"
collidingFile       = "/afs/cern.ch/" + workdir + "/" + inituser + "/" + username + f"/rpc-offline-analysis/analyzer/utils/lhc_schemes/Fill_{fill_number}/colliding_{fill_number}.txt"
regions             = ["Total", "Colliding", "NonColliding", "PreBeam", "BeamAbort"]
backgrounds         = ["Inclusive", "Delayed", "Prompt"]

inJson_path         = f"/eos/user/l/lfavilla/rpc-offline-analysis/common-tuples-results/{fill_number}/{'_'.join((map(str, runs_list)))}/partial_results_{fill_number}_{'_'.join(map(str, runs_list))}_withNoisyStripsCleaning.json"
outJson_path        = f"/eos/user/l/lfavilla/rpc-offline-analysis/common-tuples-results/{fill_number}/{'_'.join((map(str, runs_list)))}/final_results_{fill_number}_{'_'.join(map(str, runs_list))}_withNoisyStripsCleaning.json"


if fill_number in fillsDict:
    totalLumi    = sum([fillsDict[fill_number].totalLumi[run] if run in fillsDict[fill_number].runs else 0 for run in runs_list])
else:
    print("Missing file list for this fill number")
    sys.exit(1)




### Load bx-window width per each rawId ###
rpc_bx_windows                 = {}
with open(rpc_bx_windowFile, "r") as f:
    for line in f:
        rawId, bx_window_width = map(str, line.strip().split(","))
        rpc_bx_windows[rawId]  = int(bx_window_width)


### Load partial results for the specific run ###
with open(inJson_path, "r") as f:
    print(f"Loading partial results from: {inJson_path}")
    inJson = json.load(f)


### Load Geometry File ###
df_geometry = openGeomFile(GeometryFile_path)


#########################
### RATES CALCULATION ###
#########################
lumi_bins   = [[i, i + 1000] for i in range(0, 25000, 1000)]
rawIds      = select_rawIds_in_chamber(df_geometry, chamber)



print(f"Calculating Hitrate for chamber {chamber} --> # of rawIds {type(rawIds[0])}: {len(rawIds)}")
# print(rawIds)


histRatesRegions,ratesRegions,fitsRegions,fitResultsRegions              = calculateRates_regions(
                                                                                        partial_results_inJson=inJson,
                                                                                        rawIds=rawIds,
                                                                                        regions=regions,
                                                                                        bx_window_width=rpc_bx_windows[rawIds[0]],
                                                                                        lumi_bins=lumi_bins,
                                                                                    )

if all(fitsRegions[reg] is not None for reg in fitsRegions):
    ratesBackgrounds,ratesBackgrounds_parameters                         = calculateRates_backgrounds(
                                                                                        fitRatesRegions=fitsRegions,
                                                                                        fitResultsRegions=fitResultsRegions,
                                                                                        colliding_scheme_txt=collidingFile,
                                                                                    )
    ratesBackgrounds_band                               = {}
    for bkg in backgrounds:
        # ERROR BANDS for backgrounds #
        XCenters                                        = range(9000, 22000, 1000)
        YCenters                                        = [ratesBackgrounds[bkg].Eval(x) for x in XCenters]
        XErrors                                         = [0 for x in XCenters]
        YErrors                                         = [sqrt(abs((x**2)*ratesBackgrounds_parameters[bkg]["p1_error"]**2 + ratesBackgrounds_parameters[bkg]["p0_error"]**2 + 2*x*ratesBackgrounds_parameters[bkg]["cov_p0p1"])) for x in XCenters]
        
        ratesBackgrounds_band[bkg]                      = ROOT.TGraphErrors(len(XCenters), array.array("f", XCenters), array.array("f", YCenters), array.array("f", XErrors), array.array("f", YErrors))
else:
    ratesBackgrounds, ratesBackgrounds_parameters       = {bkg: None for bkg in backgrounds}, {bkg: None for bkg in backgrounds}




#######################################
######### SAVE OUTPUT TO JSON #########
#######################################
### Check if output file already exists, if so, just update the rates for that chamber ###
if os.path.exists(outJson_path):
    print(f"Output file already exists:                 {outJson_path}")
    with open(outJson_path, "r") as f:
        outJson = json.load(f)
else:
    print(f"Output file does not exist, creating it:    {outJson_path}")
    outJson = {chamber: {}}

if chamber in outJson:
    print(f"Updating rates for chamber:                 {chamber}")
else:
    print(f"Adding rates for chamber:                   {chamber}")
outJson[chamber] = {
                        "rates":        ratesRegions,
                        "parameters":   fitResultsRegions | ratesBackgrounds_parameters,
                    }
print(outJson[chamber])

with open(outJson_path, "w") as f:
    json.dump(outJson, f, indent=4)