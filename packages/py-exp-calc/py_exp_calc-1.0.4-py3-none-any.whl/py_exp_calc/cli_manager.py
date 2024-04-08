import argparse
import os
import numpy as np
from importlib.resources import files
from scipy.spatial.distance import pdist, squareform

from py_report_html import Py_report_html
from py_exp_calc.exp_calc import *
from py_cmdtabs import CmdTabs

def based_0(string): return int(string) - 1
def list_based_0(string): return CmdTabs.parse_column_indices(",", string)
def double_split(string, sep1=";", sep2=","):
    return [sublst.split(sep2) for sublst in string.strip().split(sep1)]

## Common options
def add_common_options(parser):
    parser.add_argument("-i", "--input_file", dest="input",
        help="Path to input file")
    parser.add_argument("-o", "--output_file", dest="output",
        help="Path to input file")

def clusterize(args = None):
    if args == None: args = sys.argv[1:]
    parser = argparse.ArgumentParser(description="Get clusters")
    add_common_options(parser)
    parser.add_argument("-x", "--x_dim", dest="x_dim",
        help="Item list file for x axis")
    parser.add_argument("-y", "--y_dim", dest="y_dim",
        help="Item list file for y axis")
    parser.add_argument("-n", "--n_clusters", dest="n_clusters",
        help="N clusters for cut tree algorithm")
    parser.add_argument("-H", "--height", dest="height",
        help="Cut the tree with cut tree algorithm at specifc height")
    parser.add_argument("-c", "--clustering", dest="clustering", default='cut_tree',
        help="Method to identify clusters in hierarchical tree")        
    parser.add_argument("-r","--report", dest="report", default= False, action="store_true",
        help="Make report. Default false")

    opts =  vars(parser.parse_args(args))
    main_clusterize(opts)


def inference_analyzer(args = None):
    if args == None: args = sys.argv[1:]
    parser = argparse.ArgumentParser(description="Perform statistics form table")
    add_common_options(parser)
    parser.add_argument("-f", "--factor_indexes", dest="factor_indexes", type= list_based_0,
        help="Specify col number for factors")
    parser.add_argument("--alt_hyp", dest="alt_hyp", default= "two-sided",
        help="Select alternative hypotesis with optinos: two-sided, less, greater")
    parser.add_argument("-np","--no_parametric", dest="no_parametric", default= False, action='store_true', 
        help="Use this option if you want to specify not parametric analysis for all tests")
    parser.add_argument("--adj_pval", dest="adj_pval", default= None,
        help="Select multiple testing adjustment: bonferroni, sidak, holm-sidak, holm, simes-hochberg, hommel, fdr_bh, fdr_by, fdr_tsbh, fdr_tsbky")
    parser.add_argument("--header", dest = "header", default=False, action='store_true',
                        help="This is to check if you got a header")
    opts =  vars(parser.parse_args(args))
    main_inference_analyzer(opts)

def main_inference_analyzer(args):
    table = CmdTabs.load_input_data(args['input'])
    table = parse_table(table, header=args['header'], factor_index= args['factor_indexes'])
    stats = get_test(table, args['factor_indexes'], alternative = args['alt_hyp'], header = args["header"], adj_pval=args['adj_pval'], parametric = not args['no_parametric'])
    CmdTabs.write_output_data(stats, output_path=args['output'])

def main_clusterize(args):
    x_names = read_tabular_file(args['x_dim'], [0])
    x_names = [ x[0] for x in x_names ]
    y_names = read_tabular_file(args['y_dim'], [0])
    y_names = [ y[0] for y in y_names ]
    observation_matrix = np.loadtxt(args['input'])
    if len(observation_matrix.shape) == 1: # transform 1 Dimensional array to 2 Dimensional array
        observation_matrix = observation_matrix.reshape(observation_matrix.size, 1)
    clusters, cls_objects = get_hc_clusters(observation_matrix, identify_clusters=args['clustering'], item_list = x_names, n_clusters= args['n_clusters'])
    if args['report']:
        template = open(str(files('py_exp_calc.templates').joinpath('clustering.txt'))).read()
        container = {   'dist': squareform(cls_objects['dist_vector']), 
                        'link': cls_objects['link'], 
                        'raw_cls': cls_objects['cls'] }
        report = Py_report_html(container, 'Clustering')
        report.build(template)
        report.write(os.path.join(os.path.dirname(args["output"]), 'clustering.html'))
    write_dict(clusters, args['output'])

def read_tabular_file(input_file, cols):
    data = []
    with open(input_file) as f:
        for line in f:
            fields = line.rstrip().split("\t")
            data.append([fields[i] for i in cols])
    return data

def write_dict(dict, file):
    with open(file, 'w') as f:
        for k, values in dict.items():
            f.write(f"{k}\t{','.join(values)}\n")

def parse_table(table, header, factor_index):
    parsed_table = []
    if header:
        header = table.pop(0)
    for row in table:
        parsed_row = []
        for idx, el in enumerate(row):
            if not idx in factor_index:
                parsed_row.append(float(el))
            else:
                parsed_row.append(el)
        parsed_table.append(parsed_row)
    table = parsed_table
    if header:
        table.insert(0, header)
    return table