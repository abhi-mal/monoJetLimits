from ROOT import TFile
import os

filedir = os.path.dirname( os.path.realpath(__file__) )

theoryfnames = {
    "wsr_to_zsr":["wz_unc.root"],
    "ga_to_sr":["gz_unc.root","all_trig_2017.root"],
    "ze_to_sr":["all_trig_2017.root"],
    "zm_to_sr":["all_trig_2017.root"],
    "we_to_sr":["all_trig_2017.root","wtow_pdf_sys.root","veto_sys.root"],
    "wm_to_sr":["all_trig_2017.root","wtow_pdf_sys.root","veto_sys.root"]
}

theoryfiles = {}
for filelist in theoryfnames.values():
    for fname in filelist:
        if fname in theoryfiles: continue
        theoryfiles[fname] = TFile("%s/%s"%(filedir,fname))
theoryhistos = {}
for key,tfile in theoryfiles.iteritems():
    fmap = {file:key}
    for hkey in tfile.GetListOfKeys():
        fmap[hkey.GetName()] = tfile.Get(hkey.GetName())
    theoryhistos[key]=fmap

filemap = {
    ("wz_unc.root","gz_unc.root"): {
        "QCD_Scale":"QCDScale",
        "QCD_Proc":"QCDProcess",
        "QCD_Shape":"QCDShape",
        "NNLO_EWK":"NNLOEWK",
        "NNLO_Sud":"Sudakov",
        "NNLO_Miss":"NNLOMiss",
        "QCD_EWK_Mix":"MIX",
        "PDF":"PDF"
    },
    ("all_trig_2017.root",): {
        "mettrig":"trig_sys"
    },
    ("wtow_pdf_sys.root",):{
        "PDF":"ratio"
    },
    ("veto_sys.root",):{
        "mettrig":"trig_sys",
        "eleveto":"eleveto",
        "muveto":"muveto",
        "tauveto":"tauveto",
    }
}

prefixmap = {
    "wz_unc.root":"ZW_",
    "gz_unc.root":"ZG_"
}
suffixmap = {
    "wz_unc.root":"_met",
    "gz_unc.root":"_met",
}

uncorrelatedmap = {
    "zsr":"1",
    "wsr":"2",
    "sr":"1",
    "ga":"2"
}

def getHistoMap(tfname,nuisance,histomap):
    filelist = theoryfnames[tfname]
    for fname in filelist:
        for filetuple,altmap in filemap.iteritems():
            if fname in filetuple and nuisance in altmap:
                return theoryhistos[fname],altmap[nuisance]
def getUpShift(histomap,hstype,ch):
    prefix = next( (prefix for fname,prefix in prefixmap.items() if fname == histomap[file]),"")
    suffix = next( (suffix for fname,suffix in suffixmap.items() if fname == histomap[file]),"")
    hstype = prefix + hstype + suffix
    for key,hs in histomap.iteritems():
        if key is file: continue
        if 'monov' in key: continue
        if key == hstype or key == hstype+'_up':
            return hs
def getDnShift(histomap,hstype,ch):
    prefix = next( (prefix for fname,prefix in prefixmap.items() if fname == histomap[file]),"")
    suffix = next( (suffix for fname,suffix in suffixmap.items() if fname == histomap[file]),"")
    hstype = prefix + hstype + suffix
    for key,hs in histomap.iteritems():
        if key is file: continue
        if 'monov' in key: continue
        if key == hstype+'_Down' or key == hstype+'_down':
            return hs
def getTFShift(tfname,nuisance,histomap=theoryhistos,ch='monojet'):
    if ch is 'monojet': ch = lambda string:"monov" not in string
    else: ch = lambda string:"monov" in string
    # print tfname,nuisance
    altTag = None
    for tag in uncorrelatedmap:
        if tag in nuisance:
            nuisance = nuisance.replace("_"+tag,"")
            altTag = uncorrelatedmap[tag]
    histomap,altname = getHistoMap(tfname,nuisance,histomap)
    if altTag: altname += altTag
    shiftUp = getUpShift(histomap,altname,ch)
    shiftDn = getDnShift(histomap,altname,ch)
    return shiftUp,shiftDn
if __name__ == "__main__":
    print getTFShift("wsr_to_zsr","NNLO_Sud_zsr")
    print getTFShift("wsr_to_zsr","NNLO_Sud_wsr")
    print getTFShift("ga_to_sr","QCD_EWK_Mix")
    print getTFShift("ga_to_sr","PDF")
    print getTFShift("we_to_sr","PDF")
    print getTFShift("ga_to_sr","mettrig")
