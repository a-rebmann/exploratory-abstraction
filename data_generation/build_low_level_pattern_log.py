import random
from collections import deque

from pm4py.objects.log.util import sorting
from pm4py.objects.petri_net.obj import PetriNet, Marking # Objects for constructing a Petri net system.
from pm4py.objects.petri_net.utils import petri_utils
import datetime
from copy import copy
from enum import Enum
from random import choice

from pm4py.objects.log import obj as log_instance
from pm4py.objects.petri_net import semantics
from pm4py.objects.petri_net.obj import PetriNet
from pm4py.util import xes_constants

from data_generation.augment_logs import sample_from_normal


def create_composed_pn():
    net = PetriNet("runningexample")
    pass


def exclusion_receive(net, source, target, name=""):
    t_1 = PetriNet.Transition(name, "Receive chat message")
    t_2 = PetriNet.Transition(name, "Receive Email")
    net.transitions.add(t_1)
    petri_utils.add_arc_from_to(source, t_1, net)
    petri_utils.add_arc_from_to(t_1, target, net)
    net.transitions.add(t_2)
    petri_utils.add_arc_from_to(source, t_2, net)
    petri_utils.add_arc_from_to(t_2, target, net)


def exclusion_receive_db(net, source, target, name=""):
    t_1 = PetriNet.Transition(name, "Receive chat message")
    t_2 = PetriNet.Transition(name, "Receive Email")
    t_3 = PetriNet.Transition(name, "Create DB record")
    p_1 = PetriNet.Place(name)
    net.places.add(p_1)
    net.transitions.add(t_1)
    petri_utils.add_arc_from_to(source, t_1, net)
    petri_utils.add_arc_from_to(t_1, p_1, net)
    net.transitions.add(t_2)
    petri_utils.add_arc_from_to(source, t_2, net)
    petri_utils.add_arc_from_to(t_2, p_1, net)
    net.transitions.add(t_3)
    petri_utils.add_arc_from_to(p_1, t_3, net)
    petri_utils.add_arc_from_to(t_3, target, net)


def exclusion_send(net, source, target, name=""):
    t_1 = PetriNet.Transition(name, "Send chat message")
    t_2 = PetriNet.Transition(name, "Send Email")
    net.transitions.add(t_1)
    petri_utils.add_arc_from_to(source, t_1, net)
    petri_utils.add_arc_from_to(t_1, target, net)
    net.transitions.add(t_2)
    petri_utils.add_arc_from_to(source, t_2, net)
    petri_utils.add_arc_from_to(t_2, target, net)


def thorough(net, source, target, name=""):
    t_1 = PetriNet.Transition(name, "Open document")
    t_2 = PetriNet.Transition(name, "Access DB")
    #t_3 = PetriNet.Transition("silent_111", None)
    t_4 = PetriNet.Transition(name, "Close document")
    p_1 = PetriNet.Place(name)
    p_2 = PetriNet.Place(name)
    #p_3 = PetriNet.Place("pth_3")
    net.places.add(p_1)
    net.places.add(p_2)
    #net.places.add(p_3)
    net.transitions.add(t_1)
    net.transitions.add(t_2)
    #net.transitions.add(t_3)
    net.transitions.add(t_4)
    petri_utils.add_arc_from_to(source, t_1, net)
    petri_utils.add_arc_from_to(t_1, p_1, net)
    petri_utils.add_arc_from_to(p_1, t_2, net)
    petri_utils.add_arc_from_to(t_2, p_2, net)
    #petri_utils.add_arc_from_to(p_2, t_3, net)
    #petri_utils.add_arc_from_to(t_3, p_1, net)
    petri_utils.add_arc_from_to(p_2, t_4, net)
    petri_utils.add_arc_from_to(t_4, target, net)


def casual(net, source, target, name=""):
    t_1 = PetriNet.Transition(name, "Access DB")
    net.transitions.add(t_1)
    petri_utils.add_arc_from_to(source, t_1, net)
    petri_utils.add_arc_from_to(t_1, target, net)

def decide(net, source, target, name=""):
    t_1 = PetriNet.Transition(name, "Access DB")
    t_4 = PetriNet.Transition(name, "Update DB")
    p_1 = PetriNet.Place(name)
    net.places.add(p_1)
    net.transitions.add(t_1)
    net.transitions.add(t_4)
    petri_utils.add_arc_from_to(source, t_1, net)
    petri_utils.add_arc_from_to(t_1, p_1, net)
    petri_utils.add_arc_from_to(p_1, t_4, net)
    petri_utils.add_arc_from_to(t_4, target, net)


