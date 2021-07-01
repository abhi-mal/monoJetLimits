#!/usr/bin/env python
from ROOT import *
import os
from argparse import ArgumentParser
import json
from array import array
from PlotTool import *
import re
from collections import OrderedDict

gROOT.SetBatch(1)

outdir_base = "/afs/hep.wisc.edu/home/mallampalli/private/Analysis/MonoJet/test/%s/"
home = os.getcwd()
#####################################################################
def drawPlot2D(data):
    print 'Plotting 2D'
    lumi = data.lumi
    year = data.year
    variable = data.variable
    cut = data.cut
    mods = data.mods
    sysdir = data.sysdir
    #limit,mxlist,mvlist = Plot2D(data,include_central)
    limit,mxlist,mvlist = Plot2D(data)
    xbins = len(mvlist)
    ybins = len(mxlist)
    ######################################################################
    c = TCanvas("c","c",1000,800)
    c.SetMargin(0.1,0.15,0.15,0.08)
    c.SetLogz()
    gStyle.SetOptStat(0);
    gStyle.SetLegendBorderSize(0);
    gStyle.SetPaintTextFormat("0.1e")

    limit.Draw('COLZ TEXT')
    limit.SetStats(0)

    limit.GetZaxis().SetTitle("95% CL limit on #sigma/#sigma_{theory}")
    limit.GetZaxis().SetTitleOffset(1.2)
    zmin = min( ibin for ibin in limit if ibin > 0); zmax = limit.GetMaximum()
    limit.GetZaxis().SetRangeUser(zmin*0.8,zmax*1.2)
    
    ################################################################
    lumi_label = '%s' % float('%.3g' % (lumi/1000.)) + " fb^{-1}"
    texS = TLatex(0.55,0.93,("#sqrt{s} = 13 TeV, "+lumi_label));
    texS.SetNDC();
    texS.SetTextFont(42);
    texS.SetTextSize(0.035);
    texS.Draw();
    texS1 = TLatex(0.15,0.93,"#bf{CMS} : #it{Preliminary} (%s)" % year);
    texS1.SetNDC();
    texS1.SetTextFont(42);
    texS1.SetTextSize(0.035);
    texS1.Draw();
    ################################################################
    c.Modified()
    c.Update()

    outdir = outdir_base % year
    checkdir(outdir)
    subdir = variable
    outdir += '/%s' % subdir
    checkdir(outdir)
    outdir += '/%s' % sysdir
    checkdir(outdir)
    fname = 'limits_%s2D.png' % (sysdir)
    c.SaveAs( '%s/%s' % (outdir,fname) )
#####################################################################
def drawPlot1D(data):
    print 'Plotting 1D'
    lumi = data.lumi
    year = data.year
    variable = data.variable
    cut = data.cut
    mods = data.mods
    sysdir = data.sysdir
    #plots,mxlist = Plot1D(data,include_central)
    plots,mxlist = Plot1D(data)
    print(mxlist)
    print(plots) 
 

    class Bounds:
        def __init__(self):
            self.xmax = None
            self.xmin = None
            self.ymax = None
            self.ymin = None
        def setBounds(self,x,y):
            if self.xmax is None: self.xmax = x
            if self.xmin is None: self.xmin = x
            if self.ymax is None: self.ymax = y
            if self.ymin is None: self.ymin = y

            self.xmax = max(self.xmax,x)
            self.xmin = min(self.xmin,x)
            self.ymax = max(self.ymax,y)
            self.ymin = min(self.ymin,y)
        def getBounds(self): return self.xmin,self.xmax,self.ymin,self.ymax
        def __str__(self): return 'x: [%f-%f] y: [%f-%f]' % (self.xmin,self.xmax,self.ymin,self.ymax)
    bounds = Bounds()
    for mx,graph in plots.iteritems():
        x,y = Double(0),Double(0)
        for i in range(graph.GetN()):
            graph.GetPoint(i,x,y)
            bounds.setBounds(float(x),float(y))

    minX,maxX,minY,maxY = bounds.getBounds()
    print(bounds)
    ######################################################################

    c = TCanvas("c","c",800,800)
    c.SetLogy()
    # c.SetMargin(0.15,0.15,0.15,0.08)
    gStyle.SetOptStat(0);
    gStyle.SetLegendBorderSize(0);
    # gStyle.SetPalette(kRainBow)

    limits = TMultiGraph()
    legend = TLegend(0.4,0.65,0.65,0.82,"")
    legend.SetTextSize(0.02)
    legend.SetFillColor(0)
    for mx in mxlist:
        limit = plots[mx]
        limit.SetLineColor(colormap[mx])
        limit.SetLineWidth(3)
        legend.AddEntry(limit,'m_{#chi} = '+mx+' GeV','l')
        limits.Add(limit)
    limits.Draw('a l * PMC')
    limits.GetXaxis().SetRangeUser(minX,maxX)
    limits.GetYaxis().SetRangeUser(10**-1,10**2) #SetRangeUser(10**-3.5,10**5.5)
