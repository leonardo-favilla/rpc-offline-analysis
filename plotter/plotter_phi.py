import ROOT
import os
import sys
sys.path.append('../')
import numpy as np
import pandas as pd
import cmsstyle as CMS # https://cmsstyle.readthedocs.io/en/latest/reference/ , https://cms-analysis.docs.cern.ch/guidelines/plotting/general/
import json
from math import sqrt
from plotting_functions import makeCanvas
from analyzer.utils.openGeomFile import openGeomFile
from analyzer.utils.fillsInfo import *
ROOT.gROOT.SetBatch(True)
from getUser import inituser, username, uid, workdir
import array
import optparse
from statistics import mean, stdev
from select_rawIds_in_chamber import select_rawIds_in_chamber

############################
######### SETTINGS #########
############################
usage                   = "python3 plotter_eta.py -f <fill_number> -r <runs_list> --station <station> --disk <disk>"
parser                  = optparse.OptionParser(usage)
parser.add_option("-f", "--fill",       dest="fill",    type=int,                                                   help="Fill number")
parser.add_option("-r", "--runs",       dest="runs",    type=str,                                                   help="Runs")
parser.add_option(      "--station",    dest="station", type=str,                           default=None,           help="Station name - RB1in, RB1out, RB2in, RB2out, RB, RB4 (optional)")
parser.add_option(      "--disk",       dest="disk",    type=str,                           default=None,           help="Disk name - RE1, RE2, RE3, RE4 (optional)")
parser.add_option(      "--cleaning",   dest="cleaning",            action="store_true",    default=False,          help="Apply noisy strips cleaning (default: False)")
(opt, args)             = parser.parse_args()
if opt.station and opt.disk:
    parser.error("Options --station and --disk cannot be given at the same time. Please choose one of them.")
    sys.exit(1)
fill_number             = opt.fill
runs_list               = list(map(int, opt.runs.split(",")))
station                 = opt.station
disk                    = opt.disk
cleaning                = opt.cleaning

if cleaning:
    cleaning_suffix     = "_withNoisyStripsCleaning"
else:
    cleaning_suffix     = "_noNoisyStripsCleaning"
if station:
    sectors             = [f"S{str(i).zfill(2)}" for i in range(1,13)]
    chambers            = [
                            f"W-2_{station}",
                            f"W-1_{station}",
                            f"W+0_{station}",
                            f"W+1_{station}",
                            f"W+2_{station}"
                            ]
    sector_phi_width    = 30
elif disk:
    disk_number         = int(disk[-1])
    sectors             = [f"CH{str(i).zfill(2)}" for i in range(1,37)]
    chambers            = [
                            f"RE-{disk_number}_R2",
                            f"RE-{disk_number}_R3",
                            f"RE+{disk_number}_R3", 
                            f"RE+{disk_number}_R2",
                          ]
    sector_phi_width    = 10

inst_lumi               = 10000 # we are going to fix the Inst.Lumi to: <inst_lumi> x 1e30cm^-2s^-1
GeometryFile_path       = "/afs/cern.ch/" + workdir + "/" + inituser + "/" + username + "/rpc-offline-analysis/analyzer/utils/RPCGeometry.out"
inJson_path             = f"/eos/user/l/lfavilla/rpc-offline-analysis/common-tuples-results/{fill_number}/{'_'.join((map(str, runs_list)))}/final_results_{fill_number}_{'_'.join(map(str, runs_list))}{cleaning_suffix}.json"
outFolder_path          = f"/eos/user/l/lfavilla/www/rpc-offline-analysis/common-tuples-results/{fill_number}_{'_'.join(map(str, runs_list))}{cleaning_suffix}/"
plots_path              = outFolder_path + "plots/"
regions                 = ["Total", "Colliding", "NonColliding", "PreBeam", "BeamAbort"]
backgrounds             = [
                            "Inclusive",
                            "Delayed",
                            "Prompt"
                            ]

yMin                    = 0 # TO FIX
yMax                    = 10 # TO FIX

if fill_number in fillsDict:
    totalLumi    = sum([fillsDict[fill_number].totalLumi[run] if run in fillsDict[fill_number].runs else 0 for run in runs_list])
