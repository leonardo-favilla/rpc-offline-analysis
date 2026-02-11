import cmsstyle as CMS
import ROOT

def makeCanvas(h, xMin=None, xMax=None, yMin=None, yMax=None, xTitle="xTitle", yTitle="yTitle", logy=False, grid=False, extraSpace=0.0, canvName="canv", square=CMS.kSquare, extraText="Private Work", iPos=0, energy="13", lumi="", addInfo="", labelSize=0.045, titleSize=0.045, labelOffset=0.003, titleOffset=0.8, with_z_axis=False, MaxDigitsX=None, MaxDigitsY=None):
    # CMS.SetCmsText("") # default is "CMS", can be changed
    # CMS.SetCmsTextFont(52)
    # CMS.SetCmsTextSize(0.75*0.76)
    CMS.SetExtraText(extraText)
    CMS.SetLumi(lumi, unit="fb", round_lumi=False)
    CMS.SetEnergy(energy, unit="TeV")
    CMS.ResetAdditionalInfo()
    CMS.AppendAdditionalInfo(addInfo)
    # CMS.setCMSStyle()
    

    if xMin is None:
        xMin = h.GetXaxis().GetXmin()
    if xMax is None:
        xMax = h.GetXaxis().GetXmax()
    if yMin is None:
        yMin = 0.
    if yMax is None:
        yMax = h.GetMaximum() * 1.5

    # xTitle = h.GetXaxis().GetTitle()
    # yTitle = h.GetYaxis().GetTitle()
    canv = CMS.cmsCanvas(canvName, xMin, xMax, yMin, yMax, xTitle, yTitle, square=square, extraSpace=extraSpace, iPos=iPos, with_z_axis=with_z_axis)
    hdf  = CMS.GetcmsCanvasHist(canv)

    hdf.GetXaxis().SetLabelOffset(labelOffset)
    hdf.GetXaxis().SetLabelSize(labelSize)
    hdf.GetXaxis().SetTitleOffset(titleOffset)
    hdf.GetXaxis().SetTitleSize(titleSize)
    if MaxDigitsX is not None:
        hdf.GetXaxis().SetMaxDigits(MaxDigitsX)

    hdf.GetYaxis().SetLabelOffset(labelOffset)
    hdf.GetYaxis().SetLabelSize(labelSize)
    hdf.GetYaxis().SetTitleOffset(titleOffset)
    hdf.GetYaxis().SetTitleSize(titleSize)
    if MaxDigitsY is not None:
        hdf.GetYaxis().SetMaxDigits(MaxDigitsY)
    




    hdf.Draw("hist")
    CMS.CMS_lumi(canv, iPosX=iPos)

    if grid:
        canv.SetGridx()
        canv.SetGridy()
        canv.Update()
        # canv.SetGrid()
    
    if logy:
        canv.SetLogy()
        canv.Update()



    # Shift multiplier position
    # ROOT.TGaxis.SetExponentOffset(-0.10, 0.01, "Y")
    # leg = CMS.cmsLeg(0.5, 0.1, 0.98, 0.5, textSize=0.04)
    return canv






def makeDiCanvas(h, xMin=None, xMax=None, yMin=None, yMax=None, rMin=None, rMax=None, xTitle="xTitle", yTitle="yTitle", rTitle="rTitle", logy=False, grid=False, extraSpace=0.0, canvName="canv", square=CMS.kSquare, extraText="Private Work", iPos=0, energy="13", lumi="", addInfo="", labelSize=0.045, titleSize=0.045, labelOffset=0.003, titleOffset=0.8, with_z_axis=False, MaxDigitsX=None, MaxDigitsY=None):
    # CMS.SetCmsText("") # default is "CMS", can be changed
    # CMS.SetCmsTextFont(52)
    # CMS.SetCmsTextSize(0.75*0.76)
    CMS.SetExtraText(extraText)
    CMS.SetLumi(lumi, unit="fb", round_lumi=False)
    CMS.SetEnergy(energy, unit="TeV")
    CMS.ResetAdditionalInfo()
    CMS.AppendAdditionalInfo(addInfo)
    # CMS.setCMSStyle()
    

    if xMin is None:
        xMin = h.GetXaxis().GetXmin()
    if xMax is None:
        xMax = h.GetXaxis().GetXmax()
    if yMin is None:
        yMin = 0.
    if yMax is None:
        yMax = h.GetMaximum() * 1.5

    # xTitle = h.GetXaxis().GetTitle()
    # yTitle = h.GetYaxis().GetTitle()
    canv = CMS.cmsDiCanvas(
                            canvName=canvName,
                            x_min=xMin,
                            x_max=xMax,
                            y_min=yMin,
                            y_max=yMax,
                            r_min=rMin,
                            r_max=rMax,
                            nameXaxis=xTitle,
                            nameYaxis=yTitle,
                            nameRatio=rTitle,
                            square=square,
                            iPos=iPos,
                            extraSpace=extraSpace,
                            scaleLumi=None,
                            )
    
    return canv