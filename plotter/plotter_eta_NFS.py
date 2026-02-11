import ROOT
import os
import sys
sys.path.append('../')
import numpy as np
import pandas as pd
import cmsstyle as CMS # https://cmsstyle.readthedocs.io/en/latest/reference/ , https://cms-analysis.docs.cern.ch/guidelines/plotting/general/
import json
from math import sqrt
from plotting_functions import makeCanvas, makeDiCanvas
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
usage                   = "python3 plotter_eta_NFS.py --station <station> --disk <disk>"
parser                  = optparse.OptionParser(usage)
parser.add_option(      "--station",    dest="station", type=str,                           default=None,       help="Station name - RB1in, RB1out, RB2in, RB2out, RB, RB4 (optional)")
parser.add_option(      "--disk",       dest="disk",    type=str,                           default=None,       help="Disk name - RE1, RE2, RE3, RE4 (optional)")
parser.add_option(      "--cleaning",   dest="cleaning",            action="store_true",    default=False,      help="Apply noisy strips cleaning (default: False)")
(opt, args)             = parser.parse_args()
if opt.station and opt.disk:
    parser.error("Options --station and --disk cannot be given at the same time. Please choose one of them.")
    sys.exit(1)

fill_1                  = 9606
# fill_2                  = 10665
fill_2                  = 10671
runs_1                  = [380466,380470]
# runs_2                  = [392524,392526] # 10665
runs_2                  = [392642] # 10671
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
elif disk:
    disk_number         = int(disk[-1])
    sectors             = [f"CH{str(i).zfill(2)}" for i in range(1,37)]
    chambers            = [
                            f"RE-{disk_number}_R2_C", f"RE-{disk_number}_R2_B", f"RE-{disk_number}_R2_A",
                            f"RE-{disk_number}_R3_C", f"RE-{disk_number}_R3_B", f"RE-{disk_number}_R3_A",
                            f"RE+{disk_number}_R3_A", f"RE+{disk_number}_R3_B", f"RE+{disk_number}_R3_C", 
                            f"RE+{disk_number}_R2_A", f"RE+{disk_number}_R2_B", f"RE+{disk_number}_R2_C",
                          ]

inst_lumi               = 10000 # we are going to fix the Inst.Lumi to: <inst_lumi> x 1e30cm^-2s^-1
GeometryFile_path       = "/afs/cern.ch/" + workdir + "/" + inituser + "/" + username + "/rpc-offline-analysis/analyzer/utils/RPCGeometry.out"
inJson_path_1           = f"/eos/user/l/lfavilla/rpc-offline-analysis/common-tuples-results/{fill_1}/{'_'.join((map(str,runs_1)))}/final_results_{fill_1}_{'_'.join((map(str,runs_1)))}{cleaning_suffix}.json"
inJson_path_2           = f"/eos/user/l/lfavilla/rpc-offline-analysis/common-tuples-results/{fill_2}/{'_'.join((map(str,runs_2)))}/final_results_{fill_2}_{'_'.join((map(str,runs_2)))}{cleaning_suffix}.json"
outFolder_path          = f"/eos/user/l/lfavilla/www/rpc-offline-analysis/common-tuples-results/NFS+_Effectiveness/"
plots_path              = outFolder_path + "plots/"
regions                 = ["Total", "Colliding", "NonColliding", "PreBeam", "BeamAbort"]
backgrounds             = [
                            "Inclusive",
                            "Delayed",
                            "Prompt"
                            ]

yMin                    = 0 # TO FIX
yMax                    = 3 # TO FIX 3 - 25
rMin                    = 0.5 # TO FIX
rMax                    = 1.5 # TO FIX

if fill_1 in fillsDict:
    totalLumi_1         = sum([fillsDict[fill_1].totalLumi[run] if run in fillsDict[fill_1].runs else 0 for run in runs_1])
else:
    print(f"Missing file list for fill number {fill_1}")
    sys.exit(1)
if fill_2 in fillsDict:
    totalLumi_2         = sum([fillsDict[fill_2].totalLumi[run] if run in fillsDict[fill_2].runs else 0 for run in runs_2])
else:
    print(f"Missing file list for fill number {fill_2}")
    sys.exit(1)

### Load Geometry File ###
df_geometry             = openGeomFile(GeometryFile_path)




if not os.path.exists(outFolder_path):
    os.makedirs(outFolder_path)
if not os.path.exists(plots_path):
    os.makedirs(plots_path)

if "www" in outFolder_path:
    os.system(f"cp /eos/user/l/lfavilla/www/index.php   {outFolder_path}")
    os.system(f"cp /eos/user/l/lfavilla/www/index.php   {plots_path}")