def apply_playout(net, initial_marking, resources_per_act, durations_per_act, no_traces=100, max_trace_length=100,
                  case_id_key=xes_constants.DEFAULT_TRACEID_KEY,
                  activity_key=xes_constants.DEFAULT_NAME_KEY, timestamp_key=xes_constants.DEFAULT_TIMESTAMP_KEY,
                  resource_key=xes_constants.DEFAULT_RESOURCE_KEY,
                  final_marking=None, return_visited_elements=False):
    """
    Do the playout of a Petrinet generating a log

    Parameters
    ----------
    net
        Petri net to play-out
    initial_marking
        Initial marking of the Petri net
    no_traces
        Number of traces to generate
    max_trace_length
        Maximum number of events per trace (do break)
    case_id_key
        Trace attribute that is the case ID
    activity_key
        Event attribute that corresponds to the activity
    timestamp_key
        Event attribute that corresponds to the timestamp
    final_marking
        If provided, the final marking of the Petri net
    """


    # assigns to each event an increased timestamp from 1970
    curr_timestamp = 10000000
    all_visited_elements = []

    for i in range(no_traces):
        visited_elements = []
        visible_transitions_visited = []

        marking = copy(initial_marking)
        while len(visible_transitions_visited) < max_trace_length:
            visited_elements.append(marking)

            if not semantics.enabled_transitions(net, marking):  # supports nets with possible deadlocks
                break
            all_enabled_trans = semantics.enabled_transitions(net, marking)
            if final_marking is not None and marking == final_marking:
                trans = choice(list(all_enabled_trans.union({None})))
            else:
                trans = choice(list(all_enabled_trans))
            if trans is None:
                break

            visited_elements.append(trans)
            if trans.label is not None:
                visible_transitions_visited.append(trans)

            marking = semantics.execute(trans, net, marking)

        all_visited_elements.append(tuple(visited_elements))

    if return_visited_elements:
        return all_visited_elements

    log = log_instance.EventLog()

    for index, visited_elements in enumerate(all_visited_elements):
        current_low_level_events_per_activity = dict()
        times_at_start = dict()
        trace = log_instance.Trace()
        trace.attributes[case_id_key] = str(index)
        for element in visited_elements:
            if type(element) is PetriNet.Transition and element.label is not None:
                event = log_instance.Event()
                event[activity_key] = element.label
                dur = 60*60
                if element.name is not None:
                    if element.name not in current_low_level_events_per_activity:
                        current_low_level_events_per_activity[element.name] = []
                    dur = durations_per_act[element.name].pop()
                current_low_level_events_per_activity[element.name].append(event)

                trace.append(event)
                # increases by 1 hour
                curr_timestamp += dur
                event[timestamp_key] = datetime.datetime.fromtimestamp(curr_timestamp)
            elif type(element) is Marking:
                marked_places = [place.name for place in element.keys() if element[place] > 0]
                for place in marked_places:
                    roles = place.split("#")
                    for role in roles:
                        if "_start" in role:
                            activity_name = role.replace("_start", "")
                            times_at_start[activity_name] = curr_timestamp
                        if "_end" in role:
                            #print(role)
                            activity_name = role.replace("_end", "")
                            if activity_name in current_low_level_events_per_activity.keys():
                                events = current_low_level_events_per_activity[activity_name]
                                res = random.choice(resources_per_act[activity_name])
                                dur = durations_per_act[activity_name].pop()
                                #time_change = datetime.timedelta(minutes=dur)
                                #dur = dur * 60
                                #print(times_at_start[activity_name])
                                for i, event in enumerate(events):
                                    #event[timestamp_key] = datetime.datetime.fromtimestamp(times_at_start[activity_name] + int((dur*(i+1))/len(events)))
                                    event[resource_key] = res
                                #print([event[activity_key] for event in events])
                                current_low_level_events_per_activity[activity_name] = []
                #print(marked_places)
        trace = sorting.sort_timestamp_trace(trace, timestamp_key)
        log.append(trace)

    return log

