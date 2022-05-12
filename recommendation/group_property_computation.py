import datetime

from const import *
import numpy as np

DUR_PER_CASE = "duration per case"
NUM_RES_PER_CASE = "number of resources per case"
SET_RES = "resources"


class PropertyComputer:

    def __init__(self, pd_events_fv, config):
        self.pd_events_fv = pd_events_fv
        self._clust_to_prop = None
        self.config = config

    def compute_props_for_clusters(self):
        clust_to_props = {}
        for clust, events in self.pd_events_fv.groupby(CLUST_COL):
            event_types = []
            resources = []
            roles = []
            cat_atts = dict()
            num_atts = dict()
            preceded_by = []
            followed_by = []

            all_group_durs = []
            ev_per_case = []
            for case, events_per_case in events.groupby(XES_CASE):
                #print(case)
                indices = events_per_case[EVENT_POS_IN_CASE].tolist()
                #print(indices)
                ev_per_case.append(len(events_per_case))
                if len(events_per_case) < 1:
                    continue
                case_full = events_per_case.iloc[0][TRACE_DF].iloc[indices]
                case_full_all = events_per_case.iloc[0][TRACE_DF]
                min_time = case_full[XES_TIME].min()
                max_time = case_full[XES_TIME].max()
                all_group_durs.append(max_time - min_time)
                # add event / activity types
                event_types.extend(case_full[XES_NAME].tolist())
                # add resources
                resources.extend(case_full[XES_RESOURCE].tolist())
                # add role
                roles.extend(case_full[MOBIS_ROLE].tolist())
                min_idx = min(indices)
                max_idx = max(indices)
                # check which types of events can happen before or after a group in a case
                if min_idx > 0:
                    preceded_by.append(case_full_all.iloc[min_idx-1][XES_NAME])
                if max_idx < len(case_full_all)-1:
                    followed_by.append(case_full_all.iloc[max_idx+1][XES_NAME])


            # for row in events.itertuples():
            #     try:
            #         preceded_by.append(row[COL_INDEX_TRACE].iloc[row[COL_INDEX_POS] - 1][XES_NAME])
            #     except:
            #         pass
            #     try:
            #         followed_by.append(row[COL_INDEX_TRACE].iloc[row[COL_INDEX_POS] + 1][XES_NAME])
            #     except:
            #         pass
            min_dur_per_case = min(all_group_durs)
            max_dur_per_case = max(all_group_durs)
            avg_dur_per_case = sum(all_group_durs, datetime.timedelta(0)) / len(all_group_durs)

            event_types_set = set(event_types)
            resources_set = set(resources)
            roles_set = set(roles)
            unique, counts = np.unique(preceded_by, return_counts=True)
            distribution = dict(zip(unique, counts))
            print("preceded", distribution)
            unique, counts = np.unique(followed_by, return_counts=True)
            distribution = dict(zip(unique, counts))
            print("followed", distribution)
            preceded_by_set = set(preceded_by)
            followed_by_set = set(followed_by)

            # distribution of event types
            unique, counts = np.unique(event_types, return_counts=True)
            distribution = dict(zip(unique, counts))
            max_num = max(distribution.values())
            #print("*"*20, clust, "*"*20)
            for et, cnt in distribution.items():
                #print(et, cnt, max_num)
                if cnt < self.config.noise_tau * max_num:
                    event_types_set.remove(et)

            # distribution of resources
            unique, counts = np.unique(resources, return_counts=True)
            distribution = dict(zip(unique, counts))
            max_num = max(distribution.values())
            #print("*" * 20, clust, "*" * 20)
            for res, cnt in distribution.items():
                if cnt < self.config.noise_tau * max_num:
                    resources_set.remove(res)
                    #print(res, cnt)
            # distribution of roles
            unique, counts = np.unique(roles, return_counts=True)
            distribution = dict(zip(unique, counts))
            max_num = max(distribution.values())
            #print("*" * 20, clust, "*" * 20)
            for res, cnt in distribution.items():
                if cnt < self.config.noise_tau * max_num:
                    roles_set.remove(res)
                    #print(res, cnt)




            clust_to_props[clust] = event_types_set, resources_set, roles_set, cat_atts, num_atts, \
                                    preceded_by_set, followed_by_set, \
                                    min_dur_per_case, max_dur_per_case, avg_dur_per_case, ev_per_case

        self._clust_to_prop = clust_to_props

    @property
    def clust_to_prop(self):
        return self._clust_to_prop

    def compute_event_types(self):
        for clust, events in self.pd_events_fv.groupby(CLUST_COL):
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
