#!/usr/bin/env python
from ROOT import *
import os
import sys
from shutil import rmtree,copyfile
from argparse import ArgumentParser
from array import array
from fitting import *
import re
from subprocess import Popen,PIPE,STDOUT

def printProcs(procs,name):
    cutoff = 300 # seconds
    prompt = '{0:<22}'.format( '\rProcessing %i %s' % (len(procs),name) )
    total = len(procs)
    current = total
    out = '%s : %i%%' % (prompt,0)
    sys.stdout.write(out)
    sys.stdout.flush()
    while any(procs):
        IDlist = procs.keys()
        for ID in IDlist:
            if procs[ID].poll() != None:
                procs.pop(ID)
            # elif procs[ID].duration() > cutoff:
            #     procs[ID].terminate()
            #     procs.pop(ID)
        ##################################################
        if current != len(procs):
            current = len(procs)
            percent = 100 * (total - current)/float(total)
            out = '%s : %.3f%%' % (prompt,percent)
            sys.stdout.write(out)
            sys.stdout.flush()
    out = '%s : %.3f%%\n' % (prompt,100.)
    sys.stdout.write(out)
    sys.stdout.flush()
def makeMphiDir(mv,options,procmap=None):
    if mv == '10000': return
    cwd = os.getcwd()
    mvdir = 'Mphi_%s' % mv
    print '--Create %s Directory' % mvdir
    if not os.path.isdir(mvdir): os.mkdir(mvdir)
    os.chdir(mvdir)
    text2workspace = ['text2workspace.py','datacard','-m',mv,'-o','%s/workspace_Mphi%s.root' % (mvdir,mv)]
    with open('make_workspace.sh','w') as f:
        f.write('#!/bin/sh\n')
        f.write('cd ../\n')
        f.write(' '.join(text2workspace)+'\n')
    proc = Popen(['sh','make_workspace.sh'],stdout=PIPE,stderr=STDOUT);
    if procmap is not None: procmap[os.getcwd()] = proc
    else:                   proc.wait()
    os.chdir(cwd)
def makeMchiDir(mx,mvlist,yearlist,options,procmap=None):
    cwd = os.getcwd()
    regions = []
    for ch in ('sr','we','wm','ze','zm','ga'):
        for year in yearlist:
            regions.append('%s_%s' % (ch,year))
    mxdir = 'Mchi_%s' % mx
    print 'Creating %s Directory' % mxdir
    if not os.path.isdir(mxdir): os.mkdir(mxdir)
    os.chdir(mxdir)
    combine_cards = ['combineCards.py']
    for region in regions: combine_cards.append('%s=../datacard_%s' % (region,region))
    combine_cards += ['>','datacard']
    replace_mx = ['sed','-i',"'s/Mchi1/Mchi%s/g'" % mx,'datacard']
    replace_mv = ['sed','-i',"'s/Mphi1000/Mphi$MASS/g'",'datacard']
    with open('make_datacard.sh','w') as f:
        f.write('#!/bin/sh\n')
        f.write(' '.join(combine_cards)+'\n')
        f.write(' '.join(replace_mx)+'\n')
        f.write(' '.join(replace_mv)+'\n')
    proc = Popen(['sh','make_datacard.sh'],stdout=PIPE,stderr=STDOUT); proc.wait()
    procmap = {}
    for mv in mvlist: makeMphiDir(mv,options,procmap)
    printProcs(procmap,"Mphi Directories")
    os.chdir(cwd)
#####
def getargs():
    def sysfile(arg):
        tfile = TFile.Open(arg)
        valid = True
        if tfile.IsZombie(): raise ValueError()
        validdir = ['sr','we','ze','wm','zm']
        for dir in validdir:
            if tfile.GetDirectory(dir) != None: return arg
        raise ValueError()
    
    parser = ArgumentParser(description='Make workspace for generating limits based on input systematics file')
    parser.add_argument("-i","--input",help="Specify input systematics file to generate limits from",nargs="+",type=sysfile,default=None,required=True)
    parser.add_argument('-r','--reset',help="Remove directory before creating workspace if it is already there",action='store_true',default=False)
    parser.add_argument('--combined',help='Create combined limit cards',action='store_true',default=False)
    try: args = parser.parse_args()
    except ValueError as err:
        print err
        parser.print_help()
        exit()
    return args
#####
def yearWorkspace(sysfile,args):
    isScaled = os.path.isfile('signal_scaling.json')
    outfname = 'Limits/%s/workspace_%s.root' % (sysfile.variable.GetTitle(),sysfile.year)
    if isScaled: copyfile('signal_scaling.json','Limits/%s/signal_scaling.json' % sysfile.variable.GetTitle())
    if not os.path.isfile(outfname) or args.reset:
        return createWorkspace(sysfile,outfname=outfname,isScaled=isScaled)
####################
def makeWorkspace(input,args):
    print "Making Workspace for",input
    cwd = os.getcwd()
    sysfile = SysFile(os.path.abspath(input))
    sysdir = 'Limits/%s' % sysfile.variable.GetTitle()
    if not os.path.isdir(sysdir): os.mkdir(sysdir)
    ws = yearWorkspace(sysfile,args)
    sysfile.ws = ws
    sysdir = '%s/%s' % (sysdir,sysfile.GetName().split('/')[-1].replace(".root",""))
    sysfile.sysdir = sysdir
    if not os.path.isdir(sysdir): os.mkdir(sysdir)
    os.chdir(sysdir)
    createDatacards('../workspace_%s.root' % sysfile.year,sysfile.year)
    for mx,mvlist in sysfile.getSignalList().items(): makeMchiDir(mx,mvlist,[sysfile.year],args)
    os.chdir(cwd)
    return sysfile
####################
def combineWorkspace(sysfiles,args):
    print "Making Combined Workspace"
    cwd = os.getcwd()
    sysdir = sysfiles[0].sysdir.replace("%s.sys"%sysfiles[0].year,"Run2.sys")
    if not os.path.isdir(sysdir): os.mkdir(sysdir)
    for sysfile in sysfiles:
        for datacard in os.listdir(sysfile.sysdir):
            if "datacard" in datacard:
                print "Copying %s/%s" %(sysfile.sysdir,datacard)
                copyfile("%s/%s"%(sysfile.sysdir,datacard),"%s/%s"%(sysdir,datacard))
    os.chdir(sysdir)
    signalist = sysfile.getSignalList()
    for mx,mvlist in signalist.items(): makeMchiDir(mx,mvlist,[ sysfile.year for sysfile in sysfiles ],args)
    os.chdir(cwd)
####################
def main():
    if not os.path.isdir('Limits/'): os.mkdir('Limits/')
    args = getargs()

    sysfiles = [ makeWorkspace(input,args) for input in args.input ]
    if args.combined: combineWorkspace(sysfiles,args)
    return sysfiles
####################
if __name__ == "__main__": a=main()
    
