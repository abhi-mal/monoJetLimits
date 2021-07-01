from ROOT import *

gSystem.Load("libHiggsAnalysisCombinedLimit.so")

dirmap = {"sr":"signal","ze":"Zee","zm":"Zmm","we":"Wen","wm":"Wmn","ga":"gjets"}
procmap = {"data":"data_obs","ZJets":"ZJets","WJets":"WJets","DYJets":"DYJets","GJets":"GJets","TTJets":"TTJets","DiBoson":"DiBoson","QCD":"QCD","axial":"axial","ggh":"ggh","vbf":"vbf","wh":"wh","zh":"zh","zprime":"zprime","dmsimp_scalar":"dmsimp_scalar","dmsimp_pscalar":"dmsimp_pscalar","dmsimp_t_0or1":"dmsimp_t_0or1","dmsimp_t_2":"dmsimp_t_2","ADD":"ADD","leptoquark":"leptoquark"}

yearlist = ["2016","2017","2018"]
lumimap = {"2016":35900,"2017":41486,"2018":59699}
catypes = ["monojet","monov","zprime"]
varmap = {
    "monojet":RooRealVar("recoil","recoil",250,1400),
    "zprime":RooRealVar("ChNemPtFrac","ChNemPtFrac",0.,1.0)
}

class SysRegion(TDirectoryFile):
    def __init__(self,region,syscat):
        TDirectoryFile.__init__(self,region,region+"_"+syscat.year)
        self.cat = syscat.cat
        self.year = syscat.year
        self.lumi = lumimap[self.year]
        sigtype_list = ["leptoquark","ADD","dmsimp_t_2","dmsimp_t_0or1","dmsimp_pscalar","dmsimp_scalar"]
        for key in syscat.tdir.GetListOfKeys():
            is_sig =0
            for sigtype in sigtype_list : 
               if sigtype in key.GetName(): is_sig =1 #if "dmsimp_scalar" in key.GetName(): #if "axial" in key.GetName():
            if is_sig ==1:
               #r,p = "signal","axial"
               r,p = "signal",key.GetName().replace("signal_","")
            else :
               #r,p = key.GetName().split("_")
                r = key.GetName().split("_")[0]
                p = key.GetName().replace(r+"_","")
            if dirmap[region] != r: continue
            if p == "sumofbkg": continue
#            if "axial" in p :  procname = p
            if "data" in p : procname = procmap[p]
            else:            procname = p
#            if "dmsimp_scalar" in p :  procname = p
#            else :             procname = procmap[p]
            process = syscat.tdir.Get(key.GetName()).Clone(procname)
            self.Add(process)
class SysCat:
    def __init__(self,tdir):
        self.tdir = tdir
        self.cat = next( cat for cat in catypes if cat in self.tdir.GetName() )
        self.year = next( year for year in yearlist if year in self.tdir.GetName() )
        self.lumi = lumimap[self.year]
        self.var = varmap[self.cat]
        self.varlist = RooArgList(self.var)
    def GetRegion(self,region):
        self.sysregion = SysRegion(region,self)
        return self.sysregion
    def GetName(self): return "%s_%s.sys.root" % (self.var.GetTitle(),self.year)
    def getSignalList(self): 
#axial 
#            signal_mass_map =  {
#                               #"Mchi":"Mphi"
#                               "1":["100","300","500","750","1000","1500","1750","2000","2250"],
#                               "10":["1750","2000"],
#                               "40":["100"],
#                               "100":["300","1750","2000"],
#                               "150":["500","1750","2000","2250"],
#                               "200":["100","500","1750","2000"],
#                               "300":["300","500","750","1000","1500","1750","2000","2250"],
#                               "400":["300","2000","2250"],
#                               "500":["500","1750"],
#                               "600":["750","1000","1500"]
#           }

#dmsimp_scalar and dmsimp_pseudoscalar(dmsimp_pscalar)
            signal_mass_map_sp ={
                              #"Mchi":"Mphi"
    			       '1':['10','50','100','200','300','350','400','450','500','600','700','800'],
		               '4':['10'],
			       '6':['10'],
			       '20':['50'],
			       '22':['50'],
			       '28':['50'],
			       '40':['100'],
			       '45':['100'],
			       '50':['500'],
			       '55':['100'],
			       '150':['500'],
			       '200':['500'],
			       '225':['500'],
			       '275':['500']
	    }
