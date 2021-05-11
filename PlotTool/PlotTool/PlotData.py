from ROOT import TH2D,TGraph,TGraphAsymmErrors
from array import *
from interpolation import *

def Plot1D(data,exclude=None):
    datalist = data.getDatalist(exclude)
    mxlist = sorted(datalist.keys(),key=int)
    limits = {}
    for mx in mxlist:
        xlist = []; ylist = []
        for i,mv in enumerate( sorted(datalist[mx],key=float) ):
            if not 'exp0' in data.data[mx][mv]:
                data.data[mx].pop(mv)
                datalist[mx].remove(mv)
                continue
            x = float(mv); y = data.data[mx][mv]['exp0']
            xlist.append(x); ylist.append(y)
        if not any(xlist) or not any(ylist):
            mxlist.remove(mx)
            datalist.pop(mx)
            data.data.pop(mx)
            continue
        xlist = array('d',xlist); ylist = array('d',ylist);
        limits[mx] = TGraph(len(xlist),xlist,ylist)
    return limits,mxlist
#####################################################################
def Plot2D(data,exclude=None):
    datalist = data.getDatalist(exclude)
    mxlist = sorted(datalist.keys(),key=int)
    mvlist = []
    for mx in mxlist:
        for mv in sorted(datalist[mx],key=float):
            if mv not in mvlist: mvlist.append(mv); mvlist.sort(key=float)
    xbins = len(mvlist); ybins = len(mxlist)
    limit = TH2D("Expected Limits",";m_{med} (GeV);m_{#chi} (GeV)",xbins,0,xbins,ybins,0,ybins)
 #Cleanup
    for mx in mxlist:
        for mv in mvlist:
                 if mv not in data.data[mx]: continue 
                 if not 'exp0' in data.data[mx][mv]:
                    data.data[mx].pop(mv)
                    datalist[mx].remove(mv)
    lim = [[0 for q in range(len(mvlist))] for p in range(len(mxlist))]                       
    for p,mx in enumerate(mxlist):
        for q,mv in enumerate(mvlist):
            if mv not in data.data[mx]: lim[p][q] = 0
            else:                       lim[p][q] = data.data[mx][mv]['exp0']
#            limit.Fill(mv,mx,lim)
    print('Calling interpolation')
    final_exp_limits = do_interpolation(lim,mxlist,mvlist,method=3)
#    final_exp_limits = [list(x) for x in zip(*lim)] 
    for p,mx in enumerate(mxlist):
        for q,mv in enumerate(mvlist):
            limit.Fill(mv,mx,final_exp_limits[q][p])
    return limit,mxlist,mvlist
#######################################################################
def Plot1D_1param(data,mass_param,exclude=None):
    mx = mass_param
    datalist = data.getDatalist(exclude)
    mxlist = sorted(datalist.keys(),key=int)
    limit_keys = ['exp0','obs','exp-1','exp-2','exp+1','exp+2','exp1','exp2']
    limits = dict.fromkeys(limit_keys)
    if mx not in mxlist: raise SystemExit("Error: mchi not in the list of available mass points, try another point or do interpolation")
    xlist = []; ylist = []; ylist_obs = [] ; ylist_exp_minus1 = [] ; ylist_exp_minus2 = [] ; ylist_exp_plus1 = [] ; ylist_exp_plus2 = []
    for i,mv in enumerate( sorted(datalist[mx],key=float) ):
        if not 'exp0' in data.data[mx][mv]:
                data.data[mx].pop(mv)
                datalist[mx].remove(mv)
                continue   
        x = float(mv); y = data.data[mx][mv]['exp0'];  y_obs = data.data[mx][mv]['obs']; y_exp_minus1 = data.data[mx][mv]['exp-1']; y_exp_minus2 = data.data[mx][mv]['exp-2']; y_exp_plus1 = data.data[mx][mv]['exp+1']; y_exp_plus2 = data.data[mx][mv]['exp+2']
        xlist.append(x); ylist.append(y); ylist_obs.append(y_obs); ylist_exp_minus1.append(y_exp_minus1); ylist_exp_minus2.append(y_exp_minus2); ylist_exp_plus1.append(y_exp_plus1); ylist_exp_plus2.append(y_exp_plus2)
    if not any(xlist) or not any(ylist): raise SystemExit("Error: Either specified mchi doesn't have any mphi or the available mphi don't have exp0 limit")
    xlist = array('d',xlist)
    ylists= [ylist,ylist_obs,ylist_exp_minus1,ylist_exp_minus2,ylist_exp_plus1,ylist_exp_plus2]
    merged_list = list(zip(ylists,limit_keys))
    for i, my_list in enumerate(ylists):
        my_list = array('d',my_list); print(type(my_list))
        my_tag = merged_list[i][-1]; print(my_tag)
        limits[my_tag] = TGraph(len(xlist),xlist,my_list); 
    def get_band(up_y,down_y,name,xlist=xlist,central_y=array('d',ylist)):
        print("####") ; print(up_y) ; print("####")
        print("####") ; print(down_y) ; print("####")
        print("####") ; print(name) ; print("####")
        print("####") ; print(xlist) ; print("####")
        print("####") ; print(central_y) ; print("####")
        yvals_lo = [a_i - b_i for a_i,b_i in zip(central_y,down_y)]
        yvals_hi = [a_i - b_i for a_i,b_i in zip(up_y,central_y)]
        print("$$$$") ; print(yvals_lo) ; print("$$$$")
        print("$$$$") ; print(yvals_hi) ; print("$$$$")
        limits[name] = TGraphAsymmErrors(len(xlist),xlist,central_y,array('d', [0]),array('d', [0]),array('d', yvals_lo), array('d', yvals_hi)); limits[name].Sort()
    get_band(ylist_exp_plus1,ylist_exp_minus1,'exp1')    
    get_band(ylist_exp_plus2,ylist_exp_minus2,'exp2') 
    return limits
#####################################################################