#    limits.GetXaxis().SetTitle("m_{med} (GeV)") #dmsimp
#    limits.GetXaxis().SetTitle("Bulk Mass MD (TeV)") #ADD
#    limits.GetXaxis().SetTitle("leptoquark coupling Y_{lq}") #leptoquark
    limits.GetYaxis().SetTitle("95% CL limit on #sigma/#sigma_{theor}")
    limits.GetXaxis().SetTitleSize(0.04)
    limits.GetYaxis().SetTitleSize(0.04)
    limits.GetXaxis().SetTitleOffset(0.92)
    limits.GetYaxis().SetTitleOffset(0.92)
    limits.GetXaxis().SetLabelSize(0.03)
    limits.GetYaxis().SetLabelSize(0.03)
    ################################################################

    lumi_label = '%s' % float('%.3g' % (lumi/1000.)) + " fb^{-1}"
    texS = TLatex(0.20,0.837173,("#sqrt{s} = 13 TeV, "+lumi_label));
    texS.SetNDC();
    texS.SetTextFont(42);
    texS.SetTextSize(0.040);
    texS.Draw('same');
    texS1 = TLatex(0.12092,0.907173,"#bf{CMS} : #it{Preliminary} (%s)" % year);
    texS1.SetNDC();
    texS1.SetTextFont(42);
    texS1.SetTextSize(0.040);
    texS1.Draw('same');

    legend.Draw('same')

    line = TLine(minX,1,maxX,1)
    line.SetLineStyle(8)
    line.Draw('same')
    
    c.Modified()
    c.Update()

    outdir = outdir_base % year
    checkdir(outdir)
    subdir = variable
    outdir += '/%s' % subdir
    checkdir(outdir)
    outdir += '/%s' % sysdir
    checkdir(outdir)
    fname = 'limits_%s1D.png' % (sysdir)
    c.SaveAs( '%s/%s' % (outdir,fname) )
