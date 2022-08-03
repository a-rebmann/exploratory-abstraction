"""
Ranker for groups of events. After groups of events have been filtered, we can rank them according to different criteria
Based on 'how different' they are from other groups
Based on 'how clear they are' with respect to certain characteristics
Based on how they impact the abstraction result

We want to have multiple events per case, otherwise there is no abstraction
"""
import pandas as pd
from scipy.stats import wasserstein_distance

from abstraction.abstractor import Abstractor
from const import *
from statistics import mean, variance
from sklearn import preprocessing
from util.discovery import get_dfg_concurrency, to_real_simple_graph, get_dfg_classic, get_density


class PreSelector:

    def __init__(self, log, config, clust_to_props):
        self.config = config
        self.clust_to_props = clust_to_props
        self.log = log

    def create_ranking(self):
        distinct = self.rank_by_distinctness()
        #print(distinct)
        # distinct_per_case = self.rank_by_distinctness_per_case()
        # print(distinct_per_case)
        unique_per_case = self.rank_by_uniqueness_per_case()
        #print(unique_per_case)
        unique = self.rank_by_uniqueness()
        #print(unique)
        comp_red = dict()  # self.rank_by_abstraction_impact()

        clust_to_att_unique = dict()
        clust_to_att_distinct = dict()
        clust_to_att_unique_per_case = dict()

        won_unique_per_case = dict()
        for clustering, att_to_clust in unique_per_case.items():
            for clust in self.clust_to_props[clustering].keys():
                clust_to_att_unique_per_case[clust] = set()
                won_unique_per_case[clust] = 0
            for att, clust_to_score in att_to_clust[0].items():
                # print(clust_to_score)
                best_clust = min(clust_to_score, key=lambda x: clust_to_score[x])
                won_unique_per_case[best_clust] += 1
                clust_to_att_unique_per_case[best_clust].add(att)
            for att, clust_to_score in att_to_clust[1].items():
                # print(clust_to_score)
                best_clust = min(clust_to_score, key=lambda x: clust_to_score[x])
                won_unique_per_case[best_clust] += 1
                clust_to_att_unique_per_case[best_clust].add(att)
        print(won_unique_per_case)

        won_distinct = dict()
        for clustering, att_to_clust in distinct.items():
            for clust in self.clust_to_props[clustering].keys():
                clust_to_att_distinct[clust] = set()
                won_distinct[clust] = 0
            for att, clust_to_score in att_to_clust[0].items():
                # print(clust_to_score)
                best_clust = max(clust_to_score, key=lambda x: clust_to_score[x])
                if best_clust not in won_distinct:
                    won_distinct[best_clust] = 1
                    clust_to_att_distinct[best_clust] = set()
                won_distinct[best_clust] += 1
                clust_to_att_distinct[best_clust].add(att)
            for att, clust_to_score in att_to_clust[1].items():
                # print(clust_to_score)
                best_clust = max(clust_to_score, key=lambda x: clust_to_score[x])
                if best_clust not in won_distinct:
                    won_distinct[best_clust] = 1
                    clust_to_att_distinct[best_clust] = set()
                won_distinct[best_clust] += 1
                clust_to_att_distinct[best_clust].add(att)
        print(won_distinct)

        won_unique = dict()
        for clustering, att_to_clust in unique.items():
            for clust in self.clust_to_props[clustering].keys():
                clust_to_att_unique[clust] = set()
                won_unique[clust] = 0
            for att, clust_to_score in att_to_clust[0].items():
                #print(att, clust_to_score)
                #best_clust = min(clust_to_score, key=lambda x: clust_to_score[x])
                best_score = min(clust_to_score.values())
                for clusti, scori in clust_to_score.items():
                    if scori == best_score:
                        won_unique[clusti] += 1
                        clust_to_att_unique[clusti].add(att)
            for att, clust_to_score in att_to_clust[1].items():
                # print(clust_to_score)
                best_clust = min(clust_to_score, key=lambda x: clust_to_score[x])
                won_unique[best_clust] += 1
                clust_to_att_unique[best_clust].add(att)
        # print(won_unique)
        # print(clust_to_att_unique)
        # print(clust_to_att_distinct)
        # print(clust_to_att_unique_per_case)
        print("individual scores done")
        return clust_to_att_unique, clust_to_att_distinct, clust_to_att_unique_per_case, comp_red

    def rank_by_uniqueness(self):
        unique = {}
        for clustering in self.clust_to_props.keys():
            cat_lens = dict()
            num_ranges = dict()
            num_vars = dict()
            for clust, (
                    categorical, categorical_set, numerical, time, categorical_per_case, numerical_per_case,
                    time_per_case) in \
                    self.clust_to_props[clustering].items():

                for att, item_set in categorical_set.items():
                    if att in ["predecessors", "successors", "part_of_case", "event_pos", 'concept:instance'] or len(
                            self.log.pd_log[att].unique()) <= 2:
                        continue
                    if att == XES_NAME and len(item_set) == 1:
                        #print("skipping", att)
                        continue
                    if len(categorical_set[XES_NAME]) == len(self.log.pd_log[XES_NAME].unique()):
                        #print("skipping", att)
                        continue
                    if att not in cat_lens:
                        cat_lens[att] = dict()
                    cat_lens[att][clust] = len(item_set)
                for att, item_set in numerical.items():
                    if att in ["predecessors", "successors", "part_of_case", "event_pos", 'concept:instance'] or len(
                            self.log.pd_log[att].unique()) <= 2:
                        continue
                    if att not in num_vars:
                        num_vars[att] = dict()
                    if len(item_set) > 1:
                        num_vars[att][clust] = variance(item_set)
                    elif len(item_set) == 1:
                        num_vars[att][clust] = next(iter(item_set))

                # for att, item_set in numerical_per_case.items():
                #     if att not in num_ranges:
                #         num_ranges[att] = dict()
                #     if len(item_set) > 1:
                #         num_ranges[att][clust] = mean(item_set)
                #     elif len(item_set) == 1:
                #         num_ranges[att][clust] = next(iter(item_set))
                for att in cat_lens.keys():
                    cat_lens[att] = dict(sorted(cat_lens[att].items(), key=lambda item: item[1], reverse=True))
                for att in num_vars.keys():
                    num_vars[att] = dict(sorted(num_vars[att].items(), key=lambda item: item[1], reverse=True))
            unique[clustering] = (cat_lens, num_vars)
        return unique

    def rank_by_distinctness(self):
        distinct = {}
        for clustering in self.clust_to_props.keys():
            cat_emd = dict()
            num_ranges = dict()
            for clust1, (
                    categorical, categorical_set, numerical, time, categorical_per_case, numerical_per_case,
                    time_per_case) in \
                    self.clust_to_props[clustering].items():
                for att in categorical_set.keys():
                    if att in ["predecessors", "successors", "part_of_case", "event_pos", 'concept:instance'] or len(
                            self.log.pd_log[att].unique()) <= 2:
                        continue
                    if att == XES_NAME and len(categorical_set[att]) == 1:
                        #print("skipping", att)
                        continue

                    if att not in cat_emd:
                        cat_emd[att] = dict()
                    emd_sum = 0
                    for clust2, (
                            categorical2, categorical_set2, numerical2, time2, categorical_per_case2,
                            numerical_per_case2,
                            time_per_case2) in self.clust_to_props[clustering].items():
                        if len(categorical_set[att]) > 0 and len(categorical_set2[att]) > 0:
                            if att == PART_OF_CASE:
                                continue
                            if att == PREDECESSORS or att == SUCCESSORS:
                                ev_type_emd = wasserstein_distance(
                                    self.log.encoders[XES_NAME].transform(list(categorical_set[att])),
                                    self.log.encoders[XES_NAME].transform(list(categorical_set2[att])))
                            else:
                                ev_type_emd = wasserstein_distance(
                                    self.log.encoders[att].transform(list(categorical_set[att])),
                                    self.log.encoders[att].transform(list(categorical_set2[att])))
                            emd_sum += ev_type_emd
                    cat_emd[att][clust1] = emd_sum
                for att in numerical_per_case.keys():
                    if att in ["predecessors", "successors", "part_of_case", "event_pos", 'concept:instance'] or len(
                            self.log.pd_log[att].unique()) <= 2:
                        continue
                    if att in [XES_INST] or len(self.log.pd_log[att].unique()) <= 2:
                        continue
                    if att not in num_ranges:
                        num_ranges[att] = dict()
                    emd_sum = 0
                    for clust2, (
                            categorical2, categorical_set2, numerical2, time2, categorical_per_case2,
                            numerical_per_case2,
                            time_per_case2) in self.clust_to_props[clustering].items():
                        if len(numerical_per_case[att]) > 0 and len(numerical_per_case2[att]) > 0:
                            ev_type_emd = wasserstein_distance(numerical_per_case[att], numerical_per_case2[att])
                            emd_sum += ev_type_emd
                    num_ranges[att][clust1] = emd_sum
                for att in cat_emd.keys():
                    cat_emd[att] = dict(sorted(cat_emd[att].items(), key=lambda item: item[1], reverse=True))
                for att in num_ranges.keys():
                    num_ranges[att] = dict(sorted(num_ranges[att].items(), key=lambda item: item[1], reverse=True))
            distinct[clustering] = (cat_emd, num_ranges)
        return distinct

    def rank_by_uniqueness_per_case(self):
        unique = {}
        for clustering in self.clust_to_props.keys():
            cat_emd = dict()
            num_ranges = dict()
            for clust1, (
                    categorical, categorical_set, numerical, time, categorical_per_case, numerical_per_case,
                    time_per_case) in \
                    self.clust_to_props[clustering].items():

                for att in categorical_per_case.keys():
                    if att in [XES_NAME, "predecessors", "successors", "part_of_case", "event_pos", 'concept:instance'] or len(
                            self.log.pd_log[att].unique()) <= 2:
                        continue
                    if att not in cat_emd:
                        cat_emd[att] = dict()
                    dist = sum(categorical_per_case[att]) / len(categorical_per_case[att])
                    if att == XES_NAME and dist == 1:
                        #print("skipping", att)
                        continue
                    cat_emd[att][clust1] = dist
                for att in numerical_per_case.keys():
                    if att in ["predecessors", "successors", "part_of_case", "event_pos", 'concept:instance'] or len(
                            self.log.pd_log[att].unique()) <= 2:
                        continue
                    if att in [XES_INST] or len(self.log.pd_log[att].unique()) <= 2:
                        continue
                    if att not in num_ranges:
                        num_ranges[att] = dict()
                    dist = mean(numerical_per_case[att])
                    num_ranges[att][clust1] = dist
                for att in cat_emd.keys():
                    cat_emd[att] = dict(sorted(cat_emd[att].items(), key=lambda item: item[1], reverse=True))
                for att in num_ranges.keys():
                    num_ranges[att] = dict(sorted(num_ranges[att].items(), key=lambda item: item[1], reverse=True))
            unique[clustering] = (cat_emd, num_ranges)
        return unique
