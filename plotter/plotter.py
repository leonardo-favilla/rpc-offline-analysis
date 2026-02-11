import ROOT
import os
import sys
sys.path.append('../')
import cmsstyle as CMS # https://cmsstyle.readthedocs.io/en/latest/reference/ , https://cms-analysis.docs.cern.ch/guidelines/plotting/general/
ROOT.gROOT.SetBatch(True)
import json
import optparse
from math import sqrt
from plotting_functions import makeCanvas
from analyzer.utils.fillsInfo import *
import array

############################
######### SETTINGS #########
############################
usage               = "python3 plotter.py -f <fill_number> -r <runs_list> -c <chamber>"
parser              = optparse.OptionParser(usage)
parser.add_option("-f", "--fill",       dest="fill",    type=int,                                                   help="Fill number")
parser.add_option("-r", "--runs",       dest="runs",    type=str,                                                   help="Runs")
parser.add_option("-c", "--chamber",    dest="chamber", type=str,                                                   help="Chamber tag (check 'rpc_name' from '/analyzer/utils/RPCGeometry.out', can also be a wide region). Example: 'RE+4_R3_CH13_C', 'RE+4_R3_CH13' or 'RE+4_R3'")
parser.add_option(      "--cleaning",   dest="cleaning",            action="store_true", default=False,             help="Apply noisy strips cleaning (default: False)")
(opt, args)         = parser.parse_args()
fill_number         = opt.fill
runs_list           = list(map(int, opt.runs.split(",")))
chamber             = opt.chamber
cleaning            = opt.cleaning


if cleaning:
    cleaning_suffix = "_withNoisyStripsCleaning"
else:
    cleaning_suffix = "_noNoisyStripsCleaning"
inJson_path         = f"/eos/user/l/lfavilla/rpc-offline-analysis/common-tuples-results/{fill_number}/{'_'.join((map(str, runs_list)))}/final_results_{fill_number}_{'_'.join(map(str, runs_list))}{cleaning_suffix}.json"
outFolder_path      = f"/eos/user/l/lfavilla/www/rpc-offline-analysis/common-tuples-results/{fill_number}_{'_'.join(map(str, runs_list))}{cleaning_suffix}/"
plots_path          = outFolder_path + "plots/"
regions             = ["Total", "Colliding", "NonColliding", "PreBeam", "BeamAbort"]
backgrounds         = ["Inclusive", "Delayed", "Prompt"]
yMax                = 25 if "RE" in chamber else 5 # TO FIX


if fill_number in fillsDict:
    totalLumi    = sum([fillsDict[fill_number].totalLumi[run] if run in fillsDict[fill_number].runs else 0 for run in runs_list])
else:
    print("Missing file list for this fill number")
    sys.exit(1)

if not os.path.exists(outFolder_path):
    os.makedirs(outFolder_path)
if not os.path.exists(plots_path):
    os.makedirs(plots_path)

if "www" in outFolder_path:
    os.system(f"cp /eos/user/l/lfavilla/www/index.php   {outFolder_path}")
    os.system(f"cp /eos/user/l/lfavilla/www/index.php   {plots_path}")




### Load final results for the specific run ###
with open(inJson_path, "r") as f:
    print(f"Loading partial results from: {inJson_path}")
    inJson = json.load(f)


