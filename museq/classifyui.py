# -*- coding: utf-8 -*-
"""
Created on Wed Oct 23 11:34:48 2013

@author: jtaghiyar
"""
import argparse

mutationSeq_version="4.0.0"

#==============================================================================
# make a UI 
#==============================================================================
parser = argparse.ArgumentParser(prog='mutationSeq', 
                                 description = '''mutationSeq: a feature-based classifier 
                                 for somatic mutation detection in
                                 tumour-normal paired sequencing data''')
## positional arguments                    
parser.add_argument("samples", 
                    nargs='*', 
                    help='''A list of colon delimited sample names; normal:normal.bam
                    tumour:tumour.bam model:model.npz reference:reference.fasta''')
                    
parser.add_argument("-a", "--all", 
                    default=None, choices=["no", "yes"], 
                    help= '''force to print out even if the position(s) does not satisfy 
                    the initial criteria for Somatic call''')

parser.add_argument("-d", "--deep", 
                    default=False, action="store_true", 
                    help='''for deepseq data''')
                    
parser.add_argument("-e" , "--export", 
                    default=None, 
                    help='''save exported feature vector to the specified path''')
                    
parser.add_argument("-n", "--normalized", 
                    default=False, action="store_true",
                    help='''If you want to test with normalized features 
                    (the number of features are also different from non-deep)''')
                    
parser.add_argument("-p", "--purity", 
                    default=70, 
                    help='''pass sample purity to features''')
                    
parser.add_argument("-v", "--verbose", 
                    action="store_true", default=False,
                    help='''verbose''')
                    
parser.add_argument("--version", 
                    action="version", version=mutationSeq_version)
                    
parser.add_argument("-t", "--threshold", 
                    default=0.5, type=float,
                    help='''set threshold for positive call''') 

parser.add_argument("-u", "--features_only", 
                    default=False, action="store_true", 
                    help='''if true, only extracted features are exported''')

## mandatory options                   
mandatory_options = parser.add_argument_group("required arguments")
mandatory_options.add_argument("-o", "--out", 
                               default=None, 
                               #required=True, 
                               help='''specify the path/to/out.vcf to save output to a file''')  
                               
mandatory_options.add_argument("-c", "--config", 
                               default=None, 
                               #required=True,
                               help='''specify the path/to/metadata.config file used to add 
                               meta information to the output file''')
                    
## mutually exclusive options
exgroup = parser.add_mutually_exclusive_group()
exgroup.add_argument("-f", "--positions_file", 
                     default=None, 
                     help='''input a file containing a list of positions each of which in
                     a separate line, e.g. chr1:12345\nchr2:23456''')                  
                     
exgroup.add_argument("-i", "--interval",
                     default=None,
                     help='''specify an interval "chr[:start-stop]"''')

args = parser.parse_args()
