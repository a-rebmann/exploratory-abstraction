import math

from const import *
import numpy as np


class PropertyComputer:

    def __init__(self, log, config, clust):
        self.log = log
        self._clust_to_prop = dict()
        self.config = config
        self.clust = clust

    def compute_props_for_clusters(self, consider_multi_clusterings=False):
        clustering_clust_to_props = dict()
        if consider_multi_clusterings and self.config.multi_clustering:
            for clustering_num in self.clust.pred_labels.keys():
                clustering_clust_to_props[clustering_num] = self.compute_props_for_clustering(clustering_num)
        else:
            clustering_clust_to_props = {0: self.compute_props_for_clustering(str(self.clust.elbow) if self.config.multi_clustering else "")}
        self._clust_to_prop = clustering_clust_to_props

    def compute_props_for_clustering(self, col):
        self.log.pd_log["Noise"] = False

        print("Start property computation")
        col_name = CLUST_COL + str(col) if self.config.multi_clustering else CLUST_COL
        self.log.pd_log[col_name] = self.log.pd_fv[col_name]
        clust_to_props = {}
        #print(self.log.pd_fv[col_name].unique())
        for clust, events in self.log.pd_fv.groupby(col_name):
            print(clust)
            for act_name, evs in events.groupby(XES_NAME_DF):
                print(act_name, len(evs))
            numerical = {att: [] for att in self.log.numerical_atts}
            categorical = {att: [] for att in self.log.categorical_atts}
            categorical[PREDECESSORS] = []
            categorical[SUCCESSORS] = []
            categorical[PART_OF_CASE] = []
            numerical[EVENT_POS_IN_CASE] = []

            time = {DAY_OF_WEEK: []}

            categorical_set = {att: set() for att in self.log.categorical_atts}
            categorical_set[PREDECESSORS] = set()
            categorical_set[SUCCESSORS] = set()
            categorical_set[PART_OF_CASE] = []

            time_set = {DAY_OF_WEEK: set()}

            numerical_per_case = {att: [] for att in self.log.numerical_atts}
            categorical_per_case = {att: [] for att in self.log.categorical_atts}
            categorical_per_case[XES_INST] = []

            time_per_case = {DURATION: []}
            idx = 0
            for case, events_per_case in events.groupby(XES_CASE):
                # print(case)
                if len(events_per_case) < 1:
                    continue

                indices = events_per_case[EVENT_POS_IN_CASE].tolist()
                try:
                    case_full = events_per_case.iloc[0][TRACE_DF].iloc[indices]
                except IndexError:
                    print(clust, indices, len(events_per_case.iloc[0][TRACE_DF]))
                    continue
                case_full_all = events_per_case.iloc[0][TRACE_DF]
                categorical_per_case[XES_INST].append(len(indices))
                #instances = self.split_instances(case_full)
                for att in self.log.categorical_atts:
                    if att in case_full.columns:
                        if "ID" not in att and not att[-2:] == "id":
                            categorical[att].extend(case_full[att].dropna().tolist())
                for att in self.log.numerical_atts:
                    if att in case_full.columns:
                        numerical[att].extend(case_full[att].astype(float).dropna().tolist())
                for att in self.log.categorical_atts:
                    if att in case_full.columns:
                        categorical_per_case[att].append(len(case_full[att].dropna().unique()))
                for att in self.log.numerical_atts:
                    if att in case_full.columns:
                        try:
                            num = case_full[att].astype(float).dropna().max() - case_full[att].astype(float).dropna().min()
                            if not math.isnan(num):
                                numerical_per_case[att].append(num)
                        except TypeError:
                            idx += 1
                            print(att, case_full[att].dropna().unique())

                time[DAY_OF_WEEK].extend(case_full[XES_TIME].apply(lambda x: x.weekday()).tolist())

                min_time = case_full[XES_TIME].min()
                max_time = case_full[XES_TIME].max()
                time_per_case[DURATION].append(max_time - min_time)

                min_idx = min(indices)
                max_idx = max(indices)

                if max_idx < len(case_full_all)/2:
                    categorical[PART_OF_CASE].append("first half")
                else:
                    categorical[PART_OF_CASE].append("second half")
                # check which types of events can happen before or after a group in a case
                if min_idx > 0:
                    categorical[PREDECESSORS].append(case_full_all.iloc[min_idx - 1][XES_NAME])
                if max_idx < len(case_full_all) - 1:
                    categorical[SUCCESSORS].append(case_full_all.iloc[max_idx + 1][XES_NAME])

                # positions within the trace
                numerical[EVENT_POS_IN_CASE].append(max(indices) - min(indices))

            # print(idx, "cases ar affected in clust", clust)
            time_per_case[DURATION] = self.remove_noise_numerical_per_case(time_per_case[DURATION])
            for att in categorical.keys():
                categorical_set[att] = set(categorical[att])
                if self.config.noise_tau > 0:
                    self.remove_noise(col_name, clust, categorical, categorical_set, att)

            clust_to_props[clust] = categorical, categorical_set, numerical, time, categorical_per_case, numerical_per_case, time_per_case
        #print(categorical_per_case)
        print("End property computation")

        return clust_to_props

    def remove_noise_numerical_per_case(self, num_list):
        num_list.sort()
        num_list = num_list[:int(len(num_list)*(1-self.config.noise_tau)-1)]
        return num_list


    def remove_noise(self, clust_col, clust, group_props, group_prop_set, att):
        #print(att)
        unique, counts = np.unique(group_props[att], return_counts=True)
        distribution_group = dict(zip(unique, counts))
        if att == PREDECESSORS or att == SUCCESSORS:
            unique, counts = np.unique(self.log.pd_log[XES_NAME].dropna(), return_counts=True)
        elif att == PART_OF_CASE:
            max_num_group = max(distribution_group.values())
            for et, cnt in distribution_group.items():
                if cnt < (self.config.noise_tau * max_num_group):
                    group_prop_set[att].remove(et)

            return
        else:
            unique, counts = np.unique(self.log.pd_log[att].dropna(), return_counts=True)
        distribution_log = dict(zip(unique, counts))
        if len(distribution_log.values()) > 0 and len(distribution_group.values()) > 0:
            max_num_group = max(distribution_group.values())
            max_num_log = max(distribution_log.values())

            for et, cnt in distribution_group.items():
                if (cnt / distribution_log[et]) < (self.config.noise_tau * (max_num_group / max_num_log)):
                    group_prop_set[att].remove(et)
                    if att in self.log.pd_log.columns:
                        self.log.pd_log.loc[(self.log.pd_log[att] >= et) & (self.log.pd_log[clust_col] == clust), "Noise"] = True

    @property
    def clust_to_prop(self):
        return self._clust_to_prop

    def compute_event_types(self):
        for clust, events in self.log.pd_fv.groupby(CLUST_COL):
            # print(events.columns)
            for row in events.itertuples():
                print(row[3].iloc[row[-2]][XES_NAME])
                break
            break

    # group-based per case
    # computes the duration of a group of events per case
    def compute_duration_per_case(self):
        pass

    # computes the directly-follows context of a group of events per case
    def compute_df_context(self):
        pass

    # computes the directly-follows context of a group of events per case
    def compute_ef_context(self):
        pass

    # computes the range of att values per case
    def compute_range_num_attributes_per_case(self):
        pass

    def compute_common_cat_attributes_per_case(self):
        pass

    # group-based per log
    # computes overall set of resources involved
    def compute_pool_of_resources(self):
        pass

    # computes aggregate of att values
    def compute_aggregated_num_attributes(self):
        pass

    def compute_common_cat_attributes(self):
        pass

    def compute_common_case_attributes(self):
        pass
