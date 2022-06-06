from collections import Counter
import pm4py

import networkx as nx

from const import XES_LIFECYCLE, XES_NAME, XES_CASE, START_TOK, END_TOK


def get_dfg_concurrency(log):
    dfgs = list()
    sa = dict()
    ea = dict()
    for case, events in log.groupby(XES_CASE):
        prev = None
        for index, row in events.iterrows():
            if row[XES_LIFECYCLE] == "start":
                if prev is not None:
                    dfgs.append((prev[XES_NAME], row[XES_NAME]))
                else:
                    if row[XES_NAME] not in sa:
                        sa[row[XES_NAME]] = 1
                    sa[row[XES_NAME]] += 1
            if row[XES_LIFECYCLE] == "complete":
                prev = row

        if prev[XES_NAME] not in ea:
            ea[prev[XES_NAME]] = 1
        ea[prev[XES_NAME]] += 1
    return dict(Counter(dfgs)), sa, ea


def get_dfg_classic(log):
    # dfg, sa, ea
    return pm4py.discover_directly_follows_graph(log)


def to_real_simple_graph(dfg, sa, ea):
    G = nx.DiGraph()
    for item in dfg.keys():
        G.add_nodes_from([
            (item[0]),
            (item[1]),
        ])
        G.add_edge(item[0], item[1], weight=1 / dfg[item])
    G.add_nodes_from([
        START_TOK
    ])
    G.add_nodes_from([
        END_TOK
    ])
    for s, c in sa.items():
        G.add_edge(START_TOK, s, weight=1 / c)
    for e, c in ea.items():
        G.add_edge(e, END_TOK, weight=1 / c)
    return G


def get_density(G):
    """
    d = \frac{m}{n(n-1)}
    Parameters
    ----------
    G
    Returns
    -------
    """
    return nx.density(G)