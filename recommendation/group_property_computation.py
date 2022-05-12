import datetime

from const import *
from statistics import mean

DUR_PER_CASE = "duration per case"
NUM_RES_PER_CASE = "number of resources per case"
SET_RES = "resources"


class PropertyComputer:

    def __init__(self, pd_events_fv):
        self.pd_events_fv = pd_events_fv
        self._clust_to_prop = None

    def compute_props_for_clusters(self):
        clust_to_props = {}
        for clust, events in self.pd_events_fv.groupby(CLUST_COL):
            event_types = set()
            resources = set()
            roles = set()
            cat_atts = dict()
            num_atts = dict()
            preceded_by = set()
            followed_by = set()

            all_group_durs = set()
            for case, events_per_case in events.groupby(XES_CASE):
                #print(case)
                indices = events_per_case[EVENT_POS_IN_CASE].tolist()
                #print(indices)
                if len(events_per_case) < 1:
                    continue
                case_full = events_per_case.iloc[0][TRACE_DF].iloc[indices]
                # else:
                #    case_full = events_per_case[TRACE_DF]
                #len(case_full)
                min_time = case_full[XES_TIME].min()
                max_time = case_full[XES_TIME].max()
                all_group_durs.add(max_time - min_time)
                # add event / activity types
                event_types.update(case_full[XES_NAME].tolist())
                # add resources
                resources.update(case_full[XES_RESOURCE].tolist())
                # add role
                roles.update(case_full[MOBIS_ROLE].tolist())
            for row in events.itertuples():
                try:
                    preceded_by.add(row[COL_INDEX_TRACE].iloc[row[COL_INDEX_POS] - 1][XES_NAME])
                except:
                    pass
                try:
                    followed_by.add(row[COL_INDEX_TRACE].iloc[row[COL_INDEX_POS] + 1][XES_NAME])
                except:
                    pass
            min_dur_per_case = min(all_group_durs)
            max_dur_per_case = max(all_group_durs)
            avg_dur_per_case = sum(all_group_durs, datetime.timedelta(0)) / len(all_group_durs)
            clust_to_props[clust] = event_types, resources, roles, cat_atts, num_atts, preceded_by, followed_by, min_dur_per_case, max_dur_per_case, avg_dur_per_case

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
