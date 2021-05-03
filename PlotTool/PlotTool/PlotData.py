from ROOT import TH2D,TGraph
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