### Check if the chamber is in the json file and if the rates are not None ###
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
lumi_bins                                           = [[i, i + 1000] for i in range(0, 25000, 1000)]
# REGIONS #
histRatesRegions                                    = {}
fitsRegions                                         = {}
fitsRegions_band                                    = {}
for reg in regions:
    hist_rate   = ROOT.TH1F(f"hist_rates_{reg}", f"hist_rates_{reg}", len(lumi_bins), 0, 25000)
    fitFunc     = ROOT.TF1(f"fitFunc_{reg}", "pol1", 9000, 21000)
    for (l, u), [rate,rate_err] in zip(lumi_bins, inJson[chamber]["rates"][reg]):
        if l < 9000:
            continue
        bin_center = (l + u) / 2
        bin_num    = hist_rate.FindBin(bin_center)
        hist_rate.SetBinContent(bin_num, rate)
        hist_rate.SetBinError(bin_num, rate_err)
    fitFunc.SetParameter(0, inJson[chamber]["parameters"][reg]["p0"])
    fitFunc.SetParError(0, inJson[chamber]["parameters"][reg]["p0_error"])
    fitFunc.SetParameter(1, inJson[chamber]["parameters"][reg]["p1"])
    fitFunc.SetParError(1, inJson[chamber]["parameters"][reg]["p1_error"])

    histRatesRegions[reg]                           = hist_rate
    fitsRegions[reg]                                = fitFunc


    # ERROR BANDS for regions #
    XCenters    = range(9000, 22000, 1000)
    YCenters    = [fitFunc.Eval(x) for x in XCenters]
    XErrors     = [0 for x in XCenters]
    YErrors     = [sqrt((x**2)*inJson[chamber]["parameters"][reg]["p1_error"]**2 + inJson[chamber]["parameters"][reg]["p0_error"]**2 + 2*x*inJson[chamber]["parameters"][reg]["covMatrix"][0][1]) for x in XCenters]

    fitsRegions_band[reg] = ROOT.TGraphErrors(len(XCenters), array.array('f', XCenters), array.array('f', YCenters), array.array('f', XErrors), array.array('f', YErrors))


# BACKGROUNDS #
ratesBackgrounds                                    = {}                        
ratesBackgrounds_band                               = {}
for bkg in backgrounds:
    ratesBackgrounds[bkg]                           = ROOT.TF1(f"rate_{bkg}", "pol1", 9000, 21000)
    ratesBackgrounds[bkg].SetParameter(0, inJson[chamber]["parameters"][bkg]["p0"])
    ratesBackgrounds[bkg].SetParError(0, inJson[chamber]["parameters"][bkg]["p0_error"])
    ratesBackgrounds[bkg].SetParameter(1, inJson[chamber]["parameters"][bkg]["p1"])
    ratesBackgrounds[bkg].SetParError(1, inJson[chamber]["parameters"][bkg]["p1_error"])
    # ERROR BANDS for backgrounds #
    XCenters                                        = range(9000, 22000, 1000)
    YCenters                                        = [ratesBackgrounds[bkg].Eval(x) for x in XCenters]
    XErrors                                         = [0 for x in XCenters]
    YErrors                                         = [sqrt(abs((x**2)*inJson[chamber]["parameters"][bkg]["p1_error"]**2 + inJson[chamber]["parameters"][bkg]["p0_error"]**2 + 2*x*inJson[chamber]["parameters"][bkg]["cov_p0p1"])) for x in XCenters]

    ratesBackgrounds_band[bkg]                      = ROOT.TGraphErrors(len(XCenters), array.array("f", XCenters), array.array("f", YCenters), array.array("f", XErrors), array.array("f", YErrors))


### GRAPHIC OPTIONS ###
iPos   = 0                          # position of CMS label, 0 if out-of-frame, 11 if in-frame
lumi   = round(totalLumi*1e-3, 3)   # fb-1
energy = 13.6                       # TeV


######################################################################
##### PLOTTING RATES ALL REGIONS vs. inst.lumi. - Single Chamber #####
######################################################################
canvName            = f"rates_{fill_number}_{'_'.join((map(str, runs_list)))}_chamber_{chamber}_AllRegions"
path_png            = f"{plots_path}{canvName}.png"
path_pdf            = f"{plots_path}{canvName}.pdf"
path_C              = f"{plots_path}{canvName}.C"
canv   = makeCanvas(h=histRatesRegions["Total"],
                    xMin=0,
                    xMax=25000,
                    yMin=0,
                    # yMax=max([histRatesRegions[reg].GetMaximum()*1.5 for reg in regions]),
                    yMax=yMax,
                    xTitle="Instantaneous Luminosity (10^{30} cm^{-2} s^{-1})",
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
                    with_z_axis=True,
                    logy=False,
                    grid=True,
                    MaxDigitsX=3,
                    MaxDigitsY=3,
                    )




