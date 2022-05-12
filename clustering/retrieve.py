from scipy import spatial
import pandas as pd
import numpy as np
from const import *

"""
Retrieving events based on an event specified as a combination of case id and position
"""


def compute_similarities(pd_events_fv):
    pd_events_fv[SIMILAR_EVENTS] = pd.NA
    for idx, event in pd_events_fv.iterrows():
        pd_events_fv.at[idx, SIMILAR_EVENTS] = compute_retrieval_order(event["fv"], pd_events_fv["fv"])
    return pd_events_fv


def compute_retrieval_order(event_fv, all_fv):
    events_fv = np.array(event_fv.reshape(1, -1))
    all_fv = np.array(all_fv.tolist()).reshape(len(all_fv), event_fv.shape[-1])
    fv_distances = spatial.distance.cdist(events_fv, all_fv, metric="cosine").reshape(-1)
    return np.argsort(fv_distances).tolist()


def retrieve_most_similar_events(pd_event_fv, case_id, pos, top_n=5):
    query_event = pd_event_fv.goupby[XES_CASE][case_id][pos]#pd_event_fv[pd_event_fv[XES_CASE] == case_id]
    most_similar_cases_idx = query_event[SIMILAR_EVENTS].tolist()[0][1:top_n + 1]
    return most_similar_cases_idx
