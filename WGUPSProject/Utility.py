import copy
import config
import Package


# Takes a time in minutes of the 24 hour day and returns a military time value
# time complexity O(1)
def pretty_time_conversion(time_in_mins):
    if type(time_in_mins) is not int:
        if type(time_in_mins) is float:
            remainder = time_in_mins - int(time_in_mins)
            whole = time_in_mins - remainder
            if remainder >= .49:
                whole += 1.0
            time_in_mins = int(whole)
        else:
            time_in_mins = int(time_in_mins)
    hours = int(time_in_mins) // 60
    minutes = int(time_in_mins) % 60
    return "%02d:%02d" % (hours, minutes)


# takes a 12 hour clock time and converts it into a float value for the current minute of the day.
# 1440 minutes in a 24 hour day, program assumes end of work day is 7pm which is 1140 minutes.
# time complexity O(1)
def backwards_pretty_time_conversion(twelve_hour_time_format_in_string):
    if twelve_hour_time_format_in_string == "EOD":
        return 1140.0
    else:
        times = twelve_hour_time_format_in_string.split(' ')
        hours, minutes = times[0].split(':')
        hours.replace(' ', '')
        minutes.replace(' ', '')
        hours = int(hours)
        minutes = int(minutes)
        if times[1].casefold() == "AM".casefold():
            minutes += (hours * 60)
        else:
            minutes += ((hours + 12) * 60)
        return float(minutes)


# converts distance in miles into minutes used with 3 decimals precision.
# calculates the time taken to drive 'x' miles
# time complexity O(1)
def convert_time_taken_into_minutes(distance_traveled):
    return float("%0.3f" % ((distance_traveled / 18.0) * 60.0))


# checks status of all package list to see if all were delivered.
# time complexity O(n) based on package list length
def is_packages_delivered(list_of_packages):
    i = 0
    while i < len(list_of_packages):
        if list_of_packages[i].status != Package.Status(4):
            break
        i += 1
    else:
        return True
    return False


# adds 65 minutes to the current time for the second load from the hub in the manual loading process.
# employees have to clean up the work space left messy from the first crew ( of course )
# time complexity O(1)
def sweep_the_floors(current_time):
    current_time = current_time + 65
    return current_time


# takes a list of numbers and transforms it into a list of packages using the hash table for quick lookup.
# time complexity O(n) due to going through one loop twice.
def turn_list_of_package_ids_to_list_of_packages(list_of_ids):
    packages = []
    for i in range(len(list_of_ids)):
        packages.append(config.hash_table.search(copy.deepcopy(list_of_ids[i])))
    for i in range(len(packages)):
        list_of_ids[i] = copy.deepcopy(packages[i])
