"""
Ranker for groups of events. After groups of events have been filtered, we can rank them according to different criteria
Based on 'how different' they are from other groups
Based on 'how clear they are' with respect to certain characteristics
Based on how they impact the abstraction result

We want to have multiple events per case, otherwise there is no abstraction
"""
import pandas as pd
from scipy.stats import wasserstein_distance
from const import *
from statistics import mean
from sklearn import preprocessing

class Ranker:

    def __init__(self, log, config, clust_to_props):
        self.config = config
        self.clust_to_props = clust_to_props
        self.log = log

    def create_ranking(self):
        self.rank_by_distinctness()
        self.rank_by_uniqueness()
        self.rank_by_abstraction_impact()


    def rank_by_uniqueness(self):
        for clustering in self.clust_to_props.keys():
            cat_lens = dict()
            num_ranges = dict()
            for clust, (categorical, categorical_set, numerical, time, categorical_per_case, numerical_per_case, time_per_case) in self.clust_to_props[clustering].items():
                for att, item_set in categorical_set.items():
                    if att == XES_NAME and len(item_set) == 1:
                        continue
                    cat_lens[str(clust)+"#"+att] = len(item_set)
                for att, item_set in numerical_per_case.items():
                    num_ranges[str(clust)+"#"+att] = mean(item_set)
            cat_lens = dict(sorted(cat_lens.items(), key=lambda item: item[1]))
            num_ranges = dict(sorted(num_ranges.items(), key=lambda item: item[1]))
            print(cat_lens)
            print(num_ranges)
            return

    def rank_by_distinctness(self):
        for clustering in self.clust_to_props.keys():
            cat_emd = dict()
            num_ranges = dict()
            for clust1, (categorical, categorical_set, numerical, time, categorical_per_case, numerical_per_case, time_per_case) in self.clust_to_props[clustering].items():

                for att in categorical_set.keys():
                    emd_sum = 0
                    for clust2, (categorical2, categorical_set2, numerical2, time2, categorical_per_case2, numerical_per_case2, time_per_case2) in self.clust_to_props[clustering].items():

                        ev_type_emd = wasserstein_distance(self.log.encoders[att].transform(list(categorical_set[att])),
                                                           self.log.encoders[att].transform(list(categorical_set2[att])))
                        emd_sum += ev_type_emd

                    cat_emd[str(clust1)+"#"+att] = emd_sum
                for att in numerical_per_case.keys():
                    emd_sum = 0
                    for clust2, (categorical2, categorical_set2, numerical2, time2, categorical_per_case2, numerical_per_case2, time_per_case2) in self.clust_to_props[clustering].items():

                        ev_type_emd = wasserstein_distance(numerical_per_case[att], numerical_per_case[att])
                        emd_sum += ev_type_emd

                    cat_emd[str(clust1)+"#"+att] = emd_sum

    def rank_by_abstraction_impact(self):
        pass
