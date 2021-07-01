from ROOT import *
import os
import sys
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("-f","--files",help="Files to merge into one sys file",nargs="+",type=TFile,required=True)
parser.add_argument("-c","--categories",help="Catergory name to give to each sys file in merged file",nargs="+",required=True)
parser.add_argument("-o","--output",help="Output filename",type=lambda fn:TFile(fn,"recreate"),required=True)

args = parser.parse_args()
for tfile,cat in zip(args.files,args.categories):
    args.output.cd()
    tdir = args.output.mkdir(cat)
    tdir.cd()
    for key in tfile.GetListOfKeys(): 
                     hist_to_write = tfile.Get(key.GetName())
                     hist_name = key.GetName().replace("QCDFake","QCD").replace("pseudoscalar","pscalar").replace("leptoquark","LQ")
                     # to make 0p05 etc in leptoquark case into float like 0.05
                     if "Ylq" in hist_name : 
                     	char_list = hist_name.split('_')
                        for i, my_str in enumerate(char_list):
                             if 'Ylq' in my_str : char_list[i] = my_str.replace('p','.')
                        hist_name = '_'.join(char_list)
                     hist_to_write.SetName(hist_name)
                     hist_to_write.Write()
    tdir.Write()
args.output.Close()