if __name__ == '__main__':
    net = PetriNet("runningexample")

    source = PetriNet.Place("Receive request_start")
    net.places.add(source)
    t_a = PetriNet.Transition("silent_1", None)
    net.transitions.add(t_a)

    p_2 = PetriNet.Place("Receive request_end")
    net.places.add(p_2)

    exclusion_receive_db(net, source, p_2, "Receive request")
    petri_utils.add_arc_from_to(p_2, t_a, net)
    p_3 = PetriNet.Place("Check thoroughly_start#Check casually_start")
    net.places.add(p_3)
    petri_utils.add_arc_from_to(t_a, p_3, net)

    # Examination
    p_4 = PetriNet.Place("Check thoroughly_end#Check casually_end#Decide_start")
    net.places.add(p_4)
    thorough(net, p_3, p_4, "Check thoroughly")
    casual(net, p_3, p_4, "Check casually")

    p_5 = PetriNet.Place("Decide_end#Notify about decision_start")
    net.places.add(p_5)
    decide(net, p_4, p_5, "Decide")

    p_6 = PetriNet.Place("Notify about decision_end")

    net.places.add(p_6)
    exclusion_send(net, p_5, p_6, "Notify about decision")

    t_11 = PetriNet.Transition("silent_11", None)
    net.transitions.add(t_11)
    petri_utils.add_arc_from_to(p_6, t_11, net)
    sink = PetriNet.Place("End")
    net.places.add(sink)
    petri_utils.add_arc_from_to(t_11, sink, net)

    p_10 = PetriNet.Place("Receive status inquiry_start#Notify about status_end")
    net.places.add(p_10)
    petri_utils.add_arc_from_to(t_a, p_10, net)
    t_c = PetriNet.Transition("silent_3", None)
    net.transitions.add(t_c)
    petri_utils.add_arc_from_to(p_10, t_c, net)

    p_7 = PetriNet.Place("Receive status inquiry_end#Notify about status_start")
    net.places.add(p_7)

    exclusion_receive(net, p_10, p_7, "Receive status inquiry")

    exclusion_send(net, p_7, p_10, "Notify about status")

    p_11 = PetriNet.Place("p_11")
    net.places.add(p_11)

    petri_utils.add_arc_from_to(t_c, p_11, net)
    t_g = PetriNet.Transition("silent_6", None)
    net.transitions.add(t_g)
    petri_utils.add_arc_from_to(p_11, t_g, net)
    petri_utils.add_arc_from_to(t_g, p_10, net)
    petri_utils.add_arc_from_to(p_11, t_11, net)

    # Adding tokens
    initial_marking = Marking()
    initial_marking[source] = 1
    final_marking = Marking()
    final_marking[sink] = 1

    from pm4py.visualization.petri_net import visualizer as pn_visualizer

    gviz = pn_visualizer.apply(net, initial_marking, final_marking)
    pn_visualizer.view(gviz)
    from pm4py.objects.petri_net.exporter import exporter as pnml_exporter

    pnml_exporter.apply(net, initial_marking, "../output/petri.pnml")

    from pm4py.algo.simulation.playout.petri_net import algorithm as simulator

    high_level_acts = set([trans.name for trans in net.transitions])
    print(high_level_acts)
    clerks = ["c1", "c2", "c3", "c4", "c5", "c6", "c7", "c8", "c9", "c10"]
    experts = ["e1", "e2", "e3", "e4"]
    managers = ["m1", "m2", "m3"]
    resources_per_act = {}
    for act in high_level_acts:
        if act == "Decide":
            resources_per_act[act] = managers
        elif act == "Check thoroughly":
            resources_per_act[act] = experts
        else:
            resources_per_act[act] = clerks

    durations_per_act = {"Receive request": deque(sample_from_normal(mu=10, sigma=2))}#, "Check thoroughly": deque(sample_from_normal(mu=5, sigma=2))}
    for act in high_level_acts:
        if act not in durations_per_act.keys():
            durations_per_act[act] = deque(sample_from_normal(mu=60, sigma=10))

    simulated_log = apply_playout(net, initial_marking, resources_per_act, durations_per_act, 10000)#simulator.apply(net, initial_marking, variant=simulator.Variants.BASIC_PLAYOUT, parameters={simulator.Variants.BASIC_PLAYOUT.value.Parameters.NO_TRACES: 10000})
    from pm4py.objects.log.exporter.xes import exporter as xes_exporter

    xes_exporter.apply(simulated_log, '../output/low_level_raw.xes')


