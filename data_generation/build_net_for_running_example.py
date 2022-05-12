from pm4py.objects.petri_net.obj import PetriNet, Marking # Objects for constructing a Petri net system.
from pm4py.objects.petri_net.utils import petri_utils

if __name__ == '__main__':
    
    net = PetriNet("runningexample")

    source = PetriNet.Place("Start")
    net.places.add(source)
    t_a = PetriNet.Transition("silent_1", "")
    net.transitions.add(t_a)
    petri_utils.add_arc_from_to(source, t_a, net)
    p_1 = PetriNet.Place("p_1")
    net.places.add(p_1)
    petri_utils.add_arc_from_to(t_a, p_1, net)
    t_1 = PetriNet.Transition("name_1", "Receive request")
    net.transitions.add(t_1)
    petri_utils.add_arc_from_to(p_1, t_1, net)

    p_13 = PetriNet.Place("p_13")
    net.places.add(p_13)
    petri_utils.add_arc_from_to(t_1, p_13, net)
    t_f = PetriNet.Transition("silent_5", "")
    net.transitions.add(t_f)
    petri_utils.add_arc_from_to(p_13, t_f, net)

    p_2 = PetriNet.Place("p_2")
    net.places.add(p_2)
    petri_utils.add_arc_from_to(t_f, p_2, net)

    t_2 = PetriNet.Transition("name_2", "Check completeness")
    net.transitions.add(t_2)
    petri_utils.add_arc_from_to(p_2, t_2, net)
    p_3 = PetriNet.Place("p_3")
    net.places.add(p_3)
    petri_utils.add_arc_from_to(t_2, p_3, net)
    #Loop back

    t_9 = PetriNet.Transition("name_9", "Inquire about missing information")
    net.transitions.add(t_9)
    petri_utils.add_arc_from_to(p_3, t_9, net)

    petri_utils.add_arc_from_to(t_9, p_1, net)

    # Examination
    t_3 = PetriNet.Transition("name_3", "Examine request thoroughly")
    t_4 = PetriNet.Transition("name_4", "Examine request casually")
    net.transitions.add(t_3)
    net.transitions.add(t_4)
    petri_utils.add_arc_from_to(p_3, t_3, net)
    petri_utils.add_arc_from_to(p_3, t_4, net)
    p_4 = PetriNet.Place("p_4")
    net.places.add(p_4)
    petri_utils.add_arc_from_to(t_3, p_4, net)
    petri_utils.add_arc_from_to(t_4, p_4, net)
    # Decision
    t_5 = PetriNet.Transition("name_5", "Decide on acceptance")
    net.transitions.add(t_5)
    petri_utils.add_arc_from_to(p_4, t_5, net)
    p_5 = PetriNet.Place("p_5")
    net.places.add(p_5)
    petri_utils.add_arc_from_to(t_5, p_5, net)
    t_6 = PetriNet.Transition("name_6", "Communicate decision")
    net.transitions.add(t_6)
    petri_utils.add_arc_from_to(p_5, t_6, net)
    p_6 = PetriNet.Place("p_6")
    petri_utils.add_arc_from_to(t_6, p_6, net)
    net.places.add(p_6)
    t_e = PetriNet.Transition("silent_4", "")

    net.transitions.add(t_e)
    petri_utils.add_arc_from_to(p_6, t_e, net)
    p_12 = PetriNet.Place("p12")
    net.places.add(p_12)
    petri_utils.add_arc_from_to(t_e, p_12, net)
    t_11 = PetriNet.Transition("name_11", "Decision communicated")
    net.transitions.add(t_11)
    petri_utils.add_arc_from_to(p_12, t_11, net)
    sink = PetriNet.Place("End")
    net.places.add(sink)
    petri_utils.add_arc_from_to(t_11, sink, net)

    p_10 = PetriNet.Place("p_10")
    net.places.add(p_10)
    petri_utils.add_arc_from_to(t_a, p_10, net)
    t_c = PetriNet.Transition("silent_3", "")
    net.transitions.add(t_c)
    petri_utils.add_arc_from_to(p_10, t_c, net)
    t_7 = PetriNet.Transition("name_7", "Receive inquiry")
    net.transitions.add(t_7)
    petri_utils.add_arc_from_to(p_10, t_7, net)
    p_7 = PetriNet.Place("p_7")
    net.places.add(p_7)
    petri_utils.add_arc_from_to(t_7, p_7, net)
    t_8 = PetriNet.Transition("name_8", "Notify about status")
    net.transitions.add(t_8)
    petri_utils.add_arc_from_to(p_7, t_8, net)
    p_8 = PetriNet.Place("p_8")
    net.places.add(p_8)
    petri_utils.add_arc_from_to(t_8, p_8, net)
    t_10 = PetriNet.Transition("name_10", "Notification sent")
    net.transitions.add(t_10)
    petri_utils.add_arc_from_to(p_8, t_10, net)
    p_11 = PetriNet.Place("p_11")
    net.places.add(p_11)
    petri_utils.add_arc_from_to(t_10, p_11, net)
    petri_utils.add_arc_from_to(t_c, p_11, net)
    t_g = PetriNet.Transition("silent_6", "")
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