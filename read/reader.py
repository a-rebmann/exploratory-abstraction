import os
import pickle
from const import *
import pandas as pd
from pm4py.objects.log.importer.xes import importer
from pm4py.objects.conversion.log import converter


def load_mppn_representations(config):
    try:
        with open(os.path.join(config.in_path, config.rep_name + '.pkl'), 'rb') as f:
            pd_events_fv = pickle.load(f)
            pd_events_fv[EVENT_POS_IN_CASE] = pd.NA
            pd_events_fv[EVENT_POS_IN_CASE] = pd_events_fv.groupby(XES_CASE)[XES_CASE].rank(method='first').astype(int)
            pd_events_fv[EVENT_POS_IN_CASE] = pd_events_fv[EVENT_POS_IN_CASE] - 1
            return pd_events_fv, True
    except FileNotFoundError:
        print("not found")
        return None, False


def read_csv_log(config):
    if "Mobis" in config.log_name:
        decimal = ','
        pd_log = pd.read_csv(config.in_path + config.log_name, sep=";", engine="python", decimal=decimal)
    else:
        pd_log = pd.read_csv(config.in_path + config.log_name, sep=";", engine="python")
    """check if given column names exist in log and rename them"""
    must_have = [config.att_names[XES_CASE], config.att_names[XES_NAME], config.att_names[XES_TIME]]
    not_exist_str = " does not exist as column name"
    for e in must_have:
        if e not in pd_log.columns:
            raise ValueError(e + not_exist_str)
    pd_log.rename(columns={config.att_names[XES_CASE]: XES_CASE,
                           config.att_names[XES_TIME]: XES_TIME,
                           config.att_names[XES_NAME]: XES_NAME},
                  inplace=True)
    if config.att_names[XES_RESOURCE] in pd_log.columns:
        pd_log[config.att_names[XES_RESOURCE]] = pd_log[config.att_names[XES_RESOURCE]].fillna("None").astype(str)
        pd_log.rename(columns={config.att_names[XES_RESOURCE]: XES_RESOURCE}, inplace=True)
        #print(pd_log[XES_RESOURCE].unique())
        pass
    if config.att_names[XES_ROLE] in pd_log.columns:
        #pd_log.rename(columns={config.att_names[XES_ROLE]: XES_ROLE}, inplace=True)
        pd_log[config.att_names[XES_ROLE]] = pd_log[config.att_names[XES_ROLE]].fillna("None").astype(str)
        pass
    if "case:travel_start" in pd_log.columns:
        pd_log.rename(columns={"case:travel_start": "travel_start"}, inplace=True)
    if "case:travel_end" in pd_log.columns:
        pd_log.rename(columns={"case:travel_end": "travel_end"}, inplace=True)
    if XES_LIFECYCLE not in pd_log.columns:
        pd_log[XES_LIFECYCLE] = "start" #TODO not standrad but needed for interfacing with FVs
    if "isAccepted" in pd_log.columns:
        pd_log["isAccepted"] = pd_log["isAccepted"].astype(bool)
    return pd_log


def read_xes_log(config):
    log = importer.apply(os.path.join(config.in_path, config.log_name))
    pd_log = converter.apply(log, variant=converter.Variants.TO_DATA_FRAME)
    pd_log = pd_log.groupby(XES_CASE).head(65)
    if XES_LIFECYCLE not in pd_log.columns:
        pd_log[XES_LIFECYCLE] = "complete"
    return pd_log


def load_result(config):
    try:
        with open(os.path.join(config.out_path, str(config) + '_result.pkl'), 'rb') as f:
            pickled_res = pickle.load(f)
            return pickled_res, True
    except FileNotFoundError:
        return None, False


def deserialize_clustering(config):
    try:
        with open(os.path.join(config.out_path, str(config) + '_clusterer.pkl'), 'rb') as f:
            pickled_res = pickle.load(f)
            return pickled_res, True
    except FileNotFoundError:
        return None, False