else:
    print("Missing file list for this fill number")
    sys.exit(1)

### Load Geometry File ###
df_geometry             = openGeomFile(GeometryFile_path)
with open(inJson_path, "r") as f:
    inJson              = json.load(f)





if not os.path.exists(outFolder_path):
    os.makedirs(outFolder_path)
if not os.path.exists(plots_path):
    os.makedirs(plots_path)

if "www" in outFolder_path:
    os.system(f"cp /eos/user/l/lfavilla/www/index.php   {outFolder_path}")
    os.system(f"cp /eos/user/l/lfavilla/www/index.php   {plots_path}")




### Load final results for the specific run ###
with open(inJson_path, "r") as f:
    print(f"Loading final results from: {inJson_path}")
    inJson = json.load(f)


### Check if the chamber is in the json file and if the rates are not None ###
for chamber in chambers:
    if chamber not in inJson:
        print(f"Chamber {chamber} NOT found in the json file.")
        sys.exit()
    elif (chamber in inJson) and any([inJson[chamber]["rates"][reg] is None for reg in regions]):
        print(f"Seems it was NOT possible to calculate rates in REGIONS for chamber {chamber}")
        sys.exit()
    elif (chamber in inJson) and any([inJson[chamber]["parameters"][bkg] is None for bkg in backgrounds]):
        print(f"Seems it was NOT possible to calculate rates in BACKGROUNDS for chamber {chamber}")
        sys.exit()
    else:
        print(f"Chamber {chamber} found in the json file with rates calculated properly")



##########################################
### Fill the histograms with the rates ###
##########################################
# BACKGROUNDS #
minX, maxX                      = 9000, 21000
funcs                           = {}
rates_phi                       = {}


for bkg in backgrounds:
    funcs[bkg]                      = {}
    rates_phi[bkg]                  = {}
    for chamber in chambers:
        phiCenters                  = []
        YCenters                    = []
        phiErrors                   = []
        YErrors                     = []

        chambers_with_sector        = [f"{chamber}_{sector}" for sector in sectors]
        for nsec,chamber_with_sector in enumerate(chambers_with_sector):
            rawIds                              = select_rawIds_in_chamber(df_geometry, chamber_with_sector)
            if inJson[chamber_with_sector]["parameters"][bkg] is None:
                funcs[bkg][chamber_with_sector] = None
                continue
            funcs[bkg][chamber_with_sector]         = ROOT.TF1("func_"+chamber_with_sector+"_"+bkg, "pol1", minX, maxX)
            funcs[bkg][chamber_with_sector].SetParameter(0, inJson[chamber_with_sector]["parameters"][bkg]["p0"])
            funcs[bkg][chamber_with_sector].SetParameter(1, inJson[chamber_with_sector]["parameters"][bkg]["p1"])
            funcs[bkg][chamber_with_sector].SetParError(0, inJson[chamber_with_sector]["parameters"][bkg]["p0_error"])
            funcs[bkg][chamber_with_sector].SetParError(1, inJson[chamber_with_sector]["parameters"][bkg]["p1_error"])


            
            # phi_value                           = df_geometry[df_geometry["RPC_Id"].apply(lambda rawId: rawId in map(int,rawIds))]["phi"].mean()
            # phi_value                          += 360 if phi_value < 0 else 0 # in GeomFile, phi is not in [0, 360] but in [0, +180] + [-180, 0]
            phi_value                           = sector_phi_width * nsec
            phiCenters.append(phi_value)
            YCenters.append(funcs[bkg][chamber_with_sector].Eval(inst_lumi))
            phiErrors.append(0)
            # YErrors.append(0)
            YErrors.append(sqrt(abs((inst_lumi**2)*inJson[chamber_with_sector]["parameters"][bkg]["p1_error"]**2 + inJson[chamber_with_sector]["parameters"][bkg]["p0_error"]**2 + 2*inst_lumi*inJson[chamber_with_sector]["parameters"][bkg]["cov_p0p1"])))


        ############################################################
        # rate calculation for each background and chamber vs. phi #
        ############################################################
        rates_phi[bkg][chamber] = ROOT.TGraphErrors(len(phiCenters), array.array("f", phiCenters), array.array("f", YCenters), array.array("f", phiErrors), array.array("f", YErrors))



