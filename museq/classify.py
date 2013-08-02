#import os
import argparse
from datetime import datetime
import sys
from warnings import warn

mutationSeq_version="3.1.1"

parser = argparse.ArgumentParser(description='''classify a dataset''')
parser.add_argument("samples", nargs='*', help='''
                    A list of colon delimited sample names; normal:normal.bam
                    tumour:tumour.bam model:model.npz reference:reference.fasta''')
parser.add_argument("-o", "--out", default=None, help="save output to file")
parser.add_argument("-t", "--threshold", default=0.5, help="set threshold for positive call", type=float)
parser.add_argument("-i", "--interval", default=None, help="classify given chromosome[:start-end] range")
parser.add_argument("-a", "--all", default=None, help= "force to print out even if the position(s) does not satisfy the initial criteria for Somatic calls")
parser.add_argument("-f", "--positions_file", default=None, 
                    help="input a file containing a list of positions each of which in a separate line, e.g. chr1:12345\nchr2:23456")
parser.add_argument("--export", default=None, help="save exported feature vector")
parser.add_argument("-n", "--normalized", default=False, action="store_true",
                    help="If you want to test with normalized features(the number of features are also ifferent from non-deep)")
parser.add_argument("-v", "--verbose", action="store_true", default=False)
parser.add_argument("--version", action="version", version=mutationSeq_version)
parser.add_argument("-p", "--purity", default=70, help="pass sample purity to features")
parser.add_argument("-c", "--config", default=None,
                    help="Specify the path/to/metadata.config file used to add meta information to the output file")
args = parser.parse_args()

#==============================================================================
# check the input first
#==============================================================================
if len(args.samples) != 4:
    print >> sys.stderr, "bad input, should follow: 'classify.py normal:<normal.bam> tumour:<tumour.bam> reference:<ref.fasta> model:<model.npz> [--options]'"
    sys.exit(1)
    
if args.out is None:
    warn("--out is not specified, standard output is used to write the results")
    out = sys.stdout
else:
    out = open(args.out, 'w')

    
if args.config is None:
    warn("--config is not specified, no meta information used for the output VCF file")

if args.all is not None and args.all not in ("yes", "no"):
    print >> sys.stderr, "bad input for -a/--all, please specify only 'yes' or 'no'"
    sys.exit(1)

#==============================================================================
# import required modules here to save time when only checking version or help
#==============================================================================
print >> sys.stderr, datetime.now().strftime("%H:%M:%S") + " importing required modules"
import pybam
import numpy
#import scipy
import features
import Nfeatures
from collections import deque, defaultdict
from sklearn.ensemble import RandomForestClassifier
from math import log10
from string import Template
##

print >> sys.stderr, datetime.now().strftime("%H:%M:%S") + " mutationSeq_" + mutationSeq_version + " started"
deep_flag = 0
bases = ('A', 'C', 'G', 'T', 'N')
samples = {}
for sample in args.samples:
    samples[sample.split(':')[0]] = sample.split(':')[1]

#==============================================================================
# Add VCF format meta-information from metadata.cfg file to the output file
#==============================================================================
if args.config:
    try:
        cfg_file = open(args.config, 'r')
        tmp_file = ""
        for l in cfg_file:
            l = Template(l).substitute(DATETIME=datetime.now().strftime("%Y%m%d"),
                                       REFERENCE=samples["reference"],
                                       TUMOUR=samples["tumour"],
                                       NORMAL=samples["normal"],
				       THRESHOLD=args.threshold)
            tmp_file += l
        cfg_file.close()
        print >> out, tmp_file,
    except:
        warn("Failed to load metadata file")
        
#==============================================================================
# fit a model
#==============================================================================
try:
    npz = numpy.load(samples["model"])
except:
    print >> sys.stderr, "\tFailed to load model"
    sys.exit(1)

train = npz["arr_1"]
labels = npz["arr_2"]
model = RandomForestClassifier(random_state=0, n_estimators=1000, n_jobs=1, compute_importances=True)
print >> sys.stderr, datetime.now().strftime("%H:%M:%S") + " model fitting started"
model.fit(train, labels)

#==============================================================================
# extract feature
#==============================================================================
if not args.normalized:
    feature_set = features.feature_set
    coverage_features = features.coverage_features
    extra_features = (("xentropy", 0), ("SENTINEL", 0))
    version = features.version
    c = (float(30), float(30), float(70), float(0))
        
