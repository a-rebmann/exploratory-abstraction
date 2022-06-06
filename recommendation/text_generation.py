import math
from datetime import timedelta
from const import *

COUNT_TEMPLATE = "The group of events has {count} {name}. "

COUNT_RES_TEMPLATE = "The events are executed by {count} different {name}. "

DURATION_TEMPLATE = "The {dur} is {value} per case. "

DURATION_TEMPLATE_RANGE = "The {dur} of this group of events is between {min_value} and {max_value} per case. "

EVENTS_PER_CASE = "There are {num} events per case {addition}. "


class TextGen:

    def __init__(self, log, clust_to_prop, clust_to_atts_unique, clust_to_atts_distinct, clust_to_att_distinct_per_case, config):
        self.log = log
        self.clus_to_prop = clust_to_prop
        self.clust_to_atts_unique = clust_to_atts_unique
        self.clust_to_atts_distinct = clust_to_atts_distinct
        self.clust_to_att_distinct_per_case = clust_to_att_distinct_per_case
        self._description = {}
        self.config = config

    def generate_descriptions_for_clusters(self):
        for clustering in self.clus_to_prop.keys():
            self._description[clustering] = {}
            for clust, (
            categorical, categorical_set, numerical, time, categorical_per_case, numerical_per_case, time_per_case) in \
            self.clus_to_prop[clustering].items():
                self.generate_description_for_cluster(clustering, clust, categorical, categorical_set, numerical, time,
                                                      categorical_per_case, numerical_per_case, time_per_case)
                # print(clust, event_types)

    def generate_description_for_cluster(self, clustering, clust, categorical, categorical_set, numerical, time,
                                         categorical_per_case, numerical_per_case, time_per_case):
        self._description[clustering][clust] = ""
        # TODO decide on which text to include in the description

        self.generate_event_types_text(clustering, clust, categorical_set[XES_NAME])
        self.generate_event_stats_text(clustering, clust, categorical_per_case[XES_NAME])

        # Group-wide properties
        if XES_RESOURCE in self.log.categorical_atts:
            self.generate_resources_text(clustering, clust, categorical_set[XES_RESOURCE])
        if XES_ROLE in self.log.categorical_atts:
            self.generate_roles_text(clustering, clust, categorical_set[self.config.att_names[XES_ROLE]])
        self.generate_cat_atts_text(clustering, clust, categorical_set)
        self.generate_num_atts_text(clustering, clust, numerical)
        self.generate_preceeding_text(clustering, clust, categorical[PREDECESSORS])
        self.generate_followed_by_text(clustering, clust, categorical[SUCCESSORS])
        self.generate_position_in_cases(clustering, clust, numerical[EVENT_POS_IN_CASE])

        # Per case properties: duration, resources, roles, cat values, value ranges,...
        self.generate_duration_text(clustering, clust, time_per_case)
        if XES_RESOURCE in self.log.categorical_atts:
            self.generate_resources_text_per_case(clustering, clust, categorical_per_case[XES_RESOURCE])
        if XES_ROLE in self.log.categorical_atts:
            self.generate_roles_text_per_case(clustering, clust, categorical_per_case[self.config.att_names[XES_ROLE]])
        self.generate_cat_atts_text_per_case(clustering, clust, categorical_per_case)
        self.generate_num_atts_text_per_case(clustering, clust, numerical_per_case)

    def generate_event_types_text(self, clustering, clust, event_types):
        text = COUNT_TEMPLATE.format(name="event types", count=len(event_types))
        if len(event_types) < 6:
            if len(event_types) == 1:
                text = 'All events are of the ' + str(event_types).replace("{", "").replace("}", "") + ' type. '
            else:
                text += 'These are ' + str(event_types).replace("{", "").replace("}", "") + ". "
        self._description[clustering][clust] += text

    def generate_resources_text(self, clustering, clust, resources):
        text = COUNT_RES_TEMPLATE.format(name="resources", count=len(resources))
        if XES_RESOURCE not in self.clust_to_atts_unique[clust] and XES_RESOURCE not in self.clust_to_att_distinct_per_case[clust]:
            return
        if 'None' in resources:
            resources.remove('None')
        if len(resources) < 5:
            if len(resources) == 1:
                text = 'All events are executed by ' + str(resources).replace("{", "").replace("}", "") + '. '
            else:
                text += 'These are ' + str(resources).replace("{", "").replace("}", "") + ". "
        self._description[clustering][clust] += text

    def generate_roles_text(self, clustering, clust, roles):
        text = COUNT_RES_TEMPLATE.format(name="roles", count=len(roles))
        if XES_ROLE not in self.clust_to_atts_unique[clust] and XES_RESOURCE not in self.clust_to_att_distinct_per_case[clust]:
            return
        if 'None' in roles:
            roles.remove('None')
        if len(roles) < 3:
            if len(roles) == 1:
                text = 'All events are executed by the ' + str(roles).replace("{", "").replace("}", "") + ' role. '
            else:
                text += 'These are ' + str(roles).replace("{", "").replace("}", "") + ". "
        self._description[clustering][clust] += text

    def generate_cat_atts_text(self, clustering, clust, cat_atts):
        text = ""
        for att, items in cat_atts.items():
            if att not in self.clust_to_atts_unique[clust] and att not in self.clust_to_att_distinct_per_case[clust] and att not in self.clust_to_atts_distinct[clust]:
                continue
            if len(items) == 0:
                continue
            if att in [XES_NAME, XES_RESOURCE, XES_ROLE]:
                continue
            if att == PART_OF_CASE:
                if len(items) == 1:
                    text += "All events occur in the " + str(next(iter(items))) + " of their case."
            else:
                text += "There are the following values for " + att + " in this group: " + str(items).replace("{",
                                                                                                              "").replace(
                    "}", "") + ". "
        self._description[clustering][clust] += text

    def generate_num_atts_text(self, clustering, clust, num_atts):
        text = ""
        for att, items in num_atts.items():
            if att not in self.clust_to_att_distinct_per_case[clust] and att not in self.clust_to_atts_distinct[clust]:
                continue
            if len(items) == 0:
                continue
            if att in [EVENT_POS_IN_CASE]:
                continue
            # TODO add generic text
            text += att + " has the following value range in this group: " + str(min(items)).replace("{",
                                                                                               "").replace(
                "}", "") + " - " + str(max(items)).replace("{",
                                                                                               "").replace(
                "}", "") + ". "
        self._description[clustering][clust] += text

    def generate_resources_text_per_case(self, clustering, clust, resources):
        if XES_RESOURCE not in self.clust_to_att_distinct_per_case[clust] and XES_RESOURCE not in self.clust_to_atts_unique[clust]:
            return
        if 'None' in resources:
            resources.remove('None')
        if all(x == 1 for x in resources):
            text = 'Per case, all events are executed by the same resource. '
        else:
            rounded_avg = int(sum(resources) / len(resources))
            text = 'Per case, events are executed by ' + str(rounded_avg) + ' different resources on average. '
        self._description[clustering][clust] += text

    def generate_roles_text_per_case(self, clustering, clust, roles):
        if XES_ROLE not in self.clust_to_att_distinct_per_case[clust] and XES_ROLE not in self.clust_to_atts_unique[clust]:
            return
        if 'None' in roles:
            roles.remove('None')
        if all(x == 1 for x in roles):
            text = 'Per case, all events are executed by the same role. '
        else:
            rounded_avg = int(sum(roles) / len(roles))
            text = 'Per case, events are executed by ' + str(rounded_avg) + ' different roles on average. '
        self._description[clustering][clust] += text

    def generate_cat_atts_text_per_case(self, clustering, clust, cat_atts):
        text = ""
        for att, items in cat_atts.items():
            print(clust, att)
            if att not in self.clust_to_att_distinct_per_case[clust] and att not in self.clust_to_atts_unique[clust]:
                continue
            if len(items) == 0 or "case:" in att:
                continue
            if att in [XES_NAME, XES_RESOURCE, XES_ROLE]:
                continue
            rounded_avg = int(sum(items) / len(items))
            text += "There are " + str(rounded_avg) + " different values on average for " + att + " in this group, per " \
                                                                                                  "case. "
        self._description[clustering][clust] += text

    def generate_num_atts_text_per_case(self, clustering, clust, num_atts):
        text = ""
        for att, items in num_atts.items():

            if att not in self.clust_to_att_distinct_per_case[clust]:
                continue
            if len(items) == 0 or "case:" in att:
                continue
            rounded_avg = sum(items) / len(items)
            if math.isnan(rounded_avg):
                continue
            text = 'Per case, events have an average value range of ' + "{:.2f}".format(rounded_avg) + " for " + att + ". "
        self._description[clustering][clust] += text

    def generate_preceeding_text(self, clustering, clust, preceded_by):
        text = ""
        if PREDECESSORS not in self.clust_to_atts_distinct[clust] and XES_ROLE not in self.clust_to_atts_unique[clust]:
            return
        if len(preceded_by) == 1:
            text += "The group is always preceded by " + str(preceded_by).replace("{",
                                                                                                          "").replace(
                "}", "") + ". "
        self._description[clustering][clust] += text

    def generate_followed_by_text(self, clustering, clust, followed_by):
        text = ""
        if SUCCESSORS not in self.clust_to_atts_distinct[clust] and SUCCESSORS not in self.clust_to_atts_unique[clust]:
            return
        if len(followed_by) == 1:
            text += "The group is always followed by " + str(followed_by).replace("{",
                                                                                  "").replace(
                "}", "") + ". "
        self._description[clustering][clust] += text

    def generate_duration_text(self, clustering, clust, time_per_case):
        max_dur = max(time_per_case[DURATION])
        min_dur = min(time_per_case[DURATION])
        if max(time_per_case[DURATION]) == timedelta(seconds=0):
            return
        # min_dur_per_case = (str(min_dur_per_case.days) + " days " if min_dur_per_case.days > 0 else "") + \
        #                    (str(min_dur_per_case.hours) + " hours " if min_dur_per_case.seconds//3600 > 0 else "") + \
        #                    (str(min_dur_per_case.minutes) + " minutes " if min_dur_per_case.minutes > 0 else "") +\
        #                    (str(min_dur_per_case.seconds) + " seconds"if min_dur_per_case.seconds > 0 else "")
        # max_dur_per_case = str(max_dur_per_case.days) + " days " + str(max_dur_per_case.hours) + " hours " + str(
        #     max_dur_per_case.minutes) + " minutes " + str(max_dur_per_case.seconds) + " seconds"
        if min(time_per_case[DURATION]) == timedelta(seconds=0):
            min_dur = "O seconds"

        text = DURATION_TEMPLATE_RANGE.format(dur="duration", min_value=min_dur, max_value=max_dur)
        self._description[clustering][clust] += text
        # text = DURATION_TEMPLATE.format(dur="average duration", value=avg_dur_per_case) #TODO average
        # self._description[clustering][clust] += text

    @property
    def description(self):
        return self._description

    def generate_event_stats_text(self, clustering, clust, events_per_case):
        num = int(sum(events_per_case) / len(events_per_case))
        if num > 1:
            text = EVENTS_PER_CASE.format(addition="on average", num=int(sum(events_per_case) / len(events_per_case)))
        else:
            text = "There is one event per case. "
        self._description[clustering][clust] += text

    def generate_position_in_cases(self, clustering, clust, positional_ranges):
        text = ""
        if not len(positional_ranges) == 0:
            text += "Within individual cases, the events of this group occur in positions between " + str(min(positional_ranges)) + " and " + str(max(positional_ranges)) + ". "
            self._description[clustering][clust] += text
        self._description[clustering][clust] += text
