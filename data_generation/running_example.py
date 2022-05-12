import os
from copy import deepcopy
import random

from pm4py.objects.log.importer.xes import importer as xes_importer

from pm4py.objects.log.exporter.xes import exporter as xes_exporter
from pm4py.objects.log.obj import EventLog

XES_NAME = "concept:name"
DISCO_NAME = "Activity"
LABEL = "label"
XES_LIFECYCLE = "lifecycle:transition"
XES_TIME = "time:timestamp"
XES_RESOURCE = "org:resource"
XES_ROLE = "org:role"

PATH = "../input/"
FILE = "running.xes"
LOW_LEVEL_FILE = "running_low.xes"


mapping = {
    "Recieve request": [["Receive chat message", "Create record in DB"], ["Receive email", "Create record in DB"]],
    "Inquire about missing information": [],
    "Check completeness": [["Open Document", "Close Document"]],
    "Recieve Inquiry": [["Receive chat message"], ["Receive email"]],
    "Examine request thoroughly": [["Open Document", "Close Document", "Query DB"]],
    "Examine request casually": [["Query DB"]],
    "Notify about status": [["Send email", "Send chat message"]],
    "Decide on acceptance": [["Update record in DB", "Query DB"]],
    "Communicate decision": [["Send email", "Send chat message"]],
    "Decision was communicated": [],
    "Notification sent": []


}

def create_low_level_log(log: EventLog):
    for trace in log:
        trace._list.sort(key=lambda x: x[XES_TIME], reverse=False)
        new_trace = list()
        for event in trace:
            #last_timestamp = ev
            if event[XES_LIFECYCLE] == "start":
                last_timestamp = event[XES_LIFECYCLE]
                continue
            if event[XES_NAME] not in mapping:
                continue
            if len(mapping[event[XES_NAME]]) == 0:
                continue
            low_level_events = random.choice(mapping[event[XES_NAME]])
            for low_level_event_name in low_level_events:
                low_level_event = deepcopy(event)
                low_level_event[LABEL] = low_level_event[XES_NAME]
                low_level_event[XES_NAME] = low_level_event_name
                low_level_event[DISCO_NAME] = low_level_event_name
                low_level_event[XES_ROLE] = low_level_event[XES_RESOURCE].split("-")[0]
                new_trace.append(low_level_event)
        trace._list = new_trace
    return log





if __name__ == "__main__":
    log: EventLog = xes_importer.apply(os.path.join(PATH, FILE))
    create_low_level_log(log)
    xes_exporter.apply(log, os.path.join(PATH, LOW_LEVEL_FILE))