#####################################################################
def drawPlot1D_1param(data,mass_param): # Use this to plot the 1D version for only 1 mass point with the expected,+-1 segma and the observed
    print 'Plotting 1D_1param for mchi=%s'%mass_param
    lumi = data.lumi
    year = data.year
    variable = data.variable
    cut = data.cut
    mods = data.mods
    sysdir = data.sysdir
    #plots,mxlist = Plot1D(data,include_central)
    plots = Plot1D_1param(data,mass_param)
    print(plots) 
    class Bounds:
        def __init__(self):
            self.xmax = None
            self.xmin = None
            self.ymax = None
            self.ymin = None
        def setBounds(self,x,y):
            if self.xmax is None: self.xmax = x
            if self.xmin is None: self.xmin = x
            if self.ymax is None: self.ymax = y
            if self.ymin is None: self.ymin = y

            self.xmax = max(self.xmax,x)
            self.xmin = min(self.xmin,x)
            self.ymax = max(self.ymax,y)
            self.ymin = min(self.ymin,y)
        def getBounds(self): return self.xmin,self.xmax,self.ymin,self.ymax
        def __str__(self): return 'x: [%f-%f] y: [%f-%f]' % (self.xmin,self.xmax,self.ymin,self.ymax)
    bounds = Bounds()
    for graph_type,graph in plots.iteritems():
        x,y = Double(0),Double(0)
        for i in range(graph.GetN()):
            graph.GetPoint(i,x,y)
            bounds.setBounds(float(x),float(y))

    minX,maxX,minY,maxY = bounds.getBounds()
    print(bounds)
    ######################################################################
    draw=['exp2', 'exp1', 'exp0', 'obs']
    #draw=['exp-2', 'exp-1', 'exp0','exp+1', 'exp+2', 'obs']
    style_dict = {
             'obs' : { 'LineWidth' : 2, 'LineStyle': 9, 'MarkerSize': 1.5 ,'MarkerStyle': 20},
             'exp0' : { 'LineWidth' : 2, 'LineColor' : kRed, 'LineStyle': 1},
             'exp1' : { 'FillColor' : kGreen},
             'exp2' : { 'FillColor' : kYellow},
             'exp-1' : { 'LineWidth' : 2, 'LineColor' : kGreen, 'LineStyle': 1},
             'exp+1' : { 'LineWidth' : 2, 'LineColor' : kGreen, 'LineStyle': 1},
             'exp-2' : { 'LineWidth' : 2, 'LineColor' : kYellow, 'LineStyle': 1},
             'exp+2' : { 'LineWidth' : 2, 'LineColor' : kYellow, 'LineStyle': 1}
    }

    legend_dict = {
         'obs' : { 'Label' : 'Observed', 'LegendStyle' : 'LP', 'DrawStyle' : 'PLSAME'},
         'exp0' : { 'Label' : 'Expected', 'LegendStyle' : 'L', 'DrawStyle' : 'LSAME'},
         'exp1' : { 'Label' : '#pm1#sigma Expected', 'LegendStyle' : 'F', 'DrawStyle' : '3SAME'},
         'exp2' : { 'Label' : '#pm2#sigma Expected', 'LegendStyle' : 'F', 'DrawStyle' : '3SAME'},
         'exp-1' : { 'Label' : '-1 sigma Expected', 'LegendStyle' : 'L', 'DrawStyle' : 'LSAME'},
         'exp+1' : { 'Label' : '+1 sigma Expected', 'LegendStyle' : 'L', 'DrawStyle' : 'LSAME'},
         'exp-2' : { 'Label' : '-2 sigma Expected', 'LegendStyle' : 'L', 'DrawStyle' : 'LSAME'},
         'exp+2' : { 'Label' : '+2 sigma Expected', 'LegendStyle' : 'L', 'DrawStyle' : 'LSAME'}

     }

    c = TCanvas("c","c",800,800)
    c.SetLogy()
    # c.SetMargin(0.15,0.15,0.15,0.08)
    gStyle.SetOptStat(0);
    gStyle.SetLegendBorderSize(0);
    # gStyle.SetPalette(kRainBow)

    limits = TMultiGraph()
    legend = TLegend(0.6,0.2,0.9,0.5,"")
    legend.SetTextSize(0.02)
    legend.SetFillColor(0)
    for key in draw:
        if key in plots:
            print(key)
            #plots[key].Sort()
            legend.AddEntry(plots[key],legend_dict[key]['Label'],legend_dict[key]['LegendStyle'])
            if 'LineWidth' in style_dict[key]: plots[key].SetLineWidth(style_dict[key]['LineWidth'])
            if 'LineColor' in style_dict[key]: plots[key].SetLineColor(style_dict[key]['LineColor'])
            if 'FillColor' in style_dict[key]: plots[key].SetFillColor(style_dict[key]['FillColor'])
            if 'LineStyle' in style_dict[key]: plots[key].SetLineStyle(style_dict[key]['LineStyle'])
            if 'MarkerSize' in style_dict[key]: plots[key].SetMarkerSize(style_dict[key]['MarkerSize'])
            if 'MarkerStyle' in style_dict[key]: plots[key].SetMarkerStyle(style_dict[key]['MarkerStyle'])
            limits.Add(plots[key],legend_dict[key]['DrawStyle'])

    limits.Draw('a')
    limits.GetXaxis().SetLimits(minX,maxX) #limits.GetXaxis().SetRangeUser(minX,maxX)
    limits.GetYaxis().SetRangeUser(10**-3,10**1) #SetRangeUser(10**-3.5,10**5.5)
    limits.GetXaxis().SetTitle("m_{med} (GeV)")
    limits.GetYaxis().SetTitle("95% CL limit on #sigma/#sigma_{theor}")
    limits.GetXaxis().SetTitleSize(0.04)
    limits.GetYaxis().SetTitleSize(0.04)
    limits.GetXaxis().SetTitleOffset(0.92)
    limits.GetYaxis().SetTitleOffset(0.92)
    limits.GetXaxis().SetLabelSize(0.03)
    limits.GetYaxis().SetLabelSize(0.03)            
    ################################################################

    lumi_label = '%s' % float('%.3g' % (lumi/1000.)) + " fb^{-1}"
    texS = TLatex(0.20,0.837173,("#sqrt{s} = 13 TeV, "+lumi_label));
    texS.SetNDC();
    texS.SetTextFont(42);
    texS.SetTextSize(0.040);
    texS.Draw('same');
    texS1 = TLatex(0.12092,0.907173,"#bf{CMS} : #it{Preliminary} (%s)" % year);
    texS1.SetNDC();
    texS1.SetTextFont(42);
    texS1.SetTextSize(0.040);
    texS1.Draw('same');

    legend.Draw('same')

    line = TLine(minX,1,maxX,1)
    line.SetLineStyle(8)
    line.Draw('same')
    
    c.Modified()
    c.Update()
    gROOT.GetListOfCanvases().Draw()
    outdir = outdir_base % year
    #checkdir(outdir)
    subdir = variable
    outdir += '/%s' % subdir
    #checkdir(outdir)
    outdir += '/%s' % sysdir
    #checkdir(outdir)
    fname = 'limits_%s1D_mchi=%sGeV.png' % (sysdir,mass_param)
    c.SaveAs( '%s/%s' % (outdir,fname) )
