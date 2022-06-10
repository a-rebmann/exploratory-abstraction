from copy import deepcopy

from const import XES_NAME, XES_CASE, XES_TIME, XES_LIFECYCLE
from pm4py.objects.log.log import EventLog
import pandas as pd


# TODO how to handle multiple instances of the same activity within a trace? TODO build pojection and abstraction
#  functions (retain only events per case, replace these with only one start and one complete event
class Abstractor:
    """
    applies the selected groups to the input event log to create an abstracted event log
    """

    def __init__(self, log, config, selection, group_indicator_col):
        self.log = log
        self.config = config
        self.selection = selection
        self.group_indicator_col = group_indicator_col

    def apply_abstraction(self):
        print(len(self.log.pd_log), len(self.log.pd_fv))
        # COpy the original log
        abstracted_log = self.log.pd_log.copy(deep=True)
        if XES_LIFECYCLE not in abstracted_log.columns:
            abstracted_log[XES_LIFECYCLE] = 'complete'
        abstracted_log[XES_NAME+'_old'] = abstracted_log[XES_NAME]
        abstracted_log[self.group_indicator_col] = self.log.pd_fv[self.group_indicator_col]
        #abstracted_log[XES_NAME] = abstracted_log[self.group_indicator_col]
        # create a column that contains new activity labels for the final log
        abstracted_log.loc[abstracted_log[self.group_indicator_col].isin(self.selection), XES_NAME] = \
        abstracted_log.loc[abstracted_log[self.group_indicator_col].isin(self.selection)][self.group_indicator_col]

        # create a column that contains new activity labels for the group by
        abstracted_log.loc[~abstracted_log[self.group_indicator_col].isin(self.selection), self.group_indicator_col] = \
            abstracted_log.loc[~abstracted_log[self.group_indicator_col].isin(self.selection)][XES_NAME].astype(str) + \
        abstracted_log.loc[~abstracted_log[self.group_indicator_col].isin(self.selection)][XES_TIME].astype(str)

        abstracted_log.to_csv(self.config.out_path + self.config.log_name + "_d.csv")

        g = abstracted_log.groupby([XES_CASE, self.group_indicator_col])
        abstracted_log.loc[g[XES_LIFECYCLE].head(1).index, XES_LIFECYCLE] = 'start'
        abstracted_log.loc[g[XES_LIFECYCLE].tail(1).index, XES_LIFECYCLE] = 'complete'
        # in each case retain only the first and last event of each group
        abstracted_log = (pd.concat([g.head(1), g.tail(1)]).drop_duplicates().reset_index(drop=True)) #.sort_values(XES_TIME) sorting might cause the complete events before start events if duration=0
        return abstracted_log