### Load final results for the specific run ###
with open(inJson_path_1, "r") as f:
    print(f"Loading final results from: {inJson_path_1}")
    inJson_1            = json.load(f)
with open(inJson_path_2, "r") as f:
    print(f"Loading final results from: {inJson_path_2}")
    inJson_2            = json.load(f)


### Check if the chamber is in the json file and if the rates are not None ###
for chamber in chambers:
    if chamber not in inJson_1:
        # print(f"Chamber {chamber} NOT found in the json file of fill {fill_1}.")
        sys.exit()
    elif (chamber in inJson_1) and any([inJson_1[chamber]["rates"][reg] is None for reg in regions]):
        # print(f"Seems it was NOT possible to calculate rates in REGIONS for chamber {chamber} for fill {fill_1}")
        sys.exit()
    elif (chamber in inJson_1) and any([inJson_1[chamber]["parameters"][bkg] is None for bkg in backgrounds]):
        # print(f"Seems it was NOT possible to calculate rates in BACKGROUNDS for chamber {chamber} for fill {fill_1}")
        sys.exit()

    if chamber not in inJson_2:
        # print(f"Chamber {chamber} NOT found in the json file of fill {fill_2}.")
        sys.exit()
    elif (chamber in inJson_2) and any([inJson_2[chamber]["rates"][reg] is None for reg in regions]):
        # print(f"Seems it was NOT possible to calculate rates in REGIONS for chamber {chamber} for fill {fill_2}")
        sys.exit()
    elif (chamber in inJson_2) and any([inJson_2[chamber]["parameters"][bkg] is None for bkg in backgrounds]):
        # print(f"Seems it was NOT possible to calculate rates in BACKGROUNDS for chamber {chamber} for fill {fill_2}")
        sys.exit()

    else:
        # print(f"Chamber {chamber} found in the json file with rates calculated properly for both fills.")
        pass



