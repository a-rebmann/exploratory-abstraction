## util function to compute the timestamp an choose the ressource
#from pydoc import resolve
import numpy as np
import datetime
from tqdm import tqdm


 # function to compute the actual time needed for a specific activity with help of triangular distribution
def get_triang_time(_min, _mode, _max):
    if int(_min) != int(_mode): return int(np.random.default_rng().triangular(_min, _mode, _max))
    else: return int(_min)

def shift_time_remaining(shift_start, shift_end, curr_time):
    #compute the remaining time in the shift of a resource
        if curr_time.hour >= shift_end.hour:
            remaining_shift = datetime.timedelta(seconds=0)
            return remaining_shift

        if curr_time.hour < shift_start.hour:
            remaining_shift = datetime.timedelta(seconds=0)
            return remaining_shift

        time_remaining = shift_end

        time_remaining = datetime.timedelta(
            hours=time_remaining.hour, minutes=time_remaining.minute, seconds=time_remaining.second)

        curr_time = str(curr_time)
        curr_time = curr_time[11:19]
        curr_time = datetime.datetime.strptime(curr_time, "%H:%M:%S")

        curr_time = datetime.timedelta(hours=curr_time.hour,
                            minutes=curr_time.minute, seconds=curr_time.second)
        time_remaining -= curr_time

        return time_remaining

def get_role(event, model): 
        activity = model.get_transition(event)
        return activity.get_organizational_unit() 

def check_time(datum, shift_start, shift_end):
    #check if the current timestamp is wtihin working hours and adapt it if necessary

    # if date has the datatype string, then it needed to be converted to datetime object
        if not isinstance(datum, datetime.datetime):
            datum = datetime.datetime.strptime(datum, "%d.%m.%Y %H:%M:%S")

        if datum.hour < shift_start.hour:
            datum = datum.replace(hour=shift_start.hour, minute=0, second=0)
        elif datum.hour >= shift_end.hour:
            datum += datetime.timedelta(days=1)
            datum = datum.replace(hour=shift_start.hour, minute=0, second=0)

            # On weekend nobody is working therefore the actual timestamp is shifted to monday
        if datum.weekday() == 5:            # 5 == Saturday
            datum += datetime.timedelta(days=2)
            datum = datum.replace(hour=shift_start.hour, minute=0, second=0)
        elif datum.weekday() == 6:          # 6 == Sunday
            datum += datetime.timedelta(days=1)
            datum = datum.replace(hour=shift_start.hour, minute=0, second=0)

        return datum

def get_timestamp(timestamp, shift_start, shift_end, duration):
        if duration == None: return timestamp
        #compute the new timestamp   

        #adapt the timestamp if it is out o working hours
        if timestamp.hour >= shift_end.hour:
            timestamp = check_time(timestamp, shift_start, shift_end)
        if timestamp.hour < shift_start.hour:
            timestamp = check_time(timestamp, shift_start, shift_end)

        # compute remaining time in a shift in seconds
        shift_remaining_seconds = shift_time_remaining(shift_start, shift_end, timestamp).total_seconds()

        # Jump to the next shift if the needed time for the activity takes longer than the time remaining in the shift 
        # otherwise: return the timestamp marking the end of the activity
        if shift_remaining_seconds > duration:
            timestamp = check_time(datum = (timestamp + datetime.timedelta(seconds=duration)), shift_start = shift_start, shift_end = shift_end)
            return timestamp
        else:
            while shift_remaining_seconds < duration:
                duration = duration - \
                    shift_time_remaining(shift_start, shift_end, timestamp).total_seconds()
                was_er_schon_gemacht_hat = shift_time_remaining(shift_start, shift_end, timestamp)
                timestamp = check_time(timestamp+was_er_schon_gemacht_hat, shift_start, shift_end)
                shift_remaining_seconds = shift_time_remaining(shift_start, shift_end, timestamp).total_seconds()

            return timestamp+datetime.timedelta(seconds=duration)


# def simulate(machine, model, time_ress, n, start_time, start_activity):
    
#     traces = []
#     timestamp = datetime.datetime.strptime(start_time, "%d.%m.%Y %H:%M:%S")
#     currstarttime = datetime.datetime.strptime(start_time, "%d.%m.%Y %H:%M:%S")  # initial timestamp
#     casestamp = currstarttime

#     for i in tqdm(range(n)):
#         timestamp = casestamp
#         lastactivity = start_activity
#         lastactivity_notsilent = model.get_transition(lastactivity)
#         machine.set_state(machine.initial)
#         model.set_attribute("isComplete", "not complete")
#         resource = None

#         while machine.get_triggers(model, machine.get_model_state(model).name) != []:
#             activity = model.get_next_event(lastactivity, machine) 

#             #collect attributes
#             model.trigger(activity)
#             lastactivity = activity
#             if "silent" not in activity:
#                 starttime = timestamp
#                 (newresource, role, timestamp) = time_ress.get_ressource_timestamp(activity, timestamp)

#                 activity = model.get_transition(activity)
#                 waiting_time = lastactivity_notsilent.get_waiting_time() 
#                 shift_start, shift_end = time_ress.get_user_shift(role)
#                 timestamp = get_timestamp(timestamp, shift_start, shift_end, waiting_time)
#                 starttime = get_timestamp(starttime, shift_start, shift_end, waiting_time)
                                 
#                 resource = activity.check_resource(resource, newresource)
#                 traces.append([i, activity.get_label(), activity.get_high_level_activity().get_label(),role, resource, starttime, timestamp, model.get_attribute_value("isComplete")])
#                 lastactivity_notsilent = activity

#         #add waiting time between the just completed and now beginning case 
#         mn, md, mx = time_ress.get_order_intervall(casestamp.weekday())        
#         casestamp += datetime.timedelta(seconds=round(np.random.default_rng().triangular(mn, md, mx)))

#         #make timestamp compatible with shift schedule
#         shift_start, shift_end = time_ress.get_user_shift(role)
#         casestamp = check_time(datum=casestamp, shift_start=shift_start, shift_end=shift_end)
#         timestamp = check_time(timestamp, shift_start=shift_start, shift_end=shift_end)
#     return traces

