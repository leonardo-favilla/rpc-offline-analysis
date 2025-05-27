import ROOT

# Make sure interactive mode is OFF for debugging
ROOT.gROOT.SetBatch(True)

# Create canvas
c = ROOT.TCanvas("c", "c", 800, 600)
c.SetLogy()            # Enable log scale
c.SetGridx(True)       # Enable grid lines on x-axis
c.SetGridy(True)       # Enable grid lines on y-axis

h = ROOT.TH1F("h", "h", 10, 0, 10)
for i in range(1, 11):
    h.SetBinContent(i, i * 10)
h.SetMinimum(1)
h.SetMaximum(1000)
h.Draw()


c.Update()
c.SaveAs("test_grid.png")
