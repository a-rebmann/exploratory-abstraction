"""
Ranker for groups of events. After groups of events have been filtered, we can rank them according to different criteria
Based on 'how different' they are from other groups
Based on 'how clear they are' with respect to certain characteristics
Based on how they impact the abstraction result

We want to have multiple events per case, otherwise there is no abstraction
"""


class Ranker:

    def __init__(self, config, clust_to_props, pd_events_fv, pd_log,):
        self.config = config
        self.clust_to_props = clust_to_props
        self.pd_events_fv = pd_events_fv
        self.pd_log = pd_log


    def rank_by_uniqueness(self):
        pass

    def rank_by_distinctness(self):
        pass

    def rank_by_abstraction_impact(self):
        pass