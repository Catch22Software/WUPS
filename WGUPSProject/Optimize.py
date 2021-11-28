import copy
import Package
import config

'''
core self-adjusting "greedy" algorithm based off Dijkstra's algorithm.
takes a list of package objects and then finds the closest one to the hub and places it in position #0.
then looks for the next closest package from position #0 and places it in position #1.
algorithm continues to do so until it gets to the last position and returns the restructured list.
if two packages contain the same location they will end up next to each other.
returns a list containing as many lists as necessary based on the input size. The output list must be of size
16 or less due to the truck load max capacity. Algorithm will always return in the form of a list of list(s).
time complexity O(n**2) due to the double nested while loop for checking through the list once per item.'''


def _optimize_one_list(list_to_optimize):
    if len(list_to_optimize) == 0:
        return None  # returns None if nothing is sent from the caller
    elif len(list_to_optimize) == 1:
        holder = []
        holder.append(copy.deepcopy(list_to_optimize))
        return holder  # returns the list if it only contain one package.
    else:
        route = []
        runs = []
        while True:
            current_position = "Western Governors University"
            i = 0
            x = 0
            minimum_distance = float('inf')
            index_to_swap = -1
            while x < (len(list_to_optimize) - 1):
                index = config.master_addresses.index(list_to_optimize[i].address)
                value = config.area_graph_object \
                    .return_distance_between_two_vertices(current_position,
                                                          config.master_names[index])
                #  utilizes a master names list for the locations based off the address contained in the Package object
                if 0.0 < value < minimum_distance:
                    minimum_distance = value
                    index_to_swap = i
                if i < (len(list_to_optimize) - 1):
                    i += 1
                    continue
                else:
                    temp = copy.deepcopy(list_to_optimize[index_to_swap])
                    list_to_optimize[index_to_swap] = copy.deepcopy(list_to_optimize[x])
                    list_to_optimize[x] = copy.deepcopy(temp)
                    index = config.master_addresses.index(list_to_optimize[x].address)
                    current_position = config.master_names[index]
                    x += 1
                    i = x + 1
                    minimum_distance = float('inf')
                    index_to_swap = -1
                    continue
            if len(list_to_optimize) < 17:
                route.append(copy.deepcopy(list_to_optimize))
                list_to_optimize.clear()
                break
            else:
                for i in range(16):
                    runs.append(copy.deepcopy(list_to_optimize[i]))
                for i in range(16):
                    list_to_optimize.pop(0)
                route.append(copy.deepcopy(runs))
                runs.clear()
                continue
        return route


'''
Version #1 of my optimization used this algorithm as the base and then employed the above protected algorithm 
within to make the individual optimizations. It did not make it into the final cut, due to the below algorithm, 
prioritizing package delivery being on time and minimizing total man hours spent versus miles driven. It takes the 
entire list of packages. updates the entire list based on the current time, then will take out packages that have 
already been delivered, have been delayed and are not at the hub currently, or ones that are currently en-route. 
from that sublist it then checks for any packages that have a deadline less than three hours from the current time.
if there are ANY priority packages, it first checks if any of the priority package list contains a sister package, 
since there are sister packages that have deadlines before EOD. If there is one included in the priority list, 
it adds the rest of the sister packages to the priority list so they go out together. the algorithm uses the above 
sorting algorithm on the priority packages only and splits them between available trucks. If not, it takes the list
and splits it into three categories. One for sister package requirements, one for truck requirements and the rest 
in a no requirements list. It then takes the resulting three categorical lists and runs the above optimization on 
them. It then heuristically builds a list of optimized runs re running the above optimization function before 
putting in a final list of 16. This continues until the all of the three categorical lists are empty. Then returns 
the resulting list of optimized delivery routes in order to be loaded by the trucks. This causes truck loads to not
be maximized always, while minimizing late packages and still optimizing time and mileage. The result ends with a 
quicker delivery day while utilizing both drivers for the entire work day and brings the trucks back to the hub at 
the end as well. This algorithm takes the package list and returns it into optimal "truck loads" based on the 
priority and trucks available. The trucks then heuristically load the packages from the returned package list and 
run the routes until the packages are all delivered. Trucks make 7 total runs with this method. The output for this
run causes the day to end at 12:13 pm with 173.8 total miles ran. All packages are still delivered on time with 
zero late packages, zero productivity losses and excellent labor usage. since it does not make the run under the 
required minimum mileage, it was done elsewhere. No package left behind is the motto of this function.  Every time 
the above optimization method is called, it takes a list of packages and returns a list of a list of packages where
the sublist are all of length 16 or less. This is the cause of the extra lines in order to format the three 
dimensional arrays correctly and still return a list of lists of packages at the end in order for the trucks to be 
able to load efficiently. due to extra complexity involved, the time complexity of this is O(n**3) because of the 
double nested while loops that contain a for loop.'''


