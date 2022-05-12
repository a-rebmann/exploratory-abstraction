COUNT_TEMPLATE = "The group of events has {count} {name}. "

COUNT_RES_TEMPLATE = "The events are executed by {count} different {name}. "

DURATION_TEMPLATE = "The {dur} is {value} per case. "

DURATION_TEMPLATE_RANGE = "The {dur} of this group of events is between {min_value} and {max_value} per case. "


class TextGen:

    def __init__(self, pd_events_fv, clust_to_prop):
        self.pd_events_fv = pd_events_fv
        self.clus_to_prop = clust_to_prop
        self._description = {}

    def generate_descriptions_for_clusters(self):
        for clust, (
                event_types, resources, roles, cat_atts, num_atts, preceded_by, followed_by, min_dur_per_case,
                max_dur_per_case,
                avg_dur_per_case) in self.clus_to_prop.items():
            self.generate_description_for_cluster(clust, event_types, resources, roles, cat_atts, num_atts, preceded_by,
                                                  followed_by, min_dur_per_case, max_dur_per_case, avg_dur_per_case)
            #print(clust, event_types)

    def generate_description_for_cluster(self, clust, event_types, resources, roles, cat_atts, num_atts, preceded_by,
                                         followed_by, min_dur_per_case, max_dur_per_case, avg_dur_per_case):
        self._description[clust] = ""
        # TODO decide on which text to include in the description
        self.generate_event_types_text(clust, event_types)
        self.generate_resources_text(clust, resources)
        self.generate_roles_text(clust, roles)
        self.generate_cat_atts_text(clust, cat_atts)
        self.generate_num_atts_text(clust, num_atts)
        self.generate_preceeding_text(clust, preceded_by)
        self.generate_followed_by_text(clust, followed_by)
        self.generate_duration_text(clust, min_dur_per_case, max_dur_per_case, avg_dur_per_case)

    def generate_event_types_text(self, clust, event_types):
        text = COUNT_TEMPLATE.format(name="event types", count=len(event_types))
        self._description[clust] += text

    def generate_resources_text(self, clust, resources):
        text = COUNT_RES_TEMPLATE.format(name="resources", count=len(resources))
        self._description[clust] += text

    def generate_roles_text(self, clust, roles):
        pass

    def generate_cat_atts_text(self, clust, cat_atts):
        pass

    def generate_num_atts_text(self, clust, num_atts):
        pass

    def generate_preceeding_text(self, clust, preceded_by):
        pass

    def generate_followed_by_text(self, clust, followed_by):
        pass

    def generate_duration_text(self, clust, min_dur_per_case, max_dur_per_case, avg_dur_per_case):
        text = DURATION_TEMPLATE_RANGE.format(dur="duration", min_value=min_dur_per_case, max_value=max_dur_per_case)
        self._description[clust] += text
        text = DURATION_TEMPLATE.format(dur="average duration", value=avg_dur_per_case)
        self._description[clust] += text

    @property
    def description(self):
        return self._description