#####################################################################
def drawPlot2D_intersection(data,y_coord): # Use this to plot the 2D version limits where the limits line intersects the y=y_coord value
    print 'Plotting 2D intersections of the limit curves with line y=%s for all mchi'%y_coord
    lumi = data.lumi
    year = data.year
    variable = data.variable
    cut = data.cut
    mods = data.mods
    sysdir = data.sysdir
    #plots,mxlist = Plot1D(data,include_central)
    plots = Plot2D_intersection(data,y_coord)
    print(plots) 
    class Bounds:
        def __init__(self):
            self.xmax = None
            self.xmin = None
            self.ymax = None
            self.ymin = None
        def setBounds(self,x,y):
            if self.xmax is None: self.xmax = x
            if self.xmin is None: self.xmin = x
            if self.ymax is None: self.ymax = y
            if self.ymin is None: self.ymin = y

            self.xmax = max(self.xmax,x)
            self.xmin = min(self.xmin,x)
            self.ymax = max(self.ymax,y)
            self.ymin = min(self.ymin,y)
        def getBounds(self): return self.xmin,self.xmax,self.ymin,self.ymax
        def __str__(self): return 'x: [%f-%f] y: [%f-%f]' % (self.xmin,self.xmax,self.ymin,self.ymax)
    bounds = Bounds()
    xlist = []; ylist = []; ylist_obs = [] ; ylist_exp_minus1 = [] ; ylist_exp_minus2 = [] ; ylist_exp_plus1 = [] ; ylist_exp_plus2 = []
    print(plots) ; plots = OrderedDict(sorted(plots.iteritems(), key =lambda ele : float(ele[0]))); print(plots) ; raw_input("order?")
    for mx,mx_dict in plots.iteritems():    
        for intersec_type,intersec_value in mx_dict.iteritems():
                x = float(mx) ; y = intersec_value ; bounds.setBounds(float(x),float(y))
                if x not in xlist : xlist.append(x)
                if '0' in intersec_type: ylist.append(y)
                elif '+1' in intersec_type: ylist_exp_plus1.append(y)
                elif '-1' in intersec_type: ylist_exp_minus1.append(y)
                elif '+2' in intersec_type: ylist_exp_plus2.append(y)
                elif '-2' in intersec_type: ylist_exp_minus2.append(y)
                else : ylist_obs.append(y)
    xlist = array('d',xlist); ylist = array('d',ylist); ylist_obs = array('d',ylist_obs)
    graphs = {}
    graphs['exp0'] = TGraph(len(xlist),xlist,ylist)
    graphs['obs']  = TGraph(len(xlist),xlist,ylist_obs)
    def get_band(up_y,down_y,name,xlist=xlist,central_y=ylist):
        print("####") ; print(up_y) ; print("####")
        print("####") ; print(down_y) ; print("####")
        print("####") ; print(name) ; print("####")
        print("####") ; print(xlist) ; print("####")
        print("####") ; print(central_y) ; print("####")
        yvals_lo = [a_i - b_i for a_i,b_i in zip(central_y,down_y)]
        yvals_hi = [a_i - b_i for a_i,b_i in zip(up_y,central_y)]
        print("$$$$") ; print(yvals_lo) ; print("$$$$")
        print("$$$$") ; print(yvals_hi) ; print("$$$$")
        graphs[name] = TGraphAsymmErrors(len(xlist),xlist,central_y,array('d', [0.5]),array('d', [0.5]),array('d', yvals_lo), array('d', yvals_hi)); graphs[name].Sort()            
    get_band(ylist_exp_plus1,ylist_exp_minus1,'exp1')    
    get_band(ylist_exp_plus2,ylist_exp_minus2,'exp2')

    minX,maxX,minY,maxY = bounds.getBounds()
    print(bounds)
    ######################################################################
    draw=['exp2', 'exp1', 'exp0', 'obs']
    #draw=['exp-2', 'exp-1', 'exp0','exp+1', 'exp+2', 'obs']
    style_dict = {
             'obs' : { 'LineWidth' : 2, 'LineStyle': 9, 'MarkerSize': 1.5 ,'MarkerStyle': 20},
             'exp0' : { 'LineWidth' : 2, 'LineColor' : kRed, 'LineStyle': 1},
             'exp1' : { 'FillColor' : kGreen},
             'exp2' : { 'FillColor' : kYellow},
             'exp-1' : { 'LineWidth' : 2, 'LineColor' : kGreen, 'LineStyle': 1},
             'exp+1' : { 'LineWidth' : 2, 'LineColor' : kGreen, 'LineStyle': 1},
             'exp-2' : { 'LineWidth' : 2, 'LineColor' : kYellow, 'LineStyle': 1},
             'exp+2' : { 'LineWidth' : 2, 'LineColor' : kYellow, 'LineStyle': 1}
    }

    legend_dict = {
         'obs' : { 'Label' : 'Observed', 'LegendStyle' : 'LP', 'DrawStyle' : 'PLSAME'},
         'exp0' : { 'Label' : 'Expected', 'LegendStyle' : 'L', 'DrawStyle' : 'LSAME'},
         'exp1' : { 'Label' : '#pm1#sigma Expected', 'LegendStyle' : 'F', 'DrawStyle' : '3SAME'},
         'exp2' : { 'Label' : '#pm2#sigma Expected', 'LegendStyle' : 'F', 'DrawStyle' : '3SAME'},
         'exp-1' : { 'Label' : '-1 sigma Expected', 'LegendStyle' : 'L', 'DrawStyle' : 'LSAME'},
         'exp+1' : { 'Label' : '+1 sigma Expected', 'LegendStyle' : 'L', 'DrawStyle' : 'LSAME'},
         'exp-2' : { 'Label' : '-2 sigma Expected', 'LegendStyle' : 'L', 'DrawStyle' : 'LSAME'},
         'exp+2' : { 'Label' : '+2 sigma Expected', 'LegendStyle' : 'L', 'DrawStyle' : 'LSAME'}

     }

    c = TCanvas("c","c",800,800)
    #c.SetLogy()
    # c.SetMargin(0.15,0.15,0.15,0.08)
    gStyle.SetOptStat(0);
    gStyle.SetLegendBorderSize(0);
    # gStyle.SetPalette(kRainBow)

    limits = TMultiGraph()
    legend = TLegend(0.4,0.65,0.65,0.82,"")
    legend.SetTextSize(0.02)
    legend.SetFillColor(0)
    for key in draw:
        if key in graphs:
            print(key)
            #plots[key].Sort()
            legend.AddEntry(graphs[key],legend_dict[key]['Label'],legend_dict[key]['LegendStyle'])
            if 'LineWidth' in style_dict[key]: graphs[key].SetLineWidth(style_dict[key]['LineWidth'])
            if 'LineColor' in style_dict[key]: graphs[key].SetLineColor(style_dict[key]['LineColor'])
            if 'FillColor' in style_dict[key]: graphs[key].SetFillColor(style_dict[key]['FillColor'])
            if 'LineStyle' in style_dict[key]: graphs[key].SetLineStyle(style_dict[key]['LineStyle'])
            if 'MarkerSize' in style_dict[key]: graphs[key].SetMarkerSize(style_dict[key]['MarkerSize'])
            if 'MarkerStyle' in style_dict[key]: graphs[key].SetMarkerStyle(style_dict[key]['MarkerStyle'])
            limits.Add(graphs[key],legend_dict[key]['DrawStyle'])

    limits.Draw('a')
    #limits.Draw('ap2') # ADD #FIXME
   # limits.GetXaxis().SetLimits(minX-0.5,maxX+0.5) # leptoquark
    limits.GetXaxis().SetLimits(minX-50,maxX+50) #limits.GetXaxis().SetRangeUser(minX,maxX)# dmsimp
    #limits.GetXaxis().SetLimits(800-50,2000+50) # leptoquark
    limits.GetYaxis().SetRangeUser(minY-50,maxY+50) # dmsimp
   # limits.GetYaxis().SetRangeUser(0,20) # ADD
   # limits.GetYaxis().SetRangeUser(0,2) # leptoquark
   # limits.GetXaxis().SetTitle("Number of extra dimensions d") # ADD
   # limits.GetYaxis().SetTitle("95% CL lower limit on Bulk Mass MD(TeV)") # ADD
   # limits.GetXaxis().SetTitle("Leptoquark Mass M_{lq} (GeV)") # leptoquark
   # limits.GetYaxis().SetTitle("95% CL upper limit on leptoquark coupling Y_{lq} ")# leptoquark
    limits.GetXaxis().SetTitle("Mediator mass M_{#phi} (GeV)") # dmsimp
    limits.GetYaxis().SetTitle("95% CL upper limit on DM mass M_{#chi} ")# dmsimp
    limits.GetXaxis().SetTitleSize(0.04)
    limits.GetYaxis().SetTitleSize(0.04)
    limits.GetXaxis().SetTitleOffset(0.92)
    limits.GetYaxis().SetTitleOffset(0.92)
    limits.GetXaxis().SetLabelSize(0.03)
    limits.GetYaxis().SetLabelSize(0.03)            
    ################################################################

    lumi_label = '%s' % float('%.3g' % (lumi/1000.)) + " fb^{-1}"
    texS = TLatex(0.20,0.837173,("#sqrt{s} = 13 TeV, "+lumi_label));
    texS.SetNDC();
    texS.SetTextFont(42);
    texS.SetTextSize(0.040);
    texS.Draw('same');
    texS1 = TLatex(0.12092,0.907173,"#bf{CMS} : #it{Preliminary} (%s)" % year);
    texS1.SetNDC();
    texS1.SetTextFont(42);
    texS1.SetTextSize(0.040);
    texS1.Draw('same');

    legend.Draw('same')

    line = TLine(minX,1,maxX,1)
    line.SetLineStyle(8)
    line.Draw('same')
    
    c.Modified()
    c.Update()
    gROOT.GetListOfCanvases().Draw()
    outdir = outdir_base % year
    #checkdir(outdir)
    subdir = variable
    outdir += '/%s' % subdir
    #checkdir(outdir)
    outdir += '/%s' % sysdir
    #checkdir(outdir)
    fname = 'limits_%s2D_intersec_y_coord=%sGeV.png' % (sysdir,y_coord)
    c.SaveAs( '%s/%s' % (outdir,fname) ) 
