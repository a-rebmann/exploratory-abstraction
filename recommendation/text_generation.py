from datetime import timedelta

COUNT_TEMPLATE = "The group of events has {count} {name}. "

COUNT_RES_TEMPLATE = "The events are executed by {count} different {name}. "

DURATION_TEMPLATE = "The {dur} is {value} per case. "

DURATION_TEMPLATE_RANGE = "The {dur} of this group of events is between {min_value} and {max_value} per case. "

EVENTS_PER_CASE = "There are {num} events per case {addition}. "


class TextGen:

    def __init__(self, pd_events_fv, pca, clust_to_prop, config):
        self.pd_events_fv = pd_events_fv
        self.clus_to_prop = clust_to_prop
        self._description = {}
        self.pca = pca
        self.config = config

    def generate_descriptions_for_clusters(self):
        for clustering in self.clus_to_prop.keys():
            self._description[clustering] = {}
            for clust, (
                    event_types, resources, roles, cat_atts, num_atts, preceded_by, followed_by, min_dur_per_case,
                    max_dur_per_case,
                    avg_dur_per_case, events_per_case) in self.clus_to_prop[clustering].items():
                self.generate_description_for_cluster(clustering, clust, event_types, resources, roles, cat_atts, num_atts, preceded_by,
                                                      followed_by, min_dur_per_case, max_dur_per_case, avg_dur_per_case, events_per_case)
                #print(clust, event_types)

    def generate_description_for_cluster(self, clustering, clust, event_types, resources, roles, cat_atts, num_atts, preceded_by,
                                         followed_by, min_dur_per_case, max_dur_per_case, avg_dur_per_case, events_per_case):
        self._description[clustering][clust] = ""
        # TODO decide on which text to include in the description

        self.generate_event_types_text(clustering, clust, event_types)
        self.generate_event_stats_text(clustering, clust, events_per_case)
        self.generate_resources_text(clustering, clust, resources)
        self.generate_roles_text(clustering, clust, roles)
        self.generate_cat_atts_text(clustering, clust, cat_atts)
        self.generate_num_atts_text(clustering, clust, num_atts)
        self.generate_preceeding_text(clustering, clust, preceded_by)
        self.generate_followed_by_text(clustering, clust, followed_by)
        self.generate_duration_text(clustering, clust, min_dur_per_case, max_dur_per_case, avg_dur_per_case)

    def generate_event_types_text(self, clustering, clust, event_types):
        text = COUNT_TEMPLATE.format(name="event types", count=len(event_types))
        self._description[clustering][clust] += text

    def generate_resources_text(self, clustering, clust, resources):
        text = COUNT_RES_TEMPLATE.format(name="resources", count=len(resources))
        self._description[clustering][clust] += text

    def generate_roles_text(self, clustering, clust, roles):
        text = COUNT_RES_TEMPLATE.format(name="roles", count=len(roles))
        self._description[clustering][clust] += text


    def generate_cat_atts_text(self, clustering, clust, cat_atts):
        pass

    def generate_num_atts_text(self, clustering, clust, num_atts):
        pass

    def generate_preceeding_text(self, clustering, clust, preceded_by):
        pass

    def generate_followed_by_text(self, clustering, clust, followed_by):
        pass

    def generate_duration_text(self, clustering, clust, min_dur_per_case, max_dur_per_case, avg_dur_per_case):
        if max_dur_per_case == timedelta(seconds=0):
            return
        text = DURATION_TEMPLATE_RANGE.format(dur="duration", min_value=min_dur_per_case, max_value=max_dur_per_case)
        self._description[clustering][clust] += text
        text = DURATION_TEMPLATE.format(dur="average duration", value=avg_dur_per_case)
        self._description[clustering][clust] += text

    @property
    def description(self):
        return self._description

    def generate_event_stats_text(self, clustering, clust, events_per_case):
        text = EVENTS_PER_CASE.format(addition="on average", num=int(sum(events_per_case)/len(events_per_case)))
        self._description[clustering][clust] += text
