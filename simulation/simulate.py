import datetime
from tqdm import tqdm
from src.simulation_util import get_timestamp, check_time
import numpy as np


def simulate(machine, model, time_ress, n, start_time, start_activity):
    traces = []
    timestamp = datetime.datetime.strptime(start_time, "%d.%m.%Y %H:%M:%S")
    currstarttime = datetime.datetime.strptime(start_time, "%d.%m.%Y %H:%M:%S")  # initial timestamp
    casestamp = currstarttime

    for i in tqdm(range(n)):
        timestamp = casestamp
        lastactivity = start_activity
        machine.set_state(machine.initial)
        model.set_attribute("isComplete", "not complete")
        model.set_attribute("isAccepted", None)
        resource = None

        while machine.get_triggers(model, machine.get_model_state(model).name) != []:
            activity = model.get_next_event(lastactivity, machine)

            # collect attributes
            model.trigger(activity)
            lastactivity = activity
            if "silent" not in activity:
                # starttime = timestamp
                # newresource, role, timestamp) = time_ress.get_ressource_timestamp(activity, timestamp)

                # activity = model.get_transition(activity)
                # waiting_time = activity.get_waiting_time()
                # shift_start, shift_end = time_ress.get_user_shift(role)
                # timestamp = simulation.get_timestamp(timestamp, shift_start, shift_end, waiting_time)
                # starttime = simulation.get_timestamp(starttime, shift_start, shift_end, waiting_time)

                # resource = activity.check_resource(resource, newresource)
                # traces.append(
                #     [i, activity.get_label(), activity.get_high_level_activity().get_label(), role, resource, starttime,
                #      timestamp, model.get_attribute_value("isComplete"), model.get_attribute_value("isAccepted")])

                starttime = timestamp
                (newresource, role, timestamp) = time_ress.get_ressource_timestamp(activity, timestamp)

                activity = model.get_transition(activity)
                resource = activity.check_resource(resource, newresource)
                waiting_time = activity.get_waiting_time()
                shift_start, shift_end = time_ress.get_user_shift(role)
                timestamp = get_timestamp(timestamp, shift_start, shift_end, waiting_time)
                starttime = get_timestamp(starttime, shift_start, shift_end, waiting_time)

                traces.append([i,
                               activity.get_label(),
                               activity.get_high_level_activity().get_label(),
                               role,
                               resource,
                               starttime,
                               timestamp,
                               model.get_attribute_value("isComplete"),
                               model.get_attribute_value("isAccepted")])

        # add waiting time between the just completed and now beginning case
        mn, md, mx = time_ress.get_order_intervall(casestamp.weekday())
        casestamp += datetime.timedelta(seconds=round(np.random.default_rng().triangular(mn, md, mx)))

        # make timestamp compatible with shift schedule
        shift_start, shift_end = time_ress.get_user_shift(role)
        casestamp = check_time(datum=casestamp, shift_start=shift_start, shift_end=shift_end)
        timestamp = check_time(timestamp, shift_start=shift_start, shift_end=shift_end)

    return traces

# not generic part: need to decide what happened with the different attributes and needed to be added to a list
# init of every attribute could be in a function in model class
# check whether a attribute is silent