##########################################
### Fill the histograms with the rates ###
##########################################
# BACKGROUNDS #
minX, maxX                      = 9000, 21000
funcs_1                         = {}
rates_eta_1                     = {}
funcs_2                         = {}
rates_eta_2                     = {}
rates_eta_ratio                 = {}
for bkg in backgrounds:
    funcs_1[bkg]                    = {}
    funcs_2[bkg]                    = {}
    etaCenters                      = []
    etaCenters_1                    = []
    etaCenters_2                    = []
    YCenters_1                      = []
    YCenters_2                      = []
    etaErrors                       = []
    YErrors_1                       = []
    YErrors_2                       = []
    YCenters_ratio                  = []
    YErrors_ratio                   = []
    for chamber in chambers:
        rawIds                      = select_rawIds_in_chamber(df_geometry, chamber)
        combination                 = chamber.split("_")
        # hit rate vs. inst.lumi. functions for each background and chamber #
        funcs_1[bkg][chamber]         = ROOT.TF1("func_"+chamber+"_"+bkg, "pol1", minX, maxX)
        funcs_1[bkg][chamber].SetParameter(0, inJson_1[chamber]["parameters"][bkg]["p0"])
        funcs_1[bkg][chamber].SetParameter(1, inJson_1[chamber]["parameters"][bkg]["p1"])
        funcs_1[bkg][chamber].SetParError(0, inJson_1[chamber]["parameters"][bkg]["p0_error"])
        funcs_1[bkg][chamber].SetParError(1, inJson_1[chamber]["parameters"][bkg]["p1_error"])
        funcs_2[bkg][chamber]         = ROOT.TF1("func_"+chamber+"_"+bkg, "pol1", minX, maxX)
        funcs_2[bkg][chamber].SetParameter(0, inJson_2[chamber]["parameters"][bkg]["p0"])
        funcs_2[bkg][chamber].SetParameter(1, inJson_2[chamber]["parameters"][bkg]["p1"])
        funcs_2[bkg][chamber].SetParError(0, inJson_2[chamber]["parameters"][bkg]["p0_error"])
        funcs_2[bkg][chamber].SetParError(1, inJson_2[chamber]["parameters"][bkg]["p1_error"])



        # hit rate vs. inst.lumi. functions for each background and for each sector in the chamber selected (useful for the error estimation) #
        if station:
            chambers_with_sector                = [f"{chamber}_{sec}" for sec in sectors]
        elif disk:
            chambers_with_sector                = [name for name in inJson_1.keys() if (all(part in name.split("_") for part in combination) and (chamber != name))]
        YSectors_1                              = []
        YSectors_2                              = []
        YSectorsErrors_1                        = []
        YSectorsErrors_2                        = []
        for chamber_with_sector in chambers_with_sector:
            combination_with_sector             = chamber_with_sector.split("_")
            if inJson_1[chamber_with_sector]["parameters"][bkg] is None:
                # print(f"Seems it was NOT possible to calculate rates in BACKGROUNDS for chamber {chamber_with_sector} for fill {fill_1}")
                funcs_1[bkg][chamber_with_sector] = None
                continue
            elif inJson_2[chamber_with_sector]["parameters"][bkg] is None:
                # print(f"Seems it was NOT possible to calculate rates in BACKGROUNDS for chamber {chamber_with_sector} for fill {fill_2}")
                funcs_2[bkg][chamber_with_sector] = None
                continue
            funcs_1[bkg][chamber_with_sector]     = ROOT.TF1("func_"+chamber_with_sector+"_"+bkg, "pol1", minX, maxX)
            funcs_1[bkg][chamber_with_sector].SetParameter(0, inJson_1[chamber_with_sector]["parameters"][bkg]["p0"])
            funcs_1[bkg][chamber_with_sector].SetParameter(1, inJson_1[chamber_with_sector]["parameters"][bkg]["p1"])
            funcs_1[bkg][chamber_with_sector].SetParError(0, inJson_1[chamber_with_sector]["parameters"][bkg]["p0_error"])
            funcs_1[bkg][chamber_with_sector].SetParError(1, inJson_1[chamber_with_sector]["parameters"][bkg]["p1_error"])
            funcs_2[bkg][chamber_with_sector]     = ROOT.TF1("func_"+chamber_with_sector+"_"+bkg, "pol1", minX, maxX)
            funcs_2[bkg][chamber_with_sector].SetParameter(0, inJson_2[chamber_with_sector]["parameters"][bkg]["p0"])
            funcs_2[bkg][chamber_with_sector].SetParameter(1, inJson_2[chamber_with_sector]["parameters"][bkg]["p1"])
            funcs_2[bkg][chamber_with_sector].SetParError(0, inJson_2[chamber_with_sector]["parameters"][bkg]["p0_error"])
            funcs_2[bkg][chamber_with_sector].SetParError(1, inJson_2[chamber_with_sector]["parameters"][bkg]["p1_error"])

            rawIds_in_chamber_with_sector        = select_rawIds_in_chamber(df_geometry, chamber_with_sector)
            y1_                                  = funcs_1[bkg][chamber_with_sector].Eval(inst_lumi)
            yerr1_                               = sqrt(abs((inst_lumi**2)*inJson_1[chamber_with_sector]["parameters"][bkg]["p1_error"]**2 + inJson_1[chamber_with_sector]["parameters"][bkg]["p0_error"]**2 + 2*inst_lumi*inJson_1[chamber_with_sector]["parameters"][bkg]["cov_p0p1"]))
            YSectors_1.append(y1_)
            YSectorsErrors_1.append(yerr1_)
            y2_                                  = funcs_2[bkg][chamber_with_sector].Eval(inst_lumi)
            yerr2_                               = sqrt(abs((inst_lumi**2)*inJson_2[chamber_with_sector]["parameters"][bkg]["p1_error"]**2 + inJson_2[chamber_with_sector]["parameters"][bkg]["p0_error"]**2 + 2*inst_lumi*inJson_2[chamber_with_sector]["parameters"][bkg]["cov_p0p1"]))
            YSectors_2.append(y2_)
            YSectorsErrors_2.append(yerr2_)


        ############################################################
        # rate calculation for each background and chamber vs. eta #
        ############################################################
        eta_value                               = df_geometry[df_geometry["RPC_Id"].apply(lambda rawId: rawId in map(int,rawIds))]["eta"].mean()
        etaCenters.append(eta_value)
        # etaCenters_1.append(eta_value-0.01)
        # etaCenters_2.append(eta_value+0.01)
        if bkg == "Inclusive":
            etaCenters_1.append(eta_value-0.05) # to avoid overlapping with the next chamber
            etaCenters_2.append(eta_value-0.03) # to avoid overlapping with the next chamber
        elif bkg == "Delayed":
            etaCenters_1.append(eta_value-0.01)
            etaCenters_2.append(eta_value+0.01)
        elif bkg == "Prompt":
            etaCenters_1.append(eta_value+0.03)
            etaCenters_2.append(eta_value+0.05)
        y_1                                     = funcs_1[bkg][chamber].Eval(inst_lumi)
        y_2                                     = funcs_2[bkg][chamber].Eval(inst_lumi)
        YCenters_1.append(y_1)
        # YCenters_1.append(mean(YSectors))
        YCenters_2.append(y_2)
        # YCenters_2.append(mean(YSectors))
        etaErrors.append(0)
        # YErrors_1.append(0)
        # YErrors_2.append(0)
        if len(YSectors_1) > 1:
            yerr_1 = stdev(YSectors_1)
        else:
            yerr_1 = sqrt(abs((inst_lumi**2)*inJson_1[chamber]["parameters"][bkg]["p1_error"]**2 + inJson_1[chamber]["parameters"][bkg]["p0_error"]**2 + 2*inst_lumi*inJson_1[chamber]["parameters"][bkg]["cov_p0p1"]))
        if len(YSectors_2) > 1:
            yerr_2 = stdev(YSectors_2)
        else:
            yerr_2 = sqrt(abs((inst_lumi**2)*inJson_2[chamber]["parameters"][bkg]["p1_error"]**2 + inJson_2[chamber]["parameters"][bkg]["p0_error"]**2 + 2*inst_lumi*inJson_2[chamber]["parameters"][bkg]["cov_p0p1"]))
        YErrors_1.append(yerr_1)
        YErrors_2.append(yerr_2)


        y_ratio     = y_2/y_1
        y_err_ratio = y_ratio*sqrt((yerr_1/y_1)**2 + (yerr_2/y_2)**2)
        YCenters_ratio.append(y_ratio)
        # YErrors_ratio.append(0)
        YErrors_ratio.append(y_err_ratio)
    # rates_eta_1[bkg]                            = ROOT.TGraphErrors(len(etaCenters), array.array("f", etaCenters), array.array("f", YCenters_1), array.array("f", etaErrors), array.array("f", YErrors_1))
    # rates_eta_2[bkg]                            = ROOT.TGraphErrors(len(etaCenters), array.array("f", etaCenters), array.array("f", YCenters_2), array.array("f", etaErrors), array.array("f", YErrors_2))
    rates_eta_1[bkg]                            = ROOT.TGraphErrors(len(etaCenters_1), array.array("f", etaCenters_1), array.array("f", YCenters_1), array.array("f", etaErrors), array.array("f", YErrors_1))
    rates_eta_2[bkg]                            = ROOT.TGraphErrors(len(etaCenters_2), array.array("f", etaCenters_2), array.array("f", YCenters_2), array.array("f", etaErrors), array.array("f", YErrors_2))
    rates_eta_ratio[bkg]                        = ROOT.TGraphErrors(len(etaCenters), array.array("f", etaCenters), array.array("f", YCenters_ratio), array.array("f", etaErrors), array.array("f", YErrors_ratio))