#####################################################################
def plotLimits(path,verlist):
    print path
    data = Limits(path)
    for ver in verlist:
        print(ver)
        if   ver == '1D': drawPlot1D(data)
        elif ver == '2D': drawPlot2D(data)
        elif '1D_1param' in ver : drawPlot1D_1param(data,ver.replace('1D_1param-',''))
        elif '2D_intersection' in ver : drawPlot2D_intersection(data,ver.replace('2D_intersection-',''))
#####################################################################
def getargs():
    def directory(arg):
        if os.path.isdir(arg): return arg
        else: raise ValueError('Directories only')
    def version(arg):
        if ('1D' in arg or '1D_1param' in arg or '2D_intersection' in arg) or '2D' == arg:  return arg
        else:  return None
    parser = ArgumentParser(description="Plot limit information from specified directory")
    parser.add_argument("-d","--dir",help='Specify the directory to read limits from',action='store',nargs='+',type=directory,default=None,required=True)
    parser.add_argument("-v","--version",help='Specify the version of plot (1D or 2D or 1D_1param-$mchi(in this case replace $mchi with any of the available mass points)',action='store',type=version,default=None)
    try: arg = parser.parse_args()
    except:
        parser.print_help()
        exit()
    return parser.parse_args()
#####################################################################
if __name__ == "__main__":
    args = getargs()
    if args.dir == None:
        print "Please specify a director to run limits in."
        exit()
    if args.version == None: version = ('1D','2D')
    else:  version = (args.version,)
    for path in args.dir: plotLimits(path,version)
