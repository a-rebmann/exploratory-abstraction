from const import XES_CASE


class PatternAbstractor:

    def __init__(self, log, config, selection, props, clust_to_att_unique, clust_to_att_distinct, clust_to_att_unique_per_case):
        self.log = log
        self.config = config
        self.selection = selection
        self.props = props
        self.clust_to_att_unique = clust_to_att_unique
        self.clust_to_att_distinct = clust_to_att_distinct
        self.clust_to_att_unique_per_case = clust_to_att_unique_per_case

    def get_relevant_pattern(self):
        pattern_dict = dict()
        for sel in self.selection:
            pattern_dict[sel] = set()
            pattern_dict[sel].update(self.clust_to_att_unique_per_case[sel])
            pattern_dict[sel].update(self.clust_to_att_unique[sel])
        for sel, atts in pattern_dict.items():
            for att in atts:
                self.props[sel][att]

    def abstract(self):
        abstracted_log = self.log.pd_log.copy(deep=True)
        for case, events_per_case in self.log.pd_log.groupby(XES_CASE):
            pass