### GRAPHIC OPTIONS ###
iPos   = 0                          # position of CMS label, 0 if out-of-frame, 11 if in-frame
lumi_1 = round(totalLumi_1*1e-3, 3) # fb-1
lumi_2 = round(totalLumi_2*1e-3, 3) # fb-1
energy = 13.6                       # TeV



###################################################################
##### PLOTTING RATES ALL BACKGROUNDS vs. eta - Single Chamber #####
###################################################################
if station:
    canvName        = f"rates_NFS+_Effectiveness_station_{station}_AllBackgroundsVsEta_{fill_1}_{fill_2}"
elif disk:
    canvName        = f"rates_NFS+_Effectiveness_disk_{disk}_AllBackgroundsVsEta_{fill_1}_{fill_2}"
path_png            = f"{plots_path}{canvName}.png"
path_pdf            = f"{plots_path}{canvName}.pdf"
path_C              = f"{plots_path}{canvName}.C"
# canv   = makeCanvas(h=rates_eta_1["Inclusive"],
#                     xMin=min(etaCenters)*1.1,
#                     xMax=max(etaCenters)*1.1,
#                     yMin=yMin,
#                     yMax=yMax,
#                     xTitle="#eta",
#                     yTitle="Hit Rate (Hz/cm^{2})",
#                     canvName=canvName,
#                     square=CMS.kRectangular,
#                     extraText="Private Work",
#                     iPos=iPos,
#                     energy=energy,
#                     lumi="lumi",
#                     addInfo="",
#                     extraSpace=0.0,
#                     labelSize=0.045,
#                     titleSize=0.045,
#                     labelOffset=0.003,
#                     titleOffset=0.9,
#                     with_z_axis=False,
#                     logy=True,
#                     grid=True,
#                     MaxDigitsX=3,
#                     MaxDigitsY=3,
#                     )

