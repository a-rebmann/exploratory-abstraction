# util function to compute the timestamp and choose the resource
import numpy as np
import datetime


# function to compute the actual time needed for a specific activity with help of triangular distribution
def get_triang_time(_min, _mode, _max):
    if int(_min) != int(_mode):
        return int(np.random.default_rng().triangular(_min, _mode, _max))
    else:
        return int(_min)


def shift_time_remaining(shift_start, shift_end, curr_time):
    # compute the remaining time in the shift of a resource
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
    # check if the current timestamp is wtihin working hours and adapt it if necessary

    # if date has the datatype string, then it needed to be converted to datetime object
    if not isinstance(datum, datetime.datetime):
        datum = datetime.datetime.strptime(datum, "%d.%m.%Y %H:%M:%S")

    if datum.hour < shift_start.hour:
        datum = datum.replace(hour=shift_start.hour, minute=0, second=0)
    elif datum.hour >= shift_end.hour:
        datum += datetime.timedelta(days=1)
        datum = datum.replace(hour=shift_start.hour, minute=0, second=0)

        # On weekend nobody is working therefore the actual timestamp is shifted to monday
    if datum.weekday() == 5:  # 5 == Saturday
        datum += datetime.timedelta(days=2)
        datum = datum.replace(hour=shift_start.hour, minute=0, second=0)
    elif datum.weekday() == 6:  # 6 == Sunday
        datum += datetime.timedelta(days=1)
        datum = datum.replace(hour=shift_start.hour, minute=0, second=0)

    return datum


def get_timestamp(timestamp, shift_start, shift_end, duration):
    if duration == None: return timestamp
    # compute the new timestamp

    # adapt the timestamp if it is out o working hours
    if timestamp.hour >= shift_end.hour:
        timestamp = check_time(timestamp, shift_start, shift_end)
    if timestamp.hour < shift_start.hour:
        timestamp = check_time(timestamp, shift_start, shift_end)

    # compute remaining time in a shift in seconds
    shift_remaining_seconds = shift_time_remaining(shift_start, shift_end, timestamp).total_seconds()

    # Jump to the next shift if the needed time for the activity takes longer than the time remaining in the shift
    # otherwise: return the timestamp marking the end of the activity
    if shift_remaining_seconds > duration:
        timestamp = check_time(datum=(timestamp + datetime.timedelta(seconds=duration)), shift_start=shift_start,
                               shift_end=shift_end)
        return timestamp
    else:
        while shift_remaining_seconds < duration:
            duration = duration - \
                       shift_time_remaining(shift_start, shift_end, timestamp).total_seconds()
            was_er_schon_gemacht_hat = shift_time_remaining(shift_start, shift_end, timestamp)
            timestamp = check_time(timestamp + was_er_schon_gemacht_hat, shift_start, shift_end)
            shift_remaining_seconds = shift_time_remaining(shift_start, shift_end, timestamp).total_seconds()

        return timestamp + datetime.timedelta(seconds=duration)