#dmsimp_tchannel_0or1 and dmsimp_tchannel_sum 
            signal_mass_map_t_sum ={ # signal_mass_map_t_0or1
                              #"Mchi":"Mphi"
                               '1':['100','300','500','750','1000','1200','1400','1600','1800','2000','2200'],
                               '200':['300','500','750','1000','1200','1400','1600','1800','2000','2200'],
                               '350':['1400','1600','1800','2000','2200'],
                               '400':['500','750','1000','1200'],
                               '500':['1400','1600','1800','2000'],
                               '550':['750'],
                               '600':['1000','1200'],
                               '650':['1400','1600','1800'],
                               '700':['750'],
                               '750':['1000'],
                               '800':['1400','1600'],
                               '900':['1000']
            }
#dmsimp_tchannel_2
            signal_mass_map_t_2 ={
                              #"Mchi":"Mphi"
                               '1':['100','300','500','750','1000','1200','1400','1600','1800','2000','2200'],
                               '75':['100'],
                               '200':['300','500','750','1000','1200','1400','1600','1800','2000','2200'],
                               '350':['1400','1600','1800','2000','2200'],
                               '400':['500','750','1000','1200'],
                               '500':['1400','1600','1800','2000'],
                               '550':['750'],
                               '600':['1000','1200'],
                               '650':['1400','1600','1800'],
                               '700':['750'],
                               '750':['1000'],
                               '800':['1400','1600'],
                               '900':['1000','1200']
            }
#ADD
            signal_mass_map_ADD ={
                             # extra_dim d : bulk mass MD
                              '2' : ['7', '8', '9', '10', '11', '12', '13', '14', '15'],
                              '3' : ['6', '7', '8', '9', '10', '11', '12', '13'],
                              '4' : ['5', '6', '7', '8', '9', '10', '11'],
                              '5' : ['5', '6', '7', '8', '9'],
                              '6' : ['5', '6', '7', '8', '9'],
                              '7' : ['4', '5', '6', '7', '8', '9']
                              #"bulk_mass MD":"ex_dim d"
#                               '4':['7'],
#                               '5':['4','5','6','7'],
#                               '6':['3','4','5','6','7'],
#                               '7':['2','3','4','5','6','7'],
#                               '8':['2','3','4','5','6','7'],
#                               '9':['2','3','4','5','6','7'],
#                               '10':['2','3','4'],
#                               '11':['2','3','4'],
#                               '12':['2','3'],
#                               '13':['2','3'],
#                               '14':['2'],
#                               '15':['2']
            }
#leptoquark
            signal_mass_map_lq ={
                              # Ylq : Mlq
#                               '0p01' : ['500'],
#                               '0p05' : ['500', '750'],  
#                               '0p1' : ['750', '1000'],
#                               '0p25' : ['750', '1000', '1250'],
#                               '0p5' : ['1000', '1250', '1500'], 
#                               '0p7' : ['1250', '1500', '1750'],
#                               '1' : ['1500', '1750', '2000'],
#                               '1p25' : ['1750', '2000', '2250'],
#                               '1p5' : ['2000', '2250', '2500']
                              #"Mlq":"Ylq"
#                               '500':['0p01','0p05'],
#                               '750':['0p05','0p1','0p25'],
#                               '1000':['0p1','0p25','0p5'],
#                               '1250':['0p25','0p5','0p7'],
#                               '1500':['0p5','0p7','1'],
#                               '1750':['0p7','1','1p25'],
#                               '2000':['1','1p25','1p5'],
#                               '2250':['1p25','1p5'],
#                               '2500':['1p5'],
                              #"Mlq":"Ylq"
                               '500':['0.01','0.05'],
                               '750':['0.05','0.1','0.25'],
                               '1000':['0.1','0.25','0.5'],
                               '1250':['0.25','0.5','0.7'],
                               '1500':['0.5','0.7','1'],
                               '1750':['0.7','1','1.25'],
                               '2000':['1','1.25','1.5'],
                               '2250':['1.25','1.5'],
                               '2500':['1.5'],
            }

            return signal_mass_map_t_sum


class SysFile(TFile):
    def __init__(self,*args,**kwargs):
        TFile.__init__(self,*args,**kwargs)
        self.categories = { category.GetName():SysCat(self.GetDirectory(category.GetName())) for category in self.GetListOfKeys() if self.GetDirectory(category.GetName()) }
        if not any(self.categories): self.categories = { self.GetName():SysCat(self) }
if __name__ == "__main__":
    import sys
    sysfile = SysFile(sys.argv[1])
    
    syscat = sysfile.categories["category_monojet_2017"]
    sysregion = syscat.GetRegion("sr")
    sysregion.Print()
