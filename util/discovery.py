from collections import Counter

from const import XES_LIFECYCLE, XES_NAME


def get_dfg_concurrency(log):
    dfgs = list()
    for t in log:
        prev = t[0]
        for i in range(1, len(t)):
            if t[i][XES_LIFECYCLE] == "start":
                dfgs.append((prev[XES_NAME], t[i][XES_NAME]))
            if t[i][XES_LIFECYCLE] == "complete":
                prev = t[i]
    return dict(Counter(dfgs))