CMS.cmsDraw(h=histRatesRegions["Total"],
            style="PE",
            marker=ROOT.kFullCircle,
            msize=0.5,
            mcolor=ROOT.kBlack,
            )
CMS.cmsDraw(h=histRatesRegions["Colliding"],
            style="PE",
            marker=ROOT.kFullCircle,
            msize=0.5,
            mcolor=ROOT.kGreen,
            )
CMS.cmsDraw(h=histRatesRegions["NonColliding"],
            style="PE",
            marker=ROOT.kFullCircle,
            msize=0.5,
            mcolor=ROOT.kRed,
            )
CMS.cmsDraw(h=histRatesRegions["PreBeam"],
            style="PE",
            marker=ROOT.kFullCircle,
            msize=0.5,
            mcolor=ROOT.kBlue,
            )
CMS.cmsDraw(h=histRatesRegions["BeamAbort"],
            style="PE",
            marker=ROOT.kFullCircle,
            msize=0.5,
            mcolor=ROOT.kViolet,
            )



CMS.cmsObjectDraw(fitsRegions["Total"],
                    "L",
                    SetLineColor=ROOT.kBlack,
                    SetLineWidth=2,
                    )

CMS.cmsObjectDraw(fitsRegions["Colliding"],
                    "L",
                    SetLineColor=ROOT.kGreen,
                    SetLineWidth=2,
                    )

CMS.cmsObjectDraw(fitsRegions["NonColliding"],
                    "L",
                    SetLineColor=ROOT.kRed,
                    SetLineWidth=2,
                    )

CMS.cmsObjectDraw(fitsRegions["PreBeam"],
                    "L",
                    SetLineColor=ROOT.kBlue,
                    SetLineWidth=2,
                    )

CMS.cmsObjectDraw(fitsRegions["BeamAbort"],
                    "L",
                    SetLineColor=ROOT.kViolet,
                    SetLineWidth=2,
                    )



CMS.cmsObjectDraw(fitsRegions_band["Total"],
                    "E3",
                    SetFillColor=ROOT.kBlack,
                    SetFillStyle=3013,
                    )

CMS.cmsObjectDraw(fitsRegions_band["Colliding"],
                    "E3",
                    SetFillColor=ROOT.kGreen,
                    SetFillStyle=3013,
                    )

CMS.cmsObjectDraw(fitsRegions_band["NonColliding"],
                    "E3",
                    SetFillColor=ROOT.kRed,
                    SetFillStyle=3013,
                    )

CMS.cmsObjectDraw(fitsRegions_band["PreBeam"],
                    "E3",
                    SetFillColor=ROOT.kBlue,
                    SetFillStyle=3013,
                    )

CMS.cmsObjectDraw(fitsRegions_band["BeamAbort"],
                    "E3",
                    SetFillColor=ROOT.kViolet,
                    SetFillStyle=3013,
                    )



latex = ROOT.TLatex()
latex.SetTextFont(52)
latex.SetTextSize(0.03)
# latex.SetTextAlign(22)
latex.DrawLatexNDC(0.15, 0.67, f"fill:      {fill_number}") # x, y, text
latex.DrawLatexNDC(0.15, 0.62, f"runs:      {'-'.join(map(str, runs_list))}") # x, y, text
latex.DrawLatexNDC(0.15, 0.57, f"chamber:   {chamber}")
# latex.DrawLatexNDC(0.15, 0.52, f"#rawIds:   {len(rawIds)}")

leg = CMS.cmsLeg(0.15, 0.7, 0.4, 0.9, textSize=0.03, textFont=52, columns=2)
leg.AddEntry(histRatesRegions["Total"],"Total","P")
leg.AddEntry(histRatesRegions["Colliding"],"Colliding","P")
leg.AddEntry(histRatesRegions["NonColliding"],"NonColliding","P")
leg.AddEntry(histRatesRegions["PreBeam"],"PreBeam","P")
leg.AddEntry(histRatesRegions["BeamAbort"],"BeamAbort","P")
# leg.AddEntry("None", "", "")
# leg.AddEntry("None", f"run:   {run}", "")
# leg.AddEntry("None", "", "")
# leg.AddEntry("None", f"rawId: {rawId}", "")