# canv = CMS.cmsDiCanvas(
#                     canvName=canvName,
#                     x_min=min(etaCenters)*1.1,
#                     x_max=max(etaCenters)*1.1,
#                     y_min=yMin,
#                     y_max=yMax,
#                     r_min=0,
#                     r_max=2,
#                     nameXaxis="#eta",
#                     nameYaxis="Hit Rate (Hz/cm^{2})",
#                     nameRatio="2025/2024 Data",
#                     square=CMS.kRectangular,
#                     iPos=iPos,
#                     extraSpace=0,
#                     scaleLumi=None,
#                     )
canv = makeDiCanvas(
                    h=rates_eta_1["Inclusive"],
                    canvName=canvName,
                    xMin=min(etaCenters)*1.1,
                    xMax=max(etaCenters)*1.1,
                    yMin=yMin,
                    yMax=yMax,
                    rMin=0,
                    rMax=2,
                    xTitle="#eta",
                    yTitle="Hit Rate (Hz/cm^{2})",
                    rTitle="2025/2024 Data",
                    square=CMS.kRectangular,
                    iPos=iPos,
                    energy=energy,
                    lumi=f"{lumi_1} (2024) & {lumi_2} (2025)",
                    extraSpace=0,
                    extraText="Private Work",
                    addInfo="other info",
                    )



CMS.cmsDraw(rates_eta_1["Inclusive"],
            "PE",
            marker=ROOT.kFullCircle,
            msize=0.75,
            mcolor=ROOT.kBlack,
            )
CMS.cmsDraw(rates_eta_1["Delayed"],
            "PE",
            marker=ROOT.kFullCircle,
            msize=0.75,
            mcolor=ROOT.kRed,
            )
CMS.cmsDraw(rates_eta_1["Prompt"],
            "PE",
            marker=ROOT.kFullCircle,
            msize=0.75,
            mcolor=ROOT.kBlue,
            )

CMS.cmsDraw(rates_eta_2["Inclusive"],
            "PE",
            marker=ROOT.kOpenSquare,
            msize=0.75,
            mcolor=ROOT.kBlack,
            )
CMS.cmsDraw(rates_eta_2["Delayed"],
            "PE",
            marker=ROOT.kOpenSquare,
            msize=0.75,
            mcolor=ROOT.kRed,
            )
CMS.cmsDraw(rates_eta_2["Prompt"],
            "PE",
            marker=ROOT.kOpenSquare,
            msize=0.75,
            mcolor=ROOT.kBlue,
            )

canv.cd(2)
CMS.cmsDraw(rates_eta_ratio["Inclusive"],
            "PE",
            marker=ROOT.kFullDiamond,
            msize=1.25,
            mcolor=ROOT.kBlack,
            )
CMS.cmsDraw(rates_eta_ratio["Delayed"],
            "PE",
            marker=ROOT.kFullDiamond,
            msize=1.25,
            mcolor=ROOT.kRed,
            )
CMS.cmsDraw(rates_eta_ratio["Prompt"],
            "PE",
            marker=ROOT.kFullDiamond,
            msize=1.25,
            mcolor=ROOT.kBlue,
            )

canv.cd()
latex = ROOT.TLatex()
latex.SetTextFont(52)
latex.SetTextSize(0.03)
# latex.SetTextAlign(22)
# latex.DrawLatexNDC(0.75, 0.87, f"fill:      {fill_number}") # x, y, text
# latex.DrawLatexNDC(0.75, 0.82, f"runs:      {'-'.join(map(str, runs_list))}") # x, y, text
if station:
    latex.DrawLatexNDC(0.75, 0.9, f"station:   {station}")
elif disk:
    latex.DrawLatexNDC(0.75, 0.9, f"disk:      {disk}")

leg = CMS.cmsLeg(0.15, 0.75, 0.5, 0.95, textSize=0.03, textFont=52, columns=2)
leg.AddEntry(rates_eta_1["Inclusive"],"2024 Inclusive","PE")
leg.AddEntry(rates_eta_2["Inclusive"],"2025 Inclusive","PE")
leg.AddEntry(rates_eta_1["Delayed"],"2024 Delayed","PE")
leg.AddEntry(rates_eta_2["Delayed"],"2025 Delayed","PE")
leg.AddEntry(rates_eta_1["Prompt"],"2024 Prompt","PE")
leg.AddEntry(rates_eta_2["Prompt"],"2025 Prompt","PE")


# leg.AddEntry("None", "", "")
# leg.AddEntry("None", f"run:   {run}", "")
# leg.AddEntry("None", "", "")
# leg.AddEntry("None", f"rawId: {rawId}", "")



CMS.SaveCanvas(canv, path_png, close=False)
CMS.SaveCanvas(canv, path_pdf, close=False)
CMS.SaveCanvas(canv, path_C, close=True)