else:
    feature_set = Nfeatures.feature_set
    coverage_features = Nfeatures.coverage_features
    extra_features = (("xentropy", 0), ("SENTINEL", 0))
    version = Nfeatures.version
    c = (float(10000), float(10000), float(70), float(0))

#feature_set = features.feature_set
#coverage_features = features.coverage_features
#extra_features = (("xentropy", 0), ("SENTINEL", 0))


if "npz" in samples:
    try:
        npz = numpy.load(samples["npz"])
    except:
        print >> sys.stderr, "\tCould not import npz feature vector"
        sys.exit(1)
    coords = npz["arr_1"]
    batch = npz["arr_0"]
    strings = npz["arr_2"]
#    batch = batch[~numpy.isinf(batch).any(1)]
#    batch = batch[~numpy.isnan(batch).any(1)]
#    x = []
    b = []
    c = []
    s = []
    for coord, l, string in zip(coords, batch, strings):
        if numpy.isnan(l).any() or numpy.isinf(l).any():
            print >> sys.stderr, "\tnan/inf value"
            continue
        b.append(l)
        c.append(coord)
        s.append(string)
    batch = numpy.array(b)
    coords = c
    strings = s
#    print >> sys.stderr, "testing rows for bad features"
#    for line in batch:
#        if numpy.isinf(line).any() or numpy.isnan(line).any():
#            print >> sys.stderr, "chromosome has inf/nan value" 
#            for i in zip(line, feature_set + coverage_features + extra_features):
#                print >> sys.stderr, i
#            exit(1)
   
#    nl = []
#    for l in batch:
#        nl.append(numpy.nan_to_num(numpy.array(l)))
#    batch = numpy.array(nl)
    for coord, result, string in zip(coords, model.predict_proba(batch), strings):
        if result[1] >= args.threshold:
            print >> out, string[0], int(coord[0]), string[1], string[2], \
            int(coord[3]), string[3], int(coord[5]), string[4], int(coord[8]), \
            string[5], int(coord[10]), result[1], int(coord[-1])
    sys.exit(0)
    
if npz["arr_0"] != version:
    print >> sys.stderr, "\tmismatched feature set versions:",
    print >> sys.stderr, "\t" + str(npz["arr_0"]), "and", str(version)
    out.close()
    sys.exit(1)


die = False
if args.export:
    try:
        print >> sys.stderr, "\ttrying", args.export + ".npz"
        x = numpy.load(args.export + ".npz")
        die = True
    except:
        print >> sys.stderr, "\tcase not run"

if die:
    print >> sys.stderr, "\tthis case has already been run", args.export + ".npz"
    sys.exit(1)
#feature_set = features.feature_set
#coverage_features = features.coverage_features
#extra_features = (("xentropy", 0), ("SENTINEL", 0))
##
#==============================================================================
# read in bam files
#==============================================================================
try:
    n = pybam.Bam(samples["normal"])
except:
    print >> sys.stderr, "\tFailed to load normal"
    sys.exit(1)
try:
    t = pybam.Bam(samples["tumour"])
except:
    print >> sys.stderr, "\tFailed to load tumour"
    sys.exit(1)
try:
    f = pybam.Fasta(samples["reference"])
except:
    print >> sys.stderr, "\tFailed to load reference"
    sys.exit(1)

if args.verbose:
    print >> sys.stderr, "\tunsorted feature names"
    for importance, _feature in zip(model.feature_importances_, feature_set + coverage_features + extra_features):
        print >> sys.stderr, _feature[0], importance

    print >> sys.stderr, "\tsorted by importance:"
    for importance, _feature in sorted(zip(model.feature_importances_, feature_set + coverage_features + extra_features)):
        print >> sys.stderr, _feature[0], importance

#==============================================================================
# parse the positions or the file of list of positions
#==============================================================================
targets = None
l_pos = None
def parseTargetPos(poslist):
    target = poslist.split(':')[0]
    try:
        target = target.split('r')[1] #check if "chr" is used
    except:
        pass
    try:
        pos = poslist.split(':')[1]
        l_pos = int(pos.split('-')[0])
        try:
            u_pos = int(pos.split('-')[1])
        except:
            u_pos = int(l_pos) + 1
        return [target, l_pos, u_pos]
    except:
        return [target, None, None]

