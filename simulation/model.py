import numpy as np
from pm4py.objects.petri_net.utils import reachability_graph

class Model:
    def __init__(self): 
        self.dict_activity = dict()
        self.dict_attributes = dict()

    def get_next_event(self, event, machine):
        #set attribute isComplete
        if event == "silent_1": 
            self.set_attribute("isComplete", np.random.choice(["complete", "not complete"], p=[0.7, 0.3]))
        if event == "silent_4":
            self.set_attribute("isAccepted", np.random.choice(["true", "false"], p=[0.7, 0.3]))

        #decide the which activity is following based on the value of isComplete
        if event == "silent_2":
            if self.dict_attributes["isComplete"] == "not complete": return "name_11"
            else: return np.random.choice(["silent_3", "name_10"])
        else: return np.random.choice(machine.get_triggers(self, machine.get_model_state(self).name))

    def add_transition(self, activity): #activity of type Acitivity
        self.dict_activity [activity.get_id()] = activity
    
    def get_transition(self, id): 
        return self.dict_activity[id]

    def get_list_states(self, petri_net, initial_marking):
        #list of states of the reachability graph
        #needed to build the machine
        rg = reachability_graph.construct_reachability_graph(petri_net, initial_marking) 
        states = list()
        for s in rg.states:
            states.append(str(s))
        return states

    def get_list_transitions(self, petri_net, initial_marking):
        #list of transitions of the reachability graph
        #needed to build the machine
        rg = reachability_graph.construct_reachability_graph(petri_net, initial_marking)
        list_transition = []
        for t in rg.transitions:
            id = t.name.split("," )[0]
            id = id.split("(")[1]
            #activity = petri_utils.get_transition_by_name(petri_net, id)
            list_transition.append([id, str(t.from_state), str(t.to_state)])
        return list_transition
    
    def set_attribute(self, key, value):
        self.dict_attributes[key] = value

    def get_attribute_value(self, key):
        return self.dict_attributes[key]

    
            
    