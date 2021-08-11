import os, sys
from ROOT import TCanvas, TPad, TFile, TPaveLabel, TPaveText, TLatex, TLegend, TH1F, kRed, kGreen

# filename format : samplename_campaign.root 
# sample name should not contain underscores ( ex. Monojet1000 )
# identical root files should be in both Files/FastSim and Files/FullSim

fastsim_dir = os.getcwd()+"/Files/FastSim/"
fullsim_dir = os.getcwd()+"/Files/FullSim/"
output_dir = os.getcwd()+"/Outputs/"

for filename in os.listdir(fastsim_dir) : 
  # find identical sample+campaign 
  dirname = filename.split("_")[0]
  campname = filename.split("_")[1].split(".")[0]

  # make output directory structure
  if not os.path.exists(output_dir+dirname) :
    os.makedirs(output_dir+dirname)
  if not os.path.exists(output_dir+dirname+"/"+campname) :
    os.makedirs(output_dir+dirname+"/"+campname)
  if os.path.exists(output_dir+dirname) and not os.path.exists(output_dir+dirname+"/"+campname) :
    os.makedirs(output_dir+dirname+"/"+campname)

  fastsim = TFile(fastsim_dir+filename)
  fullsim = TFile(fullsim_dir+filename)
  plotdir = fastsim.Get("plots")

  for key in plotdir.GetListOfKeys() :
    histname = key.ReadObj().GetName()
    fasthist = fastsim.Get("plots/"+histname)
    fullhist = fullsim.Get("plots/"+histname)
    fasthist.SetStats(0)
    fullhist.SetStats(0)

    fasthist.SetLineColor(kRed+1)
    fasthist.SetFillColorAlpha(kRed+1,0.3)
    fullhist.SetLineColor(kGreen+1)
    fullhist.SetFillColorAlpha(kGreen+1,0.3)    

    c = TCanvas("c","",720,800)
    pad_up = TPad("pad_up","",0,0.25,1,1)
    pad_up.SetBottomMargin(0.02)
    pad_down = TPad("pad_down","",0,0,1,0.25)
    pad_down.SetGrid(1)
    pad_down.SetTopMargin(0.08)
    pad_down.SetBottomMargin(0.3)

    l = TLegend(0.65, 0.50, 0.93, 0.87)
    l.SetFillStyle(0)
    l.SetBorderSize(0)
    l.AddEntry(fasthist,"FastSim","f")
    l.AddEntry(fullhist,"FullSim","f")

    info = TLatex() ; info.SetTextSize(0.03) ; info.SetTextFont(42)
    logo = TLatex() ; logo.SetTextSize(0.04) ; logo.SetTextFont(61)
    extra_logo = TLatex() ; extra_logo.SetTextSize(0.035) ; extra_logo.SetTextFont(52)

    fullhist.GetXaxis().SetLabelSize(0)
    fasthist.GetXaxis().SetLabelSize(0)

    maximum = max(fullhist.GetMaximum(),fasthist.GetMaximum())
    if maximum is fullhist.GetMaximum() :
      fullhist.GetYaxis().SetRangeUser(0, maximum*1.8)
      fullhist.GetYaxis().SetTitle("Events")
      fullhist.GetYaxis().SetTitleOffset(1.4)
      if "Cut" in histname :
        fullhist.GetYaxis().SetRangeUser(1,maximum*30) ; pad_up.SetLogy()
    else : 
      fasthist.GetYaxis().SetRangeUser(0, maximum*1.8)
      fasthist.GetYaxis().SetTitle("Events")
      fasthist.GetYaxis().SetTitleOffset(1.4)     
      if "Cut" in histname :
        fasthist.GetYaxis().SetRangeUser(1,maximum*30) ; pad_up.SetLogy()   

    # make ratio plot
    ratio = fasthist.Clone("ratio")
    syst = fullhist.Clone("syst")
    ratio.Divide(syst)
    ratio.SetStats(0)
    ratio_syst = ratio.Clone("ratio_syst")
    ratio_syst.SetStats(0)
    ratio_syst.SetFillColorAlpha(12,0.6)
    ratio_syst.SetFillStyle(3144)
    ratio.SetTitle("")
    if "pt" or "HT" or "LT"  in histname :
      ratio.GetXaxis().SetTitle("pT [GeV]")
    if "eta" in histname :
      ratio.GetXaxis().SetTitle("#eta")
    if "phi" in histname :
      ratio.GetXaxis().SetTitle("#phi")
    ratio.GetXaxis().SetTitle("")
    ratio.GetXaxis().SetTitleSize(0.1)
    ratio.GetXaxis().SetTitleOffset(0.8)
    ratio.GetXaxis().SetLabelSize(0.08)
    
    ratio.GetYaxis().SetRangeUser(0,2)
    ratio.GetYaxis().SetTitle("Fast/Full")
    ratio.GetYaxis().CenterTitle()
    ratio.GetYaxis().SetTitleSize(0.1)
    ratio.GetYaxis().SetTitleOffset(0.4)
    ratio.GetYaxis().SetLabelSize(0.08)

    ratio.SetMarkerStyle(7)    

    # combine 
    pad_up.cd()
    fasthist.Draw("hist")
    fullhist.Draw("histsame")
    info.DrawLatexNDC(0.7, 0.91, dirname+"_"+campname)
    logo.DrawLatexNDC(0.15, 0.83, "CMS FastSim")
    extra_logo.DrawLatexNDC(0.15, 0.78, "Work in progress")
    l.Draw()
    pad_up.RedrawAxis()

    pad_down.cd()
    ratio.Draw("p&hist")
    ratio_syst.Draw("e2&f&same")

    c.cd()
    pad_up.Draw()
    pad_down.Draw()
    c.SaveAs(output_dir+dirname+"/"+campname+"/"+histname+".pdf")
    c.Close()