target_positions = defaultdict(list)

if args.interval:
    tmp_tp = parseTargetPos(args.interval)
    target_positions[tmp_tp[0]].append([tmp_tp[1], tmp_tp[2]])

elif args.positions_file:
    try:
        pos_file = open(args.positions_file, 'r')
        for l in pos_file.readlines():
            tmp_tp = parseTargetPos(l.strip())
            target_positions[tmp_tp[0]].append([tmp_tp[1], tmp_tp[2]])
        pos_file.close()
    except:
        print >> sys.stderr, "\tFailed to load the positions file from " + args.positions_file
        sys.exit(1)

else:
    targets = set(n.targets) & set(t.targets)

#==============================================================================
# run for each chromosome/position
#==============================================================================
coverage_data = (30, 30, int(args.purity), 1)
total_batch = []
total_coords = []
total_strings = []

#for chrom in targets:
for chrom in target_positions.keys(): # each key is a chromosomes
    for pos in range(len(target_positions[chrom])):
        l_pos = target_positions[chrom][pos][0]
        u_pos = target_positions[chrom][pos][1]
        if l_pos is None:
            print >> sys.stderr, datetime.now().strftime("%H:%M:%S") + \
            " reading chromosome " + chrom 
        else:
            print >> sys.stderr, datetime.now().strftime("%H:%M:%S") + \
            " reading chromosome " + chrom + " at positions " + str(l_pos) + " to " + str(u_pos)
    
        batch = []
        coords = []
        strings = []
        info_strs = []
        positions = deque([])
        
        try:
            f.load(chrom)
        except:
            message = "\treference does not have chromosome " + chrom
            warn(message)
