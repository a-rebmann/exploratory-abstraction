import os
import pickle
from const import *
import pandas as pd


def load_mppn_representations(config):
    try:
        with open(os.path.join(config.in_path, config.log_name + '.pkl'), 'rb') as f:
            pd_events_fv = pickle.load(f)
            pd_events_fv[EVENT_POS_IN_CASE] = pd.NA
            pd_events_fv[EVENT_POS_IN_CASE] = pd_events_fv.groupby(XES_CASE)[XES_CASE].rank(method='first').astype(int)
            pd_events_fv[EVENT_POS_IN_CASE] = pd_events_fv[EVENT_POS_IN_CASE] - 1
            return pd_events_fv, True
    except FileNotFoundError:
        return None, False
