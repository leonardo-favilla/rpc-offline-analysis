import cmsstyle as CMS
import ROOT
ROOT.gROOT.SetBatch(True)
import array
from plotting_functions import makeCanvas


histo = ROOT.TH1F("histo", "histo", 10, 0, 10)
for i in range(1, histo.GetNbinsX() + 1):
    histo.SetBinContent(i, i+1)

# nbins = 11
# XCenters = [i for i in range(nbins)]
# YCenters = [i+1 for i in range(nbins)]
# XErrors = [0 for x in range(nbins)]
# YErrors = [0 for x in range(nbins)]
# histo = ROOT.TGraphErrors(len(XCenters), array.array("f", XCenters), array.array("f", YCenters), array.array("f", XErrors), array.array("f", YErrors))
# histo2 = histo.Clone("histo2")
# histo2.Scale(2)
path                                                = "trial_canvas.png"
canvName, xMin, xMax, yMin, yMax, xTitle, yTitle    = "canvas", 0, 10, 1e-2, 1e2, "xTitle", "yTitle"
# canv                                                = CMS.cmsCanvas(canvName, xMin, xMax, yMin, yMax, xTitle, yTitle, )
# canv = makeCanvas(histo,
#             xMin=xMin,
#             xMax=xMax,
#             yMin=yMin,
#             yMax=yMax,
#             xTitle=xTitle,
#             yTitle=yTitle,
#             logy=True,
#             grid=True,
#             extraSpace=0.0,
#             canvName=canvName,
#             square=CMS.kRectangular,
#             extraTest="Private Work",
#             iPos=0,
#             energy="13",
#             lumi="",
#             addInfo="",
#             labelSize=0.045,
#             titleSize=0.045,
#             labelOffset=0.003,
#             titleOffset=0.8,
#             with_z_axis=False,
#         )



canv = CMS.cmsCanvas(canvName, xMin, xMax, yMin, yMax, xTitle, yTitle, square=CMS.kRectangular, extraSpace=0.0, iPos=0, with_z_axis=False)

XCenters = [i for i in range(10)]
YCenters = [i * 10 for i in range(10)]
XErrors = [0 for _ in range(10)]
YErrors = [0 for _ in range(10)]

h = ROOT.TH1F("histo", "histo", len(XCenters), 0, len(XCenters))
for i in range(len(XCenters)):
    h.SetBinContent(i + 1, YCenters[i])
    h.SetBinError(i + 1, YErrors[i])
h.SetMinimum(1)
h.SetMaximum(1000)
h.Draw("HIST")


canv.SetGridx()
canv.SetGridy()
canv.SetLogy()
canv.Update()


# hdf.Draw()

# canv.SetGrid()
# canv.SetTickx()
# canv.SetGridx()
# canv.SetGridy()
# CMS.CMS_lumi(canv)
# canv.Draw()

# CMS.cmsDraw(h=histo,
#             style="P",
#             mcolor=ROOT.kBlack,
#             )

# CMS.cmsDraw(h=histo2,
#             style="PSAME",
#             mcolor=ROOT.kRed,
#             )
# canv.SetTickx()
# canv.SetTicky()
# canv.SetGridx()
# canv.SetGridy()

# canv.cd()
# canv.SetGridx(False)
# canv.SetGridy(False)
# canv.Update()
# canv.SetLogy()
CMS.SaveCanvas(canv, path, close=True)