#            print >> sys.stderr, 
            continue
        print >> sys.stderr, "\treading tumour data"

        if l_pos is None:
            g = t.vector(chrom, deep_flag)        
        else:
            g = t.vector(chrom, deep_flag, l_pos, u_pos)
            args.all = "yes"
    
        print >> sys.stderr, "\tnominating mutation positions in tumour"
        for tumour_data in g:
            position = tumour_data[0]
            ref_data = f.vector(int(position))
            #==============================================================================
            # Get tri-nucleotide context, seems not really an efficient way, but tested it is indeed readlly fast
            #==============================================================================
            if tumour_data[5][0] - tumour_data[ref_data[0] + 1][0] > 2 or args.all == "yes":
                try:
                    pre_refBase = f.vector(int(position) - 1)[0]
                except:
                    pre_refBase = 4
                try:
                    nxt_refBase = f.vector(int(position) + 1)[0]
                except:
                    nxt_refBase = 4
                tri_nucleotide = bases[pre_refBase] + bases[ref_data[0]] + bases[nxt_refBase]
                positions.append((position, tumour_data, ref_data, tri_nucleotide))
            #===============================================================================
        
        if len(positions) == 0:
            continue
        position, tumour_data, ref_data, tc = positions.popleft()
    
        print >> sys.stderr, "\treading normal"  
        if l_pos is None:
            g = n.vector(chrom, deep_flag)
        else:
            g = n.vector(chrom, deep_flag, l_pos, u_pos)
    
        skip = False
        for normal_data in g:
            while (position < normal_data[0]):
                if len(positions) == 0:
                    skip = True
                    break
                position, tumour_data, ref_data, tc = positions.popleft()
    
            if skip:
                break
            if normal_data[0] != position:
                continue
    
            features = []
            for _, feature in feature_set:
                features.append(feature(tumour_data, normal_data, ref_data))
    
            for _, feature in coverage_features:
                features.append(feature(tumour_data, normal_data, coverage_data))
            n_counts = (normal_data[1][1], normal_data[2][1], normal_data[3][1],
                        normal_data[4][1], normal_data[5][1])
            t_counts = (tumour_data[1][1], tumour_data[2][1], tumour_data[3][1],
                        tumour_data[4][1], tumour_data[5][1])
            features.append(n.xentropy(n_counts, t_counts))
            batch.append(features)
            coords.append((position, ref_data[0], normal_data[6], normal_data[normal_data[6] + 1][0],
                           normal_data[7], normal_data[normal_data[7] + 1][0], normal_data[11],
                           tumour_data[6], tumour_data[tumour_data[6] + 1][0], tumour_data[7],
                           tumour_data[tumour_data[7] + 1][0], tumour_data[11]))
            strings.append((chrom, bases[ref_data[0]], bases[normal_data[6]], bases[normal_data[7]], bases[tumour_data[6]], bases[tumour_data[7]], tc))       
    
            ## Find the ALT 
            if bases[ref_data[0]]==bases[tumour_data[6]]:
                alt = tumour_data[7]
            else:
                alt = tumour_data[6]        
    
            ## Generate the values of info fields in the vcf output
            if alt != ref_data[0]:
                info_strs.append((alt, int(tumour_data[ref_data[0] + 1][0]), int(tumour_data[alt + 1][0]), int(normal_data[ref_data[0] + 1][0]), int(normal_data[alt + 1][0])))
            else: # to take care of the non-somatic positions
                info_strs.append((alt, int(tumour_data[ref_data[0] + 1][0]), 0, int(normal_data[ref_data[0] + 1][0]), 0))
    
            if len(positions) == 0:
                break
        if args.export:
            total_batch += batch
            total_coords += coords
            total_strings += strings
        batch = numpy.array(batch)
    #    before = len(batch)
    
    
    #   print >> sys.stdeer, "testing rows for bad features"
    #    for line in batch:
    #        if numpy.isinf(line).any() or numpy.isnan(line).any():
    #            print >> sys.stderr, "chromosome has inf/nan value" 
    #            for i in zip(line, feature_set + coverage_features + extra_features):
    #                print >> sys.stderr, i
    #            exit(1)
    
    #    batch = batch[~numpy.isinf(batch).any(1)]
    #    batch = batch[~numpy.isnan(batch).any(1)]
    #    if len(batch) != before:
    #        print >> sys.stderr, "lost positions to infinite feature values:", before - len(batch)
        b = []
        c = []
        s = []
        i = []
    
    #==============================================================================
    # remove nan/inf values
    #==============================================================================
        print >> sys.stderr, datetime.now().strftime("%H:%M:%S") + " removing potential nan/inf values"
        for coord, l, string, info in zip(coords, batch, strings, info_strs):
            if numpy.isnan(l).any() or numpy.isinf(l).any():
                print >> sys.stderr, "\tnan/inf value at position "+ str(chrom) + ":" +  str(coord[0])
                continue
            b.append(l)
            c.append(coord)
            s.append(string)
            i.append(info)
        batch = numpy.array(b)
        coords = c
        strings = s
        info_strs = i
    
    #==============================================================================
    # filter and print the results to out
    #==============================================================================
        print >> sys.stderr, datetime.now().strftime("%H:%M:%S") + " filtering and printing results"
        for coord, result, string, info in zip(coords, model.predict_proba(batch), strings, info_strs):
            if result[1] >= args.threshold:
                try:
                    phred_qual = -10 * log10(1 - result[1])            
                except:
                    phred_qual = 99
                info_str = "PR=" + "%.3f" % result[1] + ";TR=" + str(info[1]) + ";TA=" + str(info[2]) + ";NR=" + str(info[3]) + ";NA=" + str(info[4]) + ";TC=" + string[6]
                print >> out, str(string[0]) + "\t" + str(coord[0]) + "\t" + "." + "\t" + string[1] + "\t" + bases[info[0]] + "\t"+ "%.2f" % phred_qual + "\t" + "PASS" + "\t" + info_str
            elif args.all == "yes":
                phred_qual = 0
                info_str = "PR=" + "%.3f" % result[1] + ";TR=" + str(info[1]) + ";TA=" + str(info[2]) + ";NR=" + str(info[3]) + ";NA=" + str(info[4]) + ";TC=" + string[6]
                print >> out, str(string[0]) + "\t" + str(coord[0]) + "\t" + "." + "\t" + string[1] + "\t" + bases[info[0]] + "\t"+ "%.2f" % phred_qual + "\t" + "FAIL" + "\t" + info_str
                
    #    print >> sys.stderr, "***No position has been nominated (does not satisfy initial criteria for Somatic calls )"
    total_batch = numpy.array(total_batch)
#==============================================================================
# Export the batch
#==============================================================================
if args.export:
    numpy.savez(args.export, total_batch, total_coords, total_strings)
print >> sys.stderr, datetime.now().strftime("%H:%M:%S") + " done."
    