### GRAPHIC OPTIONS ###
iPos   = 0                          # position of CMS label, 0 if out-of-frame, 11 if in-frame
lumi   = round(totalLumi*1e-3, 3)   # fb-1
energy = 13.6                       # TeV



###################################################################
##### PLOTTING RATES ALL BACKGROUNDS vs. phi - Single Chamber #####
###################################################################
for bkg in backgrounds:
    if station:
        canvName        = f"rates_{fill_number}_{'_'.join((map(str, runs_list)))}_station_{station}_{bkg}VsPhi"
        colors          = [ROOT.kRed, ROOT.kBlue, ROOT.kGreen, ROOT.kBlue, ROOT.kRed]
        markers         = [ROOT.kOpenSquare, ROOT.kOpenCircle, ROOT.kFullDiamond, ROOT.kFullCircle, ROOT.kFullSquare]
        styles          = [ROOT.kDashed, ROOT.kDashed, ROOT.kSolid, ROOT.kSolid, ROOT.kSolid]
    elif disk:
        canvName        = f"rates_{fill_number}_{'_'.join((map(str, runs_list)))}_disk_{disk}_{bkg}VsPhi"
        colors          = [ROOT.kRed, ROOT.kBlue, ROOT.kBlue, ROOT.kRed]
        markers         = [ROOT.kOpenSquare, ROOT.kOpenCircle, ROOT.kFullCircle, ROOT.kFullSquare]
        styles          = [ROOT.kDashed, ROOT.kDashed, ROOT.kSolid, ROOT.kSolid]
    path_png            = f"{plots_path}{canvName}.png"
    path_pdf            = f"{plots_path}{canvName}.pdf"
    path_C              = f"{plots_path}{canvName}.C"
    canv   = makeCanvas(h=rates_phi[bkg][chambers[0]],
                        xMin=-30,
                        xMax=360,
                        yMin=yMin,
                        yMax=yMax,
                        xTitle="#phi",
                        yTitle="Hit Rate (Hz/cm^{2})",
                        canvName=canvName,
                        square=CMS.kRectangular,
                        extraText="Private Work",
                        iPos=iPos,
                        energy=energy,
                        lumi=lumi,
                        addInfo="",
                        extraSpace=0.0,
                        labelSize=0.045,
                        titleSize=0.045,
                        labelOffset=0.003,
                        titleOffset=0.9,
                        with_z_axis=False,
                        logy=False,
                        grid=False,
                        MaxDigitsX=3,
                        MaxDigitsY=3,
                        )


    latex = ROOT.TLatex()
    latex.SetTextFont(52)
    latex.SetTextSize(0.03)
    # latex.SetTextAlign(22)
    latex.DrawLatexNDC(0.75, 0.87, f"fill:      {fill_number}") # x, y, text
    latex.DrawLatexNDC(0.75, 0.82, f"runs:      {'-'.join(map(str, runs_list))}") # x, y, text
    if station:
        latex.DrawLatexNDC(0.75, 0.77, f"station:   {station}")
    elif disk:
        latex.DrawLatexNDC(0.75, 0.77, f"disk:      {disk}")
    latex.DrawLatexNDC(0.75, 0.72, f"background:{bkg}")


    leg = CMS.cmsLeg(0.15, 0.75, 0.4, 0.9, textSize=0.03, textFont=52, columns=1)
    for chamber,color,marker,style in zip(rates_phi[bkg].keys(), colors, markers, styles):
        CMS.cmsDraw(rates_phi[bkg][chamber],
                    "PEL",
                    marker=marker,
                    msize=1,
                    mcolor=color,
                    lstyle=style,
                    lcolor=color,
                    lwidth=2,
                    )

        leg.AddEntry(rates_phi[bkg][chamber],chamber,"PEL")



    # leg.AddEntry("None", "", "")
    # leg.AddEntry("None", f"run:   {run}", "")
    # leg.AddEntry("None", "", "")
    # leg.AddEntry("None", f"rawId: {rawId}", "")



    CMS.SaveCanvas(canv, path_png, close=False)
    CMS.SaveCanvas(canv, path_pdf, close=False)
    CMS.SaveCanvas(canv, path_C, close=True)