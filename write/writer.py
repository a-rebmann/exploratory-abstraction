import os
import pickle

from pm4py.objects.log.util import dataframe_utils
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.objects.log.exporter.xes import exporter as xes_exporter

from const import XES_TIME


def write_linkage_matrix(config, linkage_matrix):
    with open(os.path.join(config.out_path, config.log_name + 'linkage_matrix.pkl'), 'wb') as f:
        pickle.dump(linkage_matrix, f)


def write_result_to_disk(config, text_gen):
    with open(os.path.join(config.out_path,  str(config) + '_result.pkl'), 'wb') as f:
        pickle.dump(text_gen, f)
    f = open(os.path.join(config.out_path,  str(config) + '_text.txt'), "a")
    for clustering in text_gen.description.keys():
        for clust_num, clust_description in text_gen.description[clustering].items():
            f.write(str(clust_num) + "       " + clust_description + "\n" + "\n")
    f.close()


def export_log_as_xes(pd_log, config):
    #pd_log = dataframe_utils.convert_timestamp_columns_in_df(pd_log)
    pd_log = pd_log.sort_values(XES_TIME)
    event_log = log_converter.apply(pd_log)
    xes_exporter.apply(event_log, str(config)+'_abstracted.xes')


def serialize_clustering(clust, config):
    with open(os.path.join(config.out_path, str(config) + '_clusterer.pkl'), 'wb') as f:
        pickle.dump(clust, f)