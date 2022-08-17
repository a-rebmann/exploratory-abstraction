from pm4py.objects.petri_net.utils import petri_utils
import numpy as np

class Activity:
    #group all characteritcs for a Acivity
    def __init__(self, transition, organizational_unit, waiting_time=None, waiting_time_distribution=None):
        self.transition = transition
        self.organizational_unit = organizational_unit
        self.waiting_time = waiting_time
        self.waiting_time_distribution = waiting_time_distribution
        self.High_level_activity_started = True

    def get_label(self):
        return self.transition.label

    def get_id(self):
        return self.transition.name

    def get_organizational_unit(self):
        return self.organizational_unit

    def get_waiting_time(self):
        if self.waiting_time == None: return 0 
        if self.waiting_time_distribution == "triangular":
            return round(np.random.default_rng().triangular(self.waiting_time[0], self.waiting_time[1], self.waiting_time[2]))

        if self.waiting_time_distribution == "exponential":
            return round(np.random.default_rng().exponential(self.waiting_time))


