import datetime

from const import *
import numpy as np


class PropertyComputer:

    def __init__(self,log, config, clust):
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
        col_name = CLUST_COL + str(col) if self.config.multi_clustering else CLUST_COL
        clust_to_props = {}
        print(self.log.pd_fv[col_name].unique())
        for clust, events in self.log.pd_fv.groupby(col_name):
            numerical = {att: [] for att in self.log.numerical_atts}
            categorical = {att: [] for att in self.log.categorical_atts}
            time = {DAY_OF_WEEK: []}

            categorical_set = {att: set() for att in self.log.categorical_atts}
            time_set = {DAY_OF_WEEK: set()}

            numerical_per_case = {att: [] for att in self.log.numerical_atts}
            categorical_per_case = {att: [] for att in self.log.categorical_atts}
            categorical_per_case[PREDECESSORS] = []
            categorical_per_case[SUCCESSORS] = []
            time_per_case = {DURATION: []}

            for case, events_per_case in events.groupby(XES_CASE):
                # print(case)
                if len(events_per_case) < 1:
                    continue

                indices = events_per_case[EVENT_POS_IN_CASE].tolist()
                case_full = events_per_case.iloc[0][TRACE_DF].iloc[indices]
                case_full_all = events_per_case.iloc[0][TRACE_DF]

                for att in self.log.categorical_atts:
                    categorical[att].extend(case_full[att].tolist())
                for att in self.log.numerical_atts:
                    numerical[att].extend(case_full[att].tolist())
                for att in self.log.categorical_atts:
                    categorical_per_case[att].append(len(case_full[att]))
                for att in self.log.numerical_atts:
                    numerical_per_case[att].append(case_full[att].max() - case_full[att].min())

                time[DAY_OF_WEEK].extend(case_full[XES_TIME].apply(lambda x: x.weekday()).tolist())

                min_time = case_full[XES_TIME].min()
                max_time = case_full[XES_TIME].max()
                time_per_case[DURATION].append(max_time - min_time)

                min_idx = min(indices)
                max_idx = max(indices)
                # check which types of events can happen before or after a group in a case
                if min_idx > 0:
                    categorical_per_case[PREDECESSORS].append(case_full_all.iloc[min_idx - 1][XES_NAME])
                if max_idx < len(case_full_all) - 1:
                    categorical_per_case[SUCCESSORS].append(case_full_all.iloc[max_idx + 1][XES_NAME])

            if self.config.noise_tau > 0:
                for att in categorical.keys():
                    categorical_set[att] = set(categorical[att])
                    # distribution of event types
                    self.remove_noise(categorical, categorical_set, att)

            clust_to_props[clust] = categorical, categorical_set, numerical, time, categorical_per_case, numerical_per_case, time_per_case

        return clust_to_props

    def remove_noise(self, group_props, group_prop_set, att):
        print(att)
        unique, counts = np.unique(group_props[att], return_counts=True)
        distribution_group = dict(zip(unique, counts))

        unique, counts = np.unique(self.log.pd_log[att], return_counts=True)
        distribution_log = dict(zip(unique, counts))

        max_num_group = max(distribution_group.values())
        max_num_log = max(distribution_log.values())

        for et, cnt in distribution_group.items():
            if (cnt / distribution_log[et]) < (self.config.noise_tau * (max_num_group / max_num_log)):
                group_prop_set[att].remove(et)

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
