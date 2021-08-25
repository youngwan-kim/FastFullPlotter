import os, sys, argparse
from ROOT import TCanvas, TPad, TFile, TPaveLabel, TPaveText, TLatex, TLegend, TH1F, kRed, kGreen

# filename format : samplename_campaign.root 
# identical root files should be in both Files/FastSim and Files/FullSim

fastsim_dir = os.getcwd()+"/Files/FastSim/"
fullsim_dir = os.getcwd()+"/Files/FullSim/"
output_dir = os.getcwd()+"/Outputs/"

rebinvars = [ "pt","eta","phi" ]

parser = argparse.ArgumentParser(description='Simple Plotter')
parser.add_argument('--all', help="plot for full files", action="store_true")
parser.add_argument('-i', help="Input file name, ex) Monojet_100_UL16APV ",dest='input',default="")
args = parser.parse_args()

def plot(files) : 
  for filename in files :
  
    rescale = 0 ; n_ul16apv = 0 ; n_ul16 = 0 ;
    print("[Plotter] Plotting "+filename)
    dirname = filename.rsplit("_",1)[0]
    campname = filename.rsplit("_",1)[1].split(".")[0] 

    # make output directory structure
    if not os.path.exists(output_dir+dirname) :
      os.makedirs(output_dir+dirname)
    if not os.path.exists(output_dir+dirname+"/"+campname) :
      os.makedirs(output_dir+dirname+"/"+campname)
    if os.path.exists(output_dir+dirname) and not os.path.exists(output_dir+dirname+"/"+campname) :
      os.makedirs(output_dir+dirname+"/"+campname)

    # for FullSim UL16APV campaigns, use FastSim UL16 files for validation
    # rescaling is implemented by acting a scale factor to FullSim UL16APV histograms
    if campname == "UL16APV" :
      fastsim = TFile(fastsim_dir+dirname+"_UL16.root")
      if not os.path.isfile(fullsim_dir+dirname+"_UL16.root") :
        print("[Error] In order to rescale UL16APV FullSim files, UL16 campaign file for the sample is also needed")
	exit()
      else : 
        rescalefile = TFile(fullsim_dir+dirname+"_UL16.root")
    else : 
      fastsim = TFile(fastsim_dir+filename)
    fullsim = TFile(fullsim_dir+filename)
    plotdir = fullsim.Get("plots")  

    if campname == "UL16APV" :
      n_ul16 = rescalefile.Get("plots/TotalEvents").GetBinContent(1)
      n_ul16apv = fullsim.Get("plots/TotalEvents").GetBinContent(1)
      rescale = n_ul16 / n_ul16apv

    for key in plotdir.GetListOfKeys() :
      histname = key.ReadObj().GetName()
      fasthist = fastsim.Get("plots/"+histname)
      fullhist = fullsim.Get("plots/"+histname)
      fasthist.SetStats(0)
      fullhist.SetStats(0)

      if campname == "UL16APV" :
        fullhist = fullhist * rescale
	print("rescaling fullsim ul16apv histograms")  

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
      l.AddEntry(fasthist,"FastSim","lf")
      l.AddEntry(fullhist,"FullSim","lf")
      
      info = TLatex() ; info.SetTextSize(0.03) ; info.SetTextFont(42)
      logo = TLatex() ; logo.SetTextSize(0.04) ; logo.SetTextFont(61)
      extra_logo = TLatex() ; extra_logo.SetTextSize(0.035) ; extra_logo.SetTextFont(52)
      
      fullhist.GetXaxis().SetLabelSize(0)
      fasthist.GetXaxis().SetLabelSize(0)
      
      for rebinvar in rebinvars :
        if rebinvar in histname : 
          fasthist.Rebin(2)
          fullhist.Rebin(2)
  
      # make ratio plot
      ratio = fasthist.Clone("ratio")
      full = fullhist.Clone("full")
      ratio.Divide(full)
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
        ratio.GetXaxis().SetTitleSize(0.1)
        ratio.GetXaxis().SetTitleOffset(0.8)
        ratio.GetXaxis().SetLabelSize(0.08)
    
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
      
files=[]

if args.all : 

  fastsimfiles=[] ; fullsimfiles=[]
  onlyfastsim=[] ; onlyfullsim=[]

  if args.input != "" :
    print("[Error] Should use option --all or -i, not both")
 
  else :

    for filename in os.listdir(fastsim_dir) : 
      fastsimfiles.append(filename)
    for filename in os.listdir(fullsim_dir) :
      fullsimfiles.append(filename)

    onlyfastsim = list(set(fastsimfiles)-set(fullsimfiles))
    onlyfullsim = list(set(fullsimfiles)-set(fastsimfiles))
    files = list(set(fastsimfiles)-set(onlyfastsim))

    for onlyfast in onlyfastsim :
      print("[Plotter] FullSim file "+onlyfast+" doesn't exist in the FullSim directory. Skipping "+onlyfast+"...")

    for onlyfull in onlyfullsim :
      if onlyfull.endswith("16APV.root") :
        files.append(onlyfull)
        onlyfullsim.remove(onlyfull)
      
    for onlyfull in onlyfullsim : 
      print("[Plotter] FastSim file "+onlyfull+" doesn't exist in the FastSim directory. Skipping "+onlyfull+"...")

    print("[Plotter] Files to be plotted : " + ",".join(files))

    plot(files)

else :
  if args.input is "" :
    print("[Error] Input dataset_campaign should be specified!")

  else :
    files.append(args.input+".root")
    plot(files)

