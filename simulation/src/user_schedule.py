from calendar import weekday
import datetime
import random
import src.simulation_util as simulation


class User_schedule:
    def __init__(self, startdate, model):
        self.model = model
        self.timeDict = {}    
        self.weekday_user_shift_schedule = dict()
        self.order_intervall = dict()
        self.startdate = startdate
        self.user_pool = {}

    def get_order_intervall(self, day):
        if self.order_intervall == {}: return (1800, 3600, 4500)
        else: return self.order_intervall[day]

    def set_order_intervall(self, day, intervall):

        self.order_intervall[day] = intervall    
    
    def add_user_shift(self, organizational_unit, begin, end):
        self.weekday_user_shift_schedule[organizational_unit] = (begin, end)

    def get_user_shift(self, organizational_unit):
        if self.weekday_user_shift_schedule == {} or organizational_unit not in self.weekday_user_shift_schedule:
            shift_start = "08:00:00"
            shift_end = "16:00:00"
        else:
            shift_start, shift_end = self.weekday_user_shift_schedule.get(organizational_unit)
            shift_start = datetime.datetime.strptime(shift_start, "%H:%M:%S")
            shift_end = datetime.datetime.strptime(shift_end, "%H:%M:%S")
        return (shift_start, shift_end)    

    def set_number_associates_in_organizational_unit(self, organizational_unit, number): 
        self.user_pool[organizational_unit] = [item + str(i + 1) for i, item in enumerate([organizational_unit] * number)]
        for x in self.user_pool[organizational_unit]:
            self.timeDict[x] = self.startdate  

    def get_ressource_timestamp(self, activity, timestamp):
        if activity is not None: 
            role = simulation.get_role(activity, self.model)
            resource = random.choice(self.user_pool.get(role))

        earrliesttime = timestamp
        dictTime = self.timeDict.get(resource)
        if dictTime != None:
            if (dictTime > timestamp):
                # durchprobieren freier Ressourcen wenn beschäftigt:
                earrliesttime = dictTime
                for curruser in self.user_pool.get(role):
                    currtime = self.timeDict.get(curruser)
                    if currtime > timestamp:
                        if currtime < earrliesttime:
                            earrliesttime = currtime
                        else:
                            earrliesttime = timestamp
                            break

        timestamp = earrliesttime
        shift_start, shift_end = self.get_user_shift(role)
        min, max, avg = self.model.get_transition(activity).get_time()
        duration = simulation.get_triang_time(min, max, avg) 
        timestamp = simulation.get_timestamp(timestamp, shift_start, shift_end, duration)
        self.timeDict.update({resource: timestamp})
        
        return (resource, role, timestamp)
        
    