CMS.SaveCanvas(canv, path_png, close=False)
CMS.SaveCanvas(canv, path_pdf, close=False)
CMS.SaveCanvas(canv, path_C, close=True)



##########################################################################
##### PLOTTING RATES ALL BACKGROUNDS vs. inst.lumi. - Single Chamber #####
##########################################################################
canvName            = f"rates_{fill_number}_{'_'.join((map(str, runs_list)))}_chamber_{chamber}_AllBackgrounds"
path_png            = f"{plots_path}{canvName}.png"
path_pdf            = f"{plots_path}{canvName}.pdf"
path_C              = f"{plots_path}{canvName}.C"
canv   = makeCanvas(h=ratesBackgrounds["Inclusive"],
                    xMin=0,
                    xMax=25000,
                    yMin=0,
                    yMax=yMax,
                    xTitle="Instantaneous Luminosity (10^{30} cm^{-2} s^{-1})",
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
                    with_z_axis=True,
                    logy=False,
                    grid=True,
                    MaxDigitsX=3,
                    MaxDigitsY=3,
                    )



CMS.cmsObjectDraw(ratesBackgrounds["Inclusive"],
                    "L",
                    SetLineColor=ROOT.kBlack,
                    SetLineWidth=2,
                    )
CMS.cmsDraw(h=ratesBackgrounds_band["Inclusive"],
            style="E3",
            fcolor=ROOT.kBlack,
            alpha=0.3,
            fstyle=3001,
            )
CMS.cmsObjectDraw(ratesBackgrounds["Delayed"],
                    "L",
                    SetLineColor=ROOT.kRed,
                    SetLineWidth=2,
                    )
CMS.cmsDraw(h=ratesBackgrounds_band["Delayed"],
            style="E3",
            fcolor=ROOT.kRed,
            alpha=0.3,
            fstyle=3001,
            )   
CMS.cmsObjectDraw(ratesBackgrounds["Prompt"],
                    "L",
                    SetLineColor=ROOT.kBlue,
                    SetLineWidth=2,
                    )
CMS.cmsDraw(h=ratesBackgrounds_band["Prompt"],
            style="E3",
            fcolor=ROOT.kBlue,
            alpha=0.3,
            fstyle=3001,
            )





latex = ROOT.TLatex()
latex.SetTextFont(52)
latex.SetTextSize(0.03)
# latex.SetTextAlign(22)
latex.DrawLatexNDC(0.15, 0.67, f"fill:      {fill_number}") # x, y, text
latex.DrawLatexNDC(0.15, 0.62, f"runs:      {'-'.join(map(str, runs_list))}") # x, y, text
latex.DrawLatexNDC(0.15, 0.57, f"chamber:   {chamber}")
# latex.DrawLatexNDC(0.15, 0.52, f"#rawIds:   {len(rawIds)}")

leg = CMS.cmsLeg(0.15, 0.7, 0.4, 0.9, textSize=0.03, textFont=52, columns=1)
leg.AddEntry(ratesBackgrounds["Inclusive"],"Inclusive","L")
leg.AddEntry(ratesBackgrounds["Delayed"],"Delayed","L")
leg.AddEntry(ratesBackgrounds["Prompt"],"Prompt","L")


# leg.AddEntry("None", "", "")
# leg.AddEntry("None", f"run:   {run}", "")
# leg.AddEntry("None", "", "")
# leg.AddEntry("None", f"rawId: {rawId}", "")



CMS.SaveCanvas(canv, path_png, close=False)
CMS.SaveCanvas(canv, path_pdf, close=False)
CMS.SaveCanvas(canv, path_C, close=True)
