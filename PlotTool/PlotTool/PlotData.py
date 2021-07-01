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
#    print('Calling interpolation')
#    final_exp_limits = do_interpolation(lim,mxlist,mvlist,method=3)
    final_exp_limits = [list(x) for x in zip(*lim)] 
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
# works for monotonous functions and no extrapolating for now
def Plot2D_intersection(data,y_coord,exclude=None):
#x = [0,1,2,3,4,5]
#y_list = [0,1,2,3,4,5]
    y_coord =float(y_coord)
    #line1 : (x,y_list), line2: y=y_coord 
    # get points to either side of intersection point
    def get_points(x_list,y_list,y_coord):
        print("x_list = %s"%x_list)
        if all(element == y_list[0] for element in y_list) : # all y_list elements are same, so we have a horizontal line
            return [y_list[0],-999]
        elif y_coord in y_list : 
            return [x_list[y_list.index(y_coord)],y_coord,-9]      
        else:     
            points_list = zip(x_list,y_list)
            points_list.append(('X',y_coord))
            print("points_list = %s"%points_list)
            points_list.sort(key=lambda x: float(x[-1])); print("sorted points_list = %s"%points_list)
            high_index = points_list.index(('X',y_coord)) ; low_index = high_index -1
            points_list.remove(('X',y_coord)) # get back the original list
            print(low_index); print(high_index)#; raw_input("ok?")
            if low_index <0 : low_index = 0 ; high_index = 1 # extrapolate below
            elif high_index == len(points_list): high_index = len(points_list) -1 ; low_index = high_index -1 # extrapolate above
            xlow = points_list[low_index][0] ; ylow = points_list[low_index][1]
            xhigh = points_list[high_index][0] ; yhigh = points_list[high_index][1]
            return [[xlow,ylow],[xhigh,yhigh],-99]

    def find_intersec(x_list,y_list,y_coord):
        points = get_points(x_list,y_list,y_coord)
        if (points[-1]==-999): print("all x values have the same y_coord = %s"%points[0]) ; return []
        elif (points[-1]==-9): print "Point already in list, x_coord= %s"%(points[0]); return points[0]
        else :
            point1 = points[0]; point2 =points[1]
            x_diff = point2[0] - point1[0]; y_diff = point2[1]-point1[1]
            if (x_diff==0) : "something is wrong! x_diff can't be 0 for this case"
            else:
                slope = y_diff/x_diff
                if (slope==0) :
                    X = max(point1[0],point2[0])
                    print "Slope is 0! Returning the higher value of x; change to lower if needed depending on the signal sample"
                else:
                    X = point1[0] + (1/slope)*(y_coord-point1[1])
                    print "The required x_coord = %s"%X; return X
    #mx = mass_param
    datalist = data.getDatalist(exclude)
    mxlist = sorted(datalist.keys(),key=int)
#    mxlist.remove(u'2500') # ignoring Mlq =2500 GeV for now
    limit_keys = ['exp0','obs','exp-1','exp-2','exp+1','exp+2']#,'exp1','exp2']
    limits = dict.fromkeys(mxlist)
    for k in limits.keys(): limits[k] = dict.fromkeys(limit_keys)
    for mx in mxlist: 
        #if float(mx) == 2500: continue # ignoring Mlq =2500 GeV for now
        xlist = []; ylist = []; ylist_obs = [] ; ylist_exp_minus1 = [] ; ylist_exp_minus2 = [] ; ylist_exp_plus1 = [] ; ylist_exp_plus2 = []
        for i,mv in enumerate( sorted(datalist[mx],key=float) ):
            if not 'exp0' in data.data[mx][mv]:
                    data.data[mx].pop(mv)
                    datalist[mx].remove(mv)
                    continue   
            x = float(mv); y = data.data[mx][mv]['exp0'];  y_obs = data.data[mx][mv]['obs']; y_exp_minus1 = data.data[mx][mv]['exp-1']; y_exp_minus2 = data.data[mx][mv]['exp-2']; y_exp_plus1 = data.data[mx][mv]['exp+1']; y_exp_plus2 = data.data[mx][mv]['exp+2']
            xlist.append(x); ylist.append(y); ylist_obs.append(y_obs); ylist_exp_minus1.append(y_exp_minus1); ylist_exp_minus2.append(y_exp_minus2); ylist_exp_plus1.append(y_exp_plus1); ylist_exp_plus2.append(y_exp_plus2)
        if not any(xlist) or not any(ylist): raise SystemExit("Error: Either specified mchi doesn't have any mphi or the available mphi don't have exp0 limit")
        #xlist = array('d',xlist)
        ylists= [ylist,ylist_obs,ylist_exp_minus1,ylist_exp_minus2,ylist_exp_plus1,ylist_exp_plus2]
        merged_list = list(zip(ylists,limit_keys))
        for i, my_list in enumerate(ylists):
            #my_list = array('d',my_list); print(type(my_list))
            my_tag = merged_list[i][-1]; print(my_tag)      
            limits[mx][my_tag] = find_intersec(xlist,my_list,y_coord)
            if limits[mx][my_tag] < 0: limits[mx][my_tag] = 0
            print("limits[%s][%s]=%s"%(mx,my_tag,limits[mx][my_tag])) #; raw_input("check")
    return limits
#####################################################
