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
    with open(os.path.join(config.out_path, config.log_name + '_result.pkl'), 'wb') as f:
        pickle.dump(text_gen, f)


def export_log_as_xes(pd_log, config):
    #pd_log = dataframe_utils.convert_timestamp_columns_in_df(pd_log)
    pd_log = pd_log.sort_values(XES_TIME)
    event_log = log_converter.apply(pd_log)
    xes_exporter.apply(event_log, config.out_path+config.log_name+'_abstracted.xes')
