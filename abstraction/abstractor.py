from copy import deepcopy

from const import XES_NAME, XES_CASE, XES_TIME, XES_LIFECYCLE
from pm4py.objects.log.log import EventLog
import pandas as pd


def create_mapping_from_groups(log, groups, by_len=True):
    groups = list(groups)
    if by_len:
        groups.sort(key=len, reverse=True)
    mapping = {}
    unique_classes = set(log.unique_event_classes)
    for group in groups:
        set_group = set(group)
        if set_group.issubset(unique_classes) and not set_group.issubset(set(mapping.keys())):
            for ec in group:
                mapping[ec] = "#".join(group)
    for cls in unique_classes:
        if cls not in mapping.keys():
            mapping[cls] = cls
    return mapping


def apply_mapping_to_df(mapping, df, only_complete=False):
    df[XES_NAME] = df[XES_NAME].map(mapping)
    print(df[XES_NAME].unique())
    df = abstract_to_target(df, [XES_NAME], only_complete=only_complete)
    return df


def apply_interleaving_strategy(mapping, log, only_complete=False):
    for t in log:
        new_trace = list()
        for trace in split_into_subtraces(t):
            for event in trace:
                try:
                    event[XES_NAME] = mapping[event[XES_NAME]]
                except KeyError:
                    print(event[XES_NAME] + " is not a low-level event. Caught key error.")
            prev = None
            prev_event = None
            trace.sort(key=lambda x: x[XES_TIME], reverse=False)
            for event in trace:
                if event[XES_NAME] != prev:
                    if prev is not None:
                        prev_copy = deepcopy(prev_event)
                        prev_copy[XES_LIFECYCLE] = "complete"
                        new_trace.append(prev_copy)
                if not only_complete:
                    event[XES_LIFECYCLE] = "start"
                new_trace.append(event)
                prev = event[XES_NAME]
                prev_event = event
        new_trace.sort(key=lambda x: x[XES_TIME], reverse=False)
        trace._list = new_trace
    return log


def split_into_subtraces(trace):
    variants = []
    current = []
    current_names = []
    for event in trace:
        if event[XES_NAME] not in current_names:
            current.append(event)
            current_names.append(event[XES_NAME])
        else:
            variants.append(current)
            current = [event]
            current_names = [event[XES_NAME]]
    variants.append(current)
    return variants


def apply_parallel_strategy(mapping, log, only_complete=False):
    for t in log:
        new_trace = list()
        for trace in split_into_subtraces(t):
            for event in trace:
                try:
                    event[XES_NAME] = mapping[event[XES_NAME]]
                except KeyError:
                    print(event[XES_NAME] + " is not a low-level event. Caught key error.")
            trace.sort(key=lambda x: x[XES_TIME], reverse=False)
            if not only_complete:
                firsts = dict()
                for event in trace:
                    if event[XES_NAME] not in firsts.keys():
                        new_event = deepcopy(event)
                        new_event[XES_LIFECYCLE] = "start"
                        firsts[event[XES_NAME]] = new_event
                new_trace.extend(firsts.values())
            lasts = dict()
            reverse_iterator = reversed(trace)
            for event in reverse_iterator:
                if event[XES_NAME] not in lasts.keys():
                    new_event = deepcopy(event)
                    new_event[XES_LIFECYCLE] = "complete"
                    lasts[event[XES_NAME]] = new_event
            new_trace.extend(lasts.values())
        new_trace.sort(key=lambda x: x[XES_TIME], reverse=False)
        t._list = new_trace
    return log


def apply_mapping_to_log(mapping, log: EventLog, only_complete=False, interleaving=False):
    if interleaving:
        return apply_interleaving_strategy(mapping, log, only_complete)
    else:
        return apply_parallel_strategy(mapping, log, only_complete)


def abstract_to_target(df, targets, ignore=[], only_complete=False):
    grouped = df.sort_values(XES_CASE, ascending=True).groupby(XES_CASE)
    events = {XES_CASE: [], XES_NAME: [], XES_TIME: [], XES_LIFECYCLE: []}
    for case, case_group in grouped:
        recurse(events, case_group, case, [], targets, ignore=ignore, only_complete=only_complete)
    res_df = pd.DataFrame(events)
    res_df = res_df.sort_values([XES_CASE, XES_TIME], ascending=[True, True])
    return res_df


def recurse(events, df, case, prefixes, targets, ignore=[], only_complete=False):
    if len(targets) == 0:
        df = df.sort_values(XES_TIME, ascending=True)
        first = df.iloc[0]
        if len(df)>1:
            last = df.iloc[-1]
        else:
            last = first
        if not only_complete:
            events[XES_CASE].append(case)
            events[XES_NAME].append("_".join([prefixes[0]] + ['start']))
            events[XES_TIME].append(first[XES_TIME])
            events[XES_LIFECYCLE].append('start')
            for att in df.columns:
                if att not in events.keys():
                    events[att] = []
                if att in [XES_TIME, XES_NAME, XES_LIFECYCLE, XES_CASE]:
                    continue
                events[att].append(first[att])

        events[XES_CASE].append(case)
        events[XES_NAME].append("_".join([prefixes[0]] + ['complete']))
        events[XES_TIME].append(last[XES_TIME])
        events[XES_LIFECYCLE].append('complete')

        for att in df.columns:
            if att not in events.keys():
                events[att] = []
            if att in [XES_TIME, XES_NAME, XES_LIFECYCLE, XES_CASE]:
                continue
            events[att].append(last[att])

        return
    else:
        sp_groups = df.groupby(targets[0])
        for sp, sp_group in sp_groups:
            if sp in ignore:
                continue
            next_label = prefixes + [sp]
            new_targets = targets[1:]
            recurse(events, sp_group, case, next_label, new_targets, ignore=ignore, only_complete=only_complete)


class Abstractor:
    """
    applies the selected groups to the input event log to create an abstracted event log
    """

    def __init__(self):
        pass

