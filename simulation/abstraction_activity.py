from src.activity import Activity

class Low_level_Activity(Activity):
    def __init__(self, transition, organizational_unit, time, model, waiting_time=None, waiting_time_distribution=None): 
        super().__init__(transition, organizational_unit)
        self.time = time 
        model.add_transition(self)
        self.highlevel_activity = None
        self.waiting_time = waiting_time
        self.waiting_time_distribution = waiting_time_distribution
        
    def get_time(self):
        return self.time

    def set_high_level_activity(self, high_level_activity):
        self.highlevel_activity = high_level_activity
    
    def get_high_level_activity(self):
        return self.highlevel_activity

    def get_waiting_time(self):
        if self.get_high_level_activity() == None:
            return super().get_waiting_time()

        else:
            return self.get_high_level_activity().get_waiting_time(self.get_id()) 
           
    def check_resource(self, old_resource, new_resource):
        high_level_activity = self.get_high_level_activity()

        #check whether there exists a highlevel activity
        #check if a new highlevel activity begins -> new resource needed
        if (high_level_activity.started() or old_resource == None) and high_level_activity != None: 
            return new_resource 
        else: return old_resource

class High_level_activity(Activity):
    def __init__(self, transition, organizational_unit, low_level_acitvities, waiting_time, waiting_time_distribution):
        super().__init__(transition, organizational_unit)
        self.low_level_acitvities = low_level_acitvities
        self.waiting_time = waiting_time
        self.used_low_level_activity = []
        for act in self.low_level_acitvities:
            act.set_high_level_activity(self)
        self.waiting_time_distribution = waiting_time_distribution
        self.High_level_activity_started = True

    def check_begin(self, activity):
        started = self.High_level_activity_started  
        self.used_low_level_activity.append(activity)
        if (len(self.low_level_acitvities) == len(set(self.used_low_level_activity))) or "silent" in activity: 
            self.used_low_level_activity = []
            self.High_level_activity_started = True
        else: 
            self.High_level_activity_started = False

        return started
    
    def started(self):
        return self.High_level_activity_started
    
    def get_waiting_time(self, activity_id):
        if self.check_begin(activity_id) :
                return super().get_waiting_time()