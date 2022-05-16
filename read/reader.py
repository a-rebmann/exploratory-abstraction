import os
import pickle
from const import *
import pandas as pd


def load_mppn_representations(config):
    try:
        with open(os.path.join(config.in_path, config.rep_name + '.pkl'), 'rb') as f:
            pd_events_fv = pickle.load(f)
            pd_events_fv[EVENT_POS_IN_CASE] = pd.NA
            pd_events_fv[EVENT_POS_IN_CASE] = pd_events_fv.groupby(XES_CASE)[XES_CASE].rank(method='first').astype(int)
            pd_events_fv[EVENT_POS_IN_CASE] = pd_events_fv[EVENT_POS_IN_CASE] - 1
            return pd_events_fv, True
    except FileNotFoundError:
        return None, False


def read_csv_log(config):
    pd_log = pd.read_csv(config.in_path + config.log_name, sep=",", engine="python")
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
        pd_log.rename(columns={config.att_names[XES_RESOURCE]: XES_RESOURCE}, inplace=True)
    if config.att_names[XES_ROLE] in pd_log.columns:
        pd_log.rename(columns={config.att_names[XES_ROLE]: XES_ROLE}, inplace=True)

    return pd_log


def load_result(config):
    try:
        with open(os.path.join(config.in_path, config.rep_name + '_result.pkl'), 'rb') as f:
            pickled_res = pickle.load(f)
            return pickled_res, True
    except FileNotFoundError:
        return None, False
