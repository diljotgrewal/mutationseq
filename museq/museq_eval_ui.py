'''
Created on Feb 21, 2014

@author: dgrewal
'''
#Extra Arguments (Rest of arguments are from classify)
#reference_files are required and contain the True/False labels
#plot_features_only: Do not classify, only generate boxplots (True/False Positives/Negatives boxplots are not generated)
#input_files(-i): Do not classify, only generate plots(All plots)
#If both -i and plot_features_only are specified then only boxplots are generated(with True/False Positives/Negatives)
#model: path to the model being used
#separate_plots: if this flag is set then the code generates separate boxplots for each of the space sep values(same plot for comma sep values)
#top_features: No of features to be plotted(Default is all features)
#out : paths of output vcf files(for each ref file)(If not provided, code saves vcf in current directory).
#out: If plotting only mode: path to the output folder(if more than one paths are there then picks the first path)
#log file is concatenated to museq log
#boxplot_labels: labels for the left most boxplot(len should be equal to no of plots)


import argparse
mutationSeq_version="4.2.0"

parser = argparse.ArgumentParser(prog='mutationSeq Classify and Validate', 
                                 description = '''Validates the mutationseq model'
                                 ' by plotting curves for a list of validated positions''')

##Arguments required for classification               
parser.add_argument("-a", "--all", 
                    default=False, action="store_true", 
                    help= '''force to print out even if the predicted probability of the 
                    candidate position(s) is(are) less than the specified threshld.''')

parser.add_argument("-b", "--buffer_size",
                    default="2G",
                    help='''specify max amount of memory usage''')

parser.add_argument("--coverage", 
                    default=4,
                    type=int,
                    help='''specify min depth (coverage) to be considered''')
                    
parser.add_argument("-d", "--deep", 
                    default=False, action="store_true", 
                    help='''deepseq data analysis''')
                    
parser.add_argument("-e" , "--export_features", 
                    default=None, 
                    help='''save exported feature vector to the specified path''')

parser.add_argument("-l", "--log_file",
                    default="mutationSeq_run.log",
                    help='''specify name or path of the log file''')
                    
parser.add_argument("--no_filter", 
                    default=False, action="store_true", 
                    help= '''force to print out even if the position(s) does(do) not satisfy 
                    the initial criteria for Somatic call''')
                    
parser.add_argument("-n", "--normalized", 
                    default=False, action="store_true",
                    help='''If you want to test with normalized features 
                    (the number of features are also different from non-deep)''')

parser.add_argument("--normal_variant",
                    default=25,
                    type=int,
                    help='''specify the max variant percentage in the normal bam file''')
                    
parser.add_argument("-p", "--purity", 
                    default=70, 
                    type=int,
                    help='''pass sample purity to features''')

parser.add_argument("-s", "--single",
                    default=False, action="store_true",
                    help='''single sample analysis''')
                    
parser.add_argument("-t", "--threshold", 
                    default=0.5, type=float,
                    help='''set threshold for positive call''') 

parser.add_argument("--tumour_variant",
                    default=2,
                    type=int,
                    help='''specify the min number of variants in the tumour bam file''')
                    
parser.add_argument("--features_only", 
                    default=False, action="store_true", 
                    help='''if true, only extracted features are exported''')

parser.add_argument("-v", "--verbose", 
                    action="store_true", default=False,
                    help='''verbose''')
                    
parser.add_argument("--version", 
                    action="version", version=mutationSeq_version)

parser.add_argument("-c", "--config", 
                    default=None, required=True,
                    help='''specify the path/to/metadata.config file used to add 
                            meta information to the output file''')

## MuseqEval arguments
parser.add_argument('-r','--reference_files',
                    nargs = '*', required = True,
                    help = 'path to the reference file. Format: pos file ')

parser.add_argument('-m','--model',
                    required = True,
                     help = 'Path to the model file')

parser.add_argument("--filter_threshold",
                    type = float,default = 0.8, 
                    help=''' Threshold probability considered positive''')

parser.add_argument('--ranked_features',
                    required = True, 
                    help ='Path to the list of important features;'
                    ' ranked by least important (line 1) to most important (last line)')

parser.add_argument('--top_features',
                    type=int, default=None, 
                    help='specifies the top X number of features to plot; default is 5')

parser.add_argument('--feature_db',
                    help = 'features_file (not needed, but will decrease runtime)'
                    'If not provided, the file will be generated during runtime in output folder')

parser.add_argument('--boxplot_labels',
                    nargs='+',
                    help='specifies the x-tick labels; default being the filename(s) specified in "--boxplot_inputs"')

parser.add_argument('--input_files','-i',
                    nargs = '*',default = None,
                    help = 'the input vcf files for museqeval (classifier won\'t run if provided)')

parser.add_argument('--plot_features_only',
                    action='store_true', default = False,
                    help = 'Plots feature distributions, Museq will not run in this mode')

parser.add_argument('--separate_plots',
                    action='store_true',default = False,
                    help = 'If set, then separate boxplots are generated for each set of space sep files'
                    )

parser.add_argument("-o", "--out", 
                    default=None, nargs = '*',
                    #required=True, 
                    help='''specify the path/to/out.vcf to save output to a file''')


args = parser.parse_args()