def optimize_the_load(package_list, current_time, number_of_trucks_available):
    no_requirement = []
    truck_requirement = []
    sister_requirement = []
    priority_que = []
    for i in range(len(package_list)):
        if package_list[i].time_delivered == -1:
            package_list[i].update_package_at_time(current_time)
            config.master_package_list[i].update_package_at_time(current_time)
        else:
            package_list[i] = None
    i = 0
    while i < len(package_list):
        if package_list[i] is None:
            del package_list[i]
            i = 0
            continue
        else:
            i += 1
            continue
    for i in range(len(package_list)):
        if package_list[i].status == Package.Status(1):
            if package_list[i].deadline - current_time <= 180.0:
                priority_que.append(copy.deepcopy(package_list[i]))
            elif package_list[i].special_notes == "DNE":
                no_requirement.append(copy.deepcopy(package_list[i]))
            elif package_list[i].truck_requirement is not False:
                truck_requirement.append(copy.deepcopy(package_list[i]))
            else:
                sister_requirement.append(copy.deepcopy(package_list[i]))
        else:
            package_list[i] = None
    i = 0
    while i < len(package_list):
        if package_list[i] is None:
            del package_list[i]
            i = 0
            continue
        else:
            i += 1
            continue
    copy_list = False
    for j in range(len(priority_que)):
        if priority_que[j].id in config.sister_package_list:
            copy_list = True
            break
        else:
            continue
    if copy_list:
        for i in range(len(sister_requirement)):
            if sister_requirement[i] not in priority_que:
                priority_que.append(copy.deepcopy(sister_requirement[i]))
                sister_requirement[i] = None
        i = 0
        while i < len(sister_requirement):
            if sister_requirement[i] is None:
                del sister_requirement[i]
                i = 0
                continue
            else:
                i += 1

    delivery_route = [_optimize_one_list(copy.deepcopy(no_requirement)),
                      _optimize_one_list(copy.deepcopy(sister_requirement)),
                      _optimize_one_list(copy.deepcopy(truck_requirement))]
    priority_que = _optimize_one_list(copy.deepcopy(priority_que))
    complete_runs = []
    i = 0
    while i < len(delivery_route):
        if delivery_route[i] is None:
            del delivery_route[i]
            i = 0
            continue
        else:
            i += 1
    if priority_que is None:
        del priority_que
    if 'priority_que' in locals():
        if number_of_trucks_available == 2:
            holder_sisters = []
            holder_else = []
            for i in range(len(priority_que[0])):
                if len(priority_que[0][i].sister_packages) > 0:
                    holder_sisters.append(priority_que[0][i])
                else:
                    holder_else.append(priority_que[0][i])
            if len(holder_sisters) == 0:
                holder_sisters.clear()
                holder_else.clear()
                for i in range(len(priority_que[0])):
                    if i % 2 == 0:
                        holder_sisters.append(priority_que[0][i])
                    else:
                        holder_else.append(priority_que[0][i])
            if len(holder_sisters) > 0:
                holder_sisters = _optimize_one_list(copy.deepcopy(holder_sisters))
                complete_runs.append(holder_sisters[0])
            if len(holder_else) > 0:
                holder_else = _optimize_one_list(copy.deepcopy(holder_else))
                complete_runs.append(holder_else[0])
            return complete_runs
        else:
            complete_runs.append(priority_que[0])
            return complete_runs
    if len(package_list) < 17:
        for i in range(len(delivery_route)):
            for j in range(len(delivery_route[i])):
                if len(delivery_route[i][j]) > 0:
                    for k in range(len(delivery_route[i][j])):
                        complete_runs.append(copy.deepcopy(delivery_route[i][j][k]))
                else:
                    continue
        complete_runs = _optimize_one_list(copy.deepcopy(complete_runs))
    try:
        if len(complete_runs) > 0 and number_of_trucks_available > 0:
            return complete_runs
    except TypeError:
        pass
    try:
        if (len(complete_runs) > 0 and number_of_trucks_available <= 0) or number_of_trucks_available <= 0:
            return "NO AVAILABLE TRUCKS!!!"
    except TypeError:
        pass
    holder_list = []
    single_runs_no_requirement = []
    single_runs_truck_requirement = []
    single_runs_sister_requirement = []
    for i in range(len(delivery_route)):
        if len(delivery_route[i]) > 1:
            for j in range(len(delivery_route[i])):
                if len(delivery_route[i][j]) - len(holder_list) == 16:
                    if len(holder_list) < 16:
                        holder_list.append(copy.deepcopy(delivery_route[i][j]))
                    else:
                        holder_list = _optimize_one_list(copy.deepcopy(holder_list))
                        complete_runs.append(copy.deepcopy(holder_list[0]))
                        holder_list.clear()
                    complete_runs.append(copy.deepcopy(delivery_route[i][j]))
                elif delivery_route[i][j][0].special_notes == "DNE":
                    single_runs_no_requirement.append(copy.deepcopy(delivery_route[i][j]))
                elif len(delivery_route[i][j][0].sister_packages) > 0:
                    single_runs_sister_requirement.append(copy.deepcopy(delivery_route[i][j]))
                else:
                    single_runs_no_requirement.append(copy.deepcopy(delivery_route[i][j]))
                delivery_route[i][j] = None
        else:
            if len(delivery_route[i][0]) - len(holder_list) == 16:
                if len(holder_list) < 16:
                    holder_list.append(copy.deepcopy(delivery_route[i][0]))
                else:
                    holder_list = _optimize_one_list(copy.deepcopy(holder_list))
                    complete_runs.append(copy.deepcopy(holder_list[0]))
                    holder_list.clear()
                complete_runs.append(copy.deepcopy(delivery_route[i][0]))
            elif delivery_route[i][0][0].special_notes == "DNE":
                single_runs_no_requirement.append(copy.deepcopy(delivery_route[i][0]))
            elif len(delivery_route[i][0][0].sister_packages) > 0:
                single_runs_sister_requirement.append(copy.deepcopy(delivery_route[i][0]))
            else:
                single_runs_truck_requirement.append(copy.deepcopy(delivery_route[i][0]))
            delivery_route[i][0] = None
    holder = []
    if len(single_runs_no_requirement) > 1:
        holder = []
        for i in range(len(single_runs_no_requirement)):
            for j in range(len(single_runs_no_requirement[i])):
                holder.append(copy.deepcopy(single_runs_no_requirement[i][j]))
        single_runs_no_requirement.clear()
        single_runs_no_requirement.append(copy.deepcopy(holder))
    if len(single_runs_truck_requirement) > 1:
        holder = []
        for i in range(len(single_runs_truck_requirement)):
            for j in range(len(single_runs_truck_requirement[i])):
                holder.append(copy.deepcopy(single_runs_truck_requirement[i][j]))
        single_runs_truck_requirement.clear()
        single_runs_truck_requirement.append(copy.deepcopy(holder))
    if len(single_runs_sister_requirement) > 1:
        holder = []
        for i in range(len(single_runs_sister_requirement)):
            for j in range(len(single_runs_sister_requirement[i])):
                holder.append(copy.deepcopy(single_runs_sister_requirement[i][j]))
        single_runs_sister_requirement.clear()
        single_runs_sister_requirement.append(copy.deepcopy(holder))
    if len(single_runs_no_requirement) == 0:
        del single_runs_no_requirement
    if len(single_runs_sister_requirement) == 0:
        del single_runs_sister_requirement
    if len(single_runs_truck_requirement) == 0:
        del single_runs_truck_requirement
    del delivery_route, no_requirement, truck_requirement, sister_requirement, holder
    if len(holder_list) > 0:
        if len(holder_list[0]) == 16:
            holder_list.clear()
    while 'single_runs_no_requirement' in locals() and \
            'single_runs_sister_requirement' in locals() and \
            'single_runs_truck_requirement' in locals():
        if ((len(single_runs_no_requirement[0]) + len(single_runs_sister_requirement[0])) - len(holder_list)) < 17:
            for i in range(len(single_runs_sister_requirement[0])):
                if len(holder_list) < 16:
                    if single_runs_sister_requirement[0][i] is not None:
                        holder_list.append(copy.deepcopy(single_runs_sister_requirement[0][i]))
                        single_runs_sister_requirement[0][i] = None
                    else:
                        del single_runs_sister_requirement[0][i]
                        break
                else:
                    break
            for i in range(len(single_runs_no_requirement[0])):
                if len(holder_list) < 16:
                    if single_runs_no_requirement[0][i] is not None:
                        holder_list.append(copy.deepcopy(single_runs_no_requirement[0][i]))
                        single_runs_no_requirement[0][i] = None
                    else:
                        del single_runs_no_requirement[0][i]
                        break
                else:
                    break
            if len(holder_list) == 16:
                holder_list = _optimize_one_list(copy.deepcopy(holder_list))
                complete_runs.append(copy.deepcopy(holder_list[0]))
                holder_list.clear()
            i = 0
            while (('single_runs_sister_requirement' in locals()) and ('single_runs_no_requirement' in locals())
                   and (i < (len(single_runs_sister_requirement[0]) - 1)
                        and i < (len(single_runs_no_requirement[0]) - 1))) \
                    or (i < (len(single_runs_sister_requirement[0]) - 1)
                        and i < (len(single_runs_no_requirement[0]) - 1)):
                for i in range(len(single_runs_sister_requirement[0])):
                    if single_runs_sister_requirement[0][i] is None:
                        del single_runs_sister_requirement[0][i]
                        break
                    else:
                        continue
                for i in range(len(single_runs_no_requirement[0])):
                    if single_runs_no_requirement[0][i] is None:
                        del single_runs_no_requirement[0][i]
                        break
                    else:
                        continue
                if len(single_runs_sister_requirement[0]) == 0 and len(single_runs_no_requirement[0]) == 0:
                    del single_runs_sister_requirement[0], single_runs_no_requirement[0]
                if len(single_runs_sister_requirement[0]) == 0:
                    del single_runs_sister_requirement[0]
                if len(single_runs_sister_requirement) == 0:
                    del single_runs_sister_requirement
                if len(single_runs_no_requirement[0]) == 0:
                    del single_runs_no_requirement[0]
                if len(single_runs_no_requirement) == 0:
                    del single_runs_no_requirement
        elif ((len(single_runs_truck_requirement[0]) + len(single_runs_no_requirement[0])) - len(
                holder_list)) < 17:
            for i in range(len(single_runs_no_requirement[0])):
                if len(holder_list) < 16:
                    if single_runs_no_requirement[0][i] is not None:
                        holder_list.append(copy.deepcopy(single_runs_no_requirement[0][i]))
                        single_runs_no_requirement[0][i] = None
                    else:
                        del single_runs_no_requirement[0][i]
                        break
                else:
                    break
            for i in range(len(single_runs_truck_requirement[0])):
                if len(holder_list) < 16:
                    if single_runs_truck_requirement[0][i] is not None:
                        holder_list.append(copy.deepcopy(single_runs_truck_requirement[0][i]))
                        single_runs_truck_requirement[0][i] = None
                    else:
                        del single_runs_truck_requirement[0][i]
                        break
                else:
                    break
            if len(holder_list) == 16:
                holder_list = _optimize_one_list(copy.deepcopy(holder_list))
                complete_runs.append(copy.deepcopy(holder_list[0]))
                holder_list.clear()
            i = 0
            while (('single_runs_no_requirement' in locals()) and (
                    'single_runs_truck_requirement' in locals())
                   and (i < (len(single_runs_no_requirement[0]) - 1)
                        and i < (len(single_runs_truck_requirement[0]) - 1))) \
                    or (i < (len(single_runs_no_requirement[0]) - 1)
                        and i < (len(single_runs_truck_requirement[0]) - 1)):
                for i in range(len(single_runs_no_requirement[0])):
                    if single_runs_no_requirement[0][i] is None:
                        del single_runs_no_requirement[0][i]
                        break
                    else:
                        continue
                for i in range(len(single_runs_truck_requirement[0])):
                    if single_runs_truck_requirement[0][i] is None:
                        del single_runs_truck_requirement[0][i]
                        break
                    else:
                        continue
                if len(single_runs_no_requirement[0]) == 0 and len(
                        single_runs_truck_requirement[0]) == 0:
                    del single_runs_no_requirement[0], single_runs_truck_requirement[0]
                if len(single_runs_no_requirement[0]) == 0:
                    del single_runs_no_requirement[0]
                if len(single_runs_no_requirement) == 0:
                    del single_runs_no_requirement
                if len(single_runs_truck_requirement[0]) == 0:
                    del single_runs_truck_requirement[0]
                if len(single_runs_truck_requirement) == 0:
                    del single_runs_truck_requirement
        else:
            for i in range(len(single_runs_truck_requirement[0])):
                if len(holder_list) < 16:
                    holder_list.append(copy.deepcopy(single_runs_truck_requirement[0][i]))
                    single_runs_truck_requirement[0][i] = None
                else:
                    break
            if len(holder_list) == 16:
                holder_list = _optimize_one_list(copy.deepcopy(holder_list))
                complete_runs.append(copy.deepcopy(holder_list[0]))
                holder_list.clear()
            i = 0
            while (('single_runs_truck_requirement' in locals()) and (i < (len(single_runs_truck_requirement[0]) - 1))) \
                    or (i < (len(single_runs_truck_requirement[0]) - 1)):
                for i in range(len(single_runs_truck_requirement[0])):
                    if single_runs_truck_requirement[0][i] is None:
                        del single_runs_truck_requirement[0][i]
                        break
                    else:
                        continue
                if len(single_runs_truck_requirement[0]) == 0:
                    del single_runs_truck_requirement[0]
                if len(single_runs_truck_requirement) == 0:
                    del single_runs_truck_requirement
    while (('single_runs_no_requirement' and 'single_runs_sister_requirement' in locals()) or
           ('single_runs_no_requirement' and 'single_runs_truck_requirement' in locals()) or
           ('single_runs_truck_requirement' and 'single_runs_sister_requirement' in locals())):
        if 'single_runs_sister_requirement' in locals():
            if len(single_runs_sister_requirement[0]) > 0:
                for i in range(len(single_runs_sister_requirement[0])):
                    if len(holder_list) < 16:
                        if single_runs_sister_requirement[0][i] is not None:
                            holder_list.append(copy.deepcopy(single_runs_sister_requirement[0][i]))
                            single_runs_sister_requirement[0][i] = None
                        else:
                            del single_runs_sister_requirement[0][i]
                            break
                    else:
                        break
            else:
                del single_runs_sister_requirement
                break
            if len(holder_list) == 16:
                holder_list = _optimize_one_list(copy.deepcopy(holder_list))
                complete_runs.append(copy.deepcopy(holder_list[0]))
                holder_list.clear()
            i = 0
            while ('single_runs_sister_requirement' in locals() and i < (len(single_runs_sister_requirement[0]) - 1)) \
                    or i < (len(single_runs_sister_requirement[0]) - 1):
                for i in range(len(single_runs_sister_requirement[0])):
                    if single_runs_sister_requirement[0][i] is None:
                        del single_runs_sister_requirement[0][i]
                        break
                    else:
                        continue
                if len(single_runs_sister_requirement[0]) == 0:
                    del single_runs_sister_requirement[0]
                if len(single_runs_sister_requirement) == 0:
                    del single_runs_sister_requirement
        elif 'single_runs_no_requirement' in locals():
            if len(single_runs_no_requirement[0]) > 0:
                for i in range(len(single_runs_no_requirement[0])):
                    if len(holder_list) < 16:
                        if single_runs_no_requirement[0][i] is not None:
                            holder_list.append(copy.deepcopy(single_runs_no_requirement[0][i]))
                            single_runs_no_requirement[0][i] = None
                        else:
                            del single_runs_no_requirement[0][i]
                            break
                    else:
                        break
            else:
                del single_runs_no_requirement
                break
            if len(holder_list) == 16:
                holder_list = _optimize_one_list(copy.deepcopy(holder_list))
                complete_runs.append(copy.deepcopy(holder_list[0]))
                holder_list.clear()
            i = 0
            while ('single_runs_no_requirement' in locals() and i < (len(single_runs_no_requirement[0]) - 1)) \
                    or i < (len(single_runs_no_requirement[0]) - 1):
                for i in range(len(single_runs_no_requirement[0])):
                    if single_runs_no_requirement[0][i] is None:
                        del single_runs_no_requirement[0][i]
                        break
                    else:
                        continue
                if len(single_runs_no_requirement[0]) == 0:
                    del single_runs_no_requirement[0]
                if len(single_runs_no_requirement) == 0:
                    del single_runs_no_requirement
        else:
            for i in range(len(single_runs_truck_requirement[0])):
                if len(holder_list) < 16:
                    holder_list.append(copy.deepcopy(single_runs_truck_requirement[0][i]))
                    single_runs_truck_requirement[0][i] = None
                else:
                    break
            if len(holder_list) == 16:
                holder_list = _optimize_one_list(copy.deepcopy(holder_list))
                complete_runs.append(copy.deepcopy(holder_list[0]))
                holder_list.clear()
            i = 0
            while ('single_runs_truck_requirement' in locals() and i < (len(single_runs_truck_requirement[0]) - 1)) \
                    or i < (len(single_runs_truck_requirement[0]) - 1):
                for i in range(len(single_runs_truck_requirement[0])):
                    if single_runs_truck_requirement[0][i] is None:
                        del single_runs_truck_requirement[0][i]
                        break
                    else:
                        continue
                if len(single_runs_truck_requirement[0]) == 0:
                    del single_runs_truck_requirement[0]
                if len(single_runs_truck_requirement) == 0:
                    del single_runs_truck_requirement
    while 'single_runs_no_requirement' in locals() \
            or 'single_runs_truck_requirement' in locals() \
            or 'single_runs_sister_requirement' in locals():
        if 'single_runs_sister_requirement' in locals():
            if len(single_runs_sister_requirement[0]) > 0:
                for i in range(len(single_runs_sister_requirement[0])):
                    if len(holder_list) < 16:
                        if single_runs_sister_requirement[0][i] is not None:
                            holder_list.append(copy.deepcopy(single_runs_sister_requirement[0][i]))
                            single_runs_sister_requirement[0][i] = None
                        else:
                            del single_runs_sister_requirement[0][i]
                            break
                    else:
                        break
                if len(holder_list) == 16:
                    holder_list = _optimize_one_list(copy.deepcopy(holder_list))
                    complete_runs.append(copy.deepcopy(holder_list[0]))
                    holder_list.clear()
            else:
                del single_runs_sister_requirement
                break
            i = 0
            while ('single_runs_sister_requirement' in locals() and i < (len(single_runs_sister_requirement[0]) - 1)) \
                    or (i < (len(single_runs_sister_requirement[0]) - 1)):
                for i in range(len(single_runs_sister_requirement[0])):
                    if single_runs_sister_requirement[0][i] is None:
                        del single_runs_sister_requirement[0][i]
                        break
                    else:
                        continue
                if len(single_runs_sister_requirement[0]) == 0:
                    del single_runs_sister_requirement[0]
                    if len(single_runs_sister_requirement) == 0:
                        del single_runs_sister_requirement
                else:
                    break
        elif 'single_runs_no_requirement' in locals():
            if len(single_runs_no_requirement[0]) > 0:
                for i in range(len(single_runs_no_requirement[0])):
                    if len(holder_list) < 16:
                        if single_runs_no_requirement[0][i] is not None:
                            holder_list.append(copy.deepcopy(single_runs_no_requirement[0][i]))
                            single_runs_no_requirement[0][i] = None
                        else:
                            del single_runs_no_requirement[0][i]
                            break
                    else:
                        break
                if len(holder_list) == 16:
                    holder_list = _optimize_one_list(copy.deepcopy(holder_list))
                    complete_runs.append(copy.deepcopy(holder_list[0]))
                    holder_list.clear()
            else:
                del single_runs_no_requirement
                break
            i = 0
            while ('single_runs_no_requirement' in locals() and i < (len(single_runs_no_requirement[0]) - 1)) \
                    or (i < (len(single_runs_no_requirement[0]) - 1)):
                for i in range(len(single_runs_no_requirement[0])):
                    if single_runs_no_requirement[0][i] is None:
                        del single_runs_no_requirement[0][i]
                        break
                    else:
                        continue
                if len(single_runs_no_requirement[0]) == 0:
                    del single_runs_no_requirement[0]
                    if len(single_runs_no_requirement) == 0:
                        del single_runs_no_requirement
                else:
                    break
        else:
            if len(single_runs_truck_requirement[0]) > 0:
                for i in range(len(single_runs_truck_requirement[0])):
                    if len(holder_list) < 16:
                        if single_runs_truck_requirement[0][i] is not None:
                            holder_list.append(copy.deepcopy(single_runs_truck_requirement[0][i]))
                            single_runs_truck_requirement[0][i] = None
                        else:
                            del single_runs_truck_requirement[0][i]
                            break
                    else:
                        break
                if len(holder_list) == 16:
                    holder_list = _optimize_one_list(copy.deepcopy(holder_list))
                    complete_runs.append(copy.deepcopy(holder_list[0]))
                    holder_list.clear()
            else:
                del single_runs_truck_requirement
                break
            i = 0
            while ('single_runs_truck_requirement' in locals() and i < (len(single_runs_truck_requirement[0]) - 1)) \
                    or (i < (len(single_runs_truck_requirement[0]) - 1)):
                for i in range(len(single_runs_truck_requirement[0])):
                    if single_runs_truck_requirement[0][i] is None:
                        del single_runs_truck_requirement[0][i]
                        break
                    else:
                        continue
                if len(single_runs_truck_requirement[0]) == 0:
                    del single_runs_truck_requirement[0]
                    if len(single_runs_truck_requirement) == 0:
                        del single_runs_truck_requirement
                else:
                    break
    if len(holder_list) > 0:
        holder_list = _optimize_one_list(copy.deepcopy(holder_list))
        complete_runs.append(copy.deepcopy(holder_list[0]))
        holder_list.clear()
    return complete_runs
