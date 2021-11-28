import copy
import csv
import sys
import config
import Utility
import HashTable
import Truck
import Package
import Graph
import Optimize

''' Name: James Mills
    Date: 10/2021
    Student ID: 000955354 
'''


# takes PackageFile.csv and reads it and parses the info into a list of Package objects.
# time complexity is O(1) due to the csv file being static.
def import_package_to_list_of_package_objects():
    holder_list = []
    with open("Files/PackageFile.csv", 'r') as csv_file:
        read_csv = csv.reader(csv_file, delimiter=',')
        for row in read_csv:
            package = Package.Package(row[0])
            package.address = row[1]
            package.city = row[2]
            package.state = row[3]
            package.zip = row[4]
            package.deadline = Utility.backwards_pretty_time_conversion(row[5])
            package.weight = row[6]
            try:
                test = row[7]  # looks into the special notes section and adjusts the Package attributes where needed
                test = []
                for i in range(7, len(row)):
                    test.append(row[i])
                stuff = ''.join(test)
                package.handle_special_notes(stuff)
            except IndexError:
                # should never happen, if error does occur it's due to no notes, so package is set at hub
                package.status = Package.Status(1)
            finally:
                holder_list.append(package)
    return holder_list


# adds the above created package list to the hash table for easy searching.
# time complexity is O(n) due to list of packages length
def add_packages_to_hash_table(table, list_of_packages):
    for i in range(len(list_of_packages)):
        table.insert(list_of_packages[i].get_package_id(), list_of_packages[i])


# creates a distance dictionary containing the distances from the csv file and also fills out the missing
# bottom half of the table since it is bi-directional.
# time complexity is O(n**2) due to looping through the list of values once for each value.
def create_distance_dictionary_lookup_from_file():
    dictionary = {}
    distances = [[0] * 27 for _ in range(27)]
    names = []
    addresses = []
    with open("Files/DistanceTable.csv", 'r') as csv_file:
        read_csv = csv.reader(csv_file, delimiter=';')
        i = 0
        for row in read_csv:
            name = row[0]
            names.append(name)
            address = row[1]
            addresses.append(address)
            temp = row[2]
            temp = temp.split(",")
            distances[i] = temp
            dictionary[name] = [address, distances[i]]
            i += 1
        for r in range(len(distances) - 1, -1, -1):  # building the rest of the distance table
            for col in range(len(distances[r])):
                if distances[r][col] != 0.0:
                    temp_holder = distances[r][col]
                    distances[col][r] = temp_holder
    dictionary.clear()
    for j in range(len(names)):
        dictionary[names[j]] = [addresses[j], distances[j]]
    return dictionary


# takes the distance dictionary and then creates a Graph object with Vertex objects each representing a location.
# it also creates a master list of all names and a list of all addresses that are both sorted in the same order.
# it outputs to a master graph object that is used within the program.
# time complexity is O(n**2) due to the while loop with a nested for loop within.
def create_master_map_area():
    graph = Graph.Graph()
    distance_names = [x[:] for x in config.distance_dictionary.keys()]
    addresses_1 = [x[:] for x in config.distance_dictionary.values()]
    distances_1 = [y[:] for y in config.distance_dictionary.values()]
    addresses = ["N/A"] * 27
    distances = [[0] * 27] * 27
    for j in range(len(addresses_1)):
        addresses[j] = addresses_1[j].pop(0)
    for m in range(len(distances_1)):
        distances[m] = distances_1[m].pop(1)
    del addresses_1, distances_1
    for i in range(len(distance_names)):
        if i == 0:
            vertex_temp = Graph.Vertex(distance_names[i], addresses[i], True)
        else:
            vertex_temp = Graph.Vertex(distance_names[i], addresses[i])
        graph.add_vertex(vertex_temp)
    i = 0
    while i < len(distances):
        for z in range(len(distance_names)):
            vertex_a = graph.lookup_vertex_by_label(distance_names[i])
            vertex_b = graph.lookup_vertex_by_label(distance_names[z])
            if vertex_a != vertex_b:
                graph.add_undirected_edge(vertex_a, vertex_b, distances[i][z])
        i += 1
    return graph, distance_names, addresses


'''
main program that is ran to simulate the work day flow. It takes a end time that the day is ran until and will
begin the process of creating the package list, hash table, distance table, graph object and trucks. 
times are all calculated in minutes of the day and then converted to military time when displayed. 
the start of the day is always at 8:00 am or 480. It will create the load lists which are static then uses the
optimization algorithm to sort the made lists into an order that minimizes distance travelled. Then the trucks
are loaded with the resulting sorted lists and sent out on a delivery route and deliver packages. Time is checked
against the end time given as input at each stop the trucks make. If the current time is past the end time, the 
delivery stops and the packages are not delivered and the truck is left. In order to minimize miles, the trucks 
are both left out on their final prospective runs. All 40 packages are delivered on time within their specifications.
miles and time are both treated as floats and then rounded off at the end or when displayed.
this function is also used to check package(s) at a given time and that time is passed as the end time.
time complexity is O(n**2) due to while loop with nested for loops and also due to the optimization algorithm having
a O(n**2) complexity as well.'''


def run_simulation_manual_loading(time_in_minutes_to_run_until):
    config.sister_package_list = []  # list of sister packages to be delivered together
    config.master_package_list = import_package_to_list_of_package_objects()  # creates package objects
    config.sister_package_list = set(copy.deepcopy(config.sister_package_list))  # makes sister list unique
    config.hash_table = HashTable.HashTable(len(config.master_package_list))  # creates hash table
    config.master_package_list[8].address = "410 S State St"  # address to be corrected for package # 9
    config.master_package_list[8].zip = "84111"  # zip to be corrected for package # 9
    add_packages_to_hash_table(config.hash_table, config.master_package_list)  # adds package list to hash table
    config.distance_dictionary = create_distance_dictionary_lookup_from_file()  # creates distance dictionary
    config.area_graph_object, config.master_names, config.master_addresses = create_master_map_area()
    # above line creates graph area for the routes
    config.truck_1 = Truck.Truck(1)
    config.truck_2 = Truck.Truck(2)
    config.truck_3 = Truck.Truck(3)
    # above line creates the truck objects. Truck 3 is not used since there are only two drivers
    config.start_time = 480.0  # start time of 8:00 am
    config.total_miles_driven = 0.0  # miles total starts at 0
    for i in range(len(config.master_package_list)):
        config.master_package_list[i].update_package_at_time(config.start_time)
    truck_1_miles = []  # miles holder for each run the truck makes for display at the end
    truck_2_miles = []
    packages_for_first_run_truck_2 = [1, 13, 14, 15, 16, 19, 20, 29, 30, 31, 34, 37, 40, 39, 35, 33]
    packages_for_first_run_truck_1 = [6, 25, 12, 11, 10, 8, 7, 5, 4, 2]
    packages_for_second_run_truck_2 = [28, 32, 3, 18, 36, 38, 27, 26, 24, 23, 22, 21, 17, 12, 9]
    Utility.turn_list_of_package_ids_to_list_of_packages(packages_for_first_run_truck_2)
    run_2_1 = Optimize._optimize_one_list(packages_for_first_run_truck_2)
    Utility.turn_list_of_package_ids_to_list_of_packages(packages_for_first_run_truck_1)
    run_1_1 = Optimize._optimize_one_list(packages_for_first_run_truck_1)
    Utility.turn_list_of_package_ids_to_list_of_packages(packages_for_second_run_truck_2)
    run_2_2 = Optimize._optimize_one_list(packages_for_second_run_truck_2)
    end_time_truck_1_load_1 = 0
    end_time_truck_2_load_1 = 0
    end_time_truck_2_load_2 = 0
    while config.start_time <= time_in_minutes_to_run_until:
        config.truck_2.load_packages_in_truck(run_2_1[0])
        start_time_truck_2_load_1 = config.start_time
        end_time_truck_2_load_1 = config.truck_2 \
            .run_delivery_route(start_time_truck_2_load_1, time_in_minutes_to_run_until)
        truck_2_miles.append(int(copy.deepcopy(config.truck_2.miles_driven)))
        number_to_subtract = config.truck_2.miles_driven
        if end_time_truck_2_load_1 >= time_in_minutes_to_run_until:
            config.start_time = max(end_time_truck_1_load_1, end_time_truck_2_load_1, end_time_truck_2_load_2)
            break
        start_time_truck_1_load_1 = Utility.sweep_the_floors(config.start_time)
        for i in range(len(config.master_package_list)):
            config.master_package_list[i].update_package_at_time(start_time_truck_1_load_1)
        config.truck_1.load_packages_in_truck(run_1_1[0])
        end_time_truck_1_load_1 = config.truck_1 \
            .run_delivery_route_make_driver_walk_back(start_time_truck_1_load_1, time_in_minutes_to_run_until)
        truck_1_miles.append(int(config.truck_1.miles_driven))
        if end_time_truck_1_load_1 >= time_in_minutes_to_run_until:
            config.start_time = max(end_time_truck_1_load_1, end_time_truck_2_load_1, end_time_truck_2_load_2)
            break
        for i in range(len(config.master_package_list)):
            config.master_package_list[i].update_package_at_time(end_time_truck_1_load_1)
        config.truck_2.load_packages_in_truck(run_2_2[0])
        end_time_truck_2_load_2 = config.truck_2 \
            .run_delivery_route_make_driver_walk_back(end_time_truck_2_load_1, time_in_minutes_to_run_until)
        truck_2_miles.append(int((config.truck_2.miles_driven - number_to_subtract)))
        if end_time_truck_2_load_2 >= time_in_minutes_to_run_until:
            config.start_time = max(end_time_truck_1_load_1, end_time_truck_2_load_1, end_time_truck_2_load_2)
            break
        config.start_time = max(end_time_truck_1_load_1, end_time_truck_2_load_1, end_time_truck_2_load_2)
        if config.start_time <= time_in_minutes_to_run_until:
            if Utility.is_packages_delivered(config.master_package_list):
                break
            else:
                continue
    config.total_miles_driven += (config.truck_1.miles_driven
                                  + config.truck_2.miles_driven
                                  + config.truck_3.miles_driven)
    late_counter = 0
    met_deadline_counter = 0
    never_made_it_counter = 0
    for i in range(len(config.master_package_list)):
        print(config.master_package_list[i])
        info_holder = config.master_package_list[i].was_package_late()
        if info_holder == "Met deadline!!":
            met_deadline_counter += 1
        elif info_holder == "PACKAGE LATE!!! BAD DRIVER!!":
            late_counter += 1
        else:
            never_made_it_counter += 1
        print("\nPackage #%d : %s" % (config.master_package_list[i].get_package_id(),
                                      info_holder))
    print("\nTrucks current location is: ")
    print("Truck #1: ", config.truck_1.current_location)
    print("Truck #2: ", config.truck_2.current_location)
    print("Truck #3: ", config.truck_3.current_location)
    print("\nTrucks total individual mileage is: ")
    print("Truck #1: %0.3f" % config.truck_1.miles_driven)
    print("Truck #2: %0.3f" % config.truck_2.miles_driven)
    print("Truck #3: %0.3f" % config.truck_3.miles_driven)
    print("\nTrucks mileage per route is:")
    print("Truck #1:", truck_1_miles)
    print("Truck #2:", truck_2_miles)
    print("\nTotal Packages Met Deadline: %d" % met_deadline_counter)
    print("Total Packages Delivered Late: %d" % late_counter)
    print("Total Packages Never Delivered: %d" % never_made_it_counter)
    print("\nThe day ran until %s and the total miles ran was %0.3f\n"
          % (Utility.pretty_time_conversion(config.start_time), config.total_miles_driven))
    print("\nPlease make sure someone gets the trucks towed back to the hub.")


'''
this was version #1 of the simulation run utilizing the version #1 of the optimization algorithm. It loads the truck
it loads the trucks completely by automation and runs the optimization function each time before the truck loads
are deciphered. If there are any priority packages ( less than 3 hours til delivery deadline ) they are delivered
by themselves, causing the trucks to make more runs but also utilize both trucks more efficiently and have a more
productive labor usage. All trucks make it back to the hub safely and all packages are delivered on time. This can
also be used to check package(s) at a given time as well. Everything is automated so the package list can be changed
and updated and the truck amount can also be changed or updated. This would account better if a bigger area was used
or more trucks or more packages and presents a more real world scenario of a actual delivery route. The main difference
between the this one and the version #2 is the complete automation of the process with no load lists being already
decided and that all trucks make it back safely and all packages are delivered on time. The mileage ends up being
a little higher due to the extra delivery runs made in order to get priority packages out quicker.
# time complexity is O(n**3) due the extra complexity of the optimization algorithm.'''


def run_simulation_optimization_version(time_in_minutes_to_run_until):
    config.sister_package_list = []
    config.master_package_list = import_package_to_list_of_package_objects()
    config.sister_package_list = set(copy.deepcopy(config.sister_package_list))
    config.hash_table = HashTable.HashTable(len(config.master_package_list))
    config.master_package_list[8].address = "410 S State St"
    config.master_package_list[8].zip = "84111"
    add_packages_to_hash_table(config.hash_table, config.master_package_list)
    config.distance_dictionary = create_distance_dictionary_lookup_from_file()
    config.area_graph_object, config.master_names, config.master_addresses = create_master_map_area()
    config.truck_1 = Truck.Truck(1)
    config.truck_2 = Truck.Truck(2)
    config.truck_3 = Truck.Truck(3)
    config.start_time = 480.0
    config.total_miles_driven = 0.0
    for i in range(len(config.master_package_list)):
        config.master_package_list[i].update_package_at_time(config.start_time)
    truck_1_miles = []
    truck_2_miles = []
    while config.start_time <= time_in_minutes_to_run_until:

        config.list_of_runs_for_trucks = Optimize.optimize_the_load(copy.deepcopy(config.master_package_list),
                                                                    copy.copy(config.start_time), 2)
        if len(config.list_of_runs_for_trucks) > 1:
            hey = True
            for k in range(len(config.list_of_runs_for_trucks[0])):
                if config.list_of_runs_for_trucks[0][k].truck_requirement is False:
                    continue
                else:
                    hey = False
            if hey:
                config.truck_1.load_packages_in_truck(config.list_of_runs_for_trucks[0])
                config.truck_2.load_packages_in_truck(config.list_of_runs_for_trucks[1])
            else:
                config.truck_1.load_packages_in_truck(config.list_of_runs_for_trucks[1])
                config.truck_2.load_packages_in_truck(config.list_of_runs_for_trucks[0])
        else:
            if config.truck_2.left_hub:
                config.truck_1.load_packages_in_truck(config.list_of_runs_for_trucks[0])
            else:
                config.truck_2.load_packages_in_truck(config.list_of_runs_for_trucks[0])
        copy_of_start_time_before_delivery_1 = config.start_time
        copy_of_start_time_before_delivery_2 = config.start_time
        if config.truck_1.truck_has_packages():
            miles_to_subtract = config.truck_1.miles_driven
            copy_of_start_time_before_delivery_1_1 = \
                config.truck_1.run_delivery_route(copy_of_start_time_before_delivery_1,
                                                  time_in_minutes_to_run_until)
            truck_1_miles.append(int(config.truck_1.miles_driven - miles_to_subtract))
            if copy_of_start_time_before_delivery_1_1 > time_in_minutes_to_run_until:
                config.start_time = copy_of_start_time_before_delivery_1_1
                break
        if config.truck_2.truck_has_packages():
            miles_to_subtract = config.truck_2.miles_driven
            copy_of_start_time_before_delivery_2_2 = \
                config.truck_2.run_delivery_route(copy_of_start_time_before_delivery_2, time_in_minutes_to_run_until)
            truck_2_miles.append(int(config.truck_2.miles_driven - miles_to_subtract))
            if copy_of_start_time_before_delivery_2_2 > time_in_minutes_to_run_until:
                config.start_time = copy_of_start_time_before_delivery_2_2
                break
        if ('copy_of_start_time_before_delivery_1_1' in locals()) \
                and ('copy_of_start_time_before_delivery_2_2' in locals()):
            config.start_time = max(copy_of_start_time_before_delivery_1_1, copy_of_start_time_before_delivery_2_2)
        else:
            try:
                config.start_time = copy_of_start_time_before_delivery_1_1
                config.start_time = copy_of_start_time_before_delivery_2_2
            except AttributeError:
                pass
            try:
                config.start_time = copy_of_start_time_before_delivery_2_2
                config.start_time = copy_of_start_time_before_delivery_1_1
            except AttributeError:
                pass
        if config.start_time <= time_in_minutes_to_run_until:
            if Utility.is_packages_delivered(config.master_package_list):
                break
            else:
                continue
    config.total_miles_driven += (config.truck_1.miles_driven
                                  + config.truck_2.miles_driven
                                  + config.truck_3.miles_driven)
    late_counter = 0
    met_deadline_counter = 0
    never_made_it_counter = 0
    for i in range(len(config.master_package_list)):
        print(config.master_package_list[i])
        info_holder = config.master_package_list[i].was_package_late()
        if info_holder == "Met deadline!!":
            met_deadline_counter += 1
        elif info_holder == "PACKAGE LATE!!! BAD DRIVER!!":
            late_counter += 1
        else:
            never_made_it_counter += 1
        print("\nPackage #%d : %s" % (config.master_package_list[i].get_package_id(),
                                      info_holder))
    print("\nTrucks current location is: ")
    print("Truck #1: ", config.truck_1.current_location)
    print("Truck #2: ", config.truck_2.current_location)
    print("Truck #3: ", config.truck_3.current_location)
    print("\nTrucks total individual mileage is: ")
    print("Truck #1: %0.3f" % config.truck_1.miles_driven)
    print("Truck #2: %0.3f" % config.truck_2.miles_driven)
    print("Truck #3: %0.3f" % config.truck_3.miles_driven)
    print("\nTrucks mileage per route is:")
    print("Truck #1:", truck_1_miles)
    print("Truck #2:", truck_2_miles)
    print("\nTotal Packages Met Deadline: %d" % met_deadline_counter)
    print("Total Packages Delivered Late: %d" % late_counter)
    print("Total Packages Never Delivered: %d" % never_made_it_counter)
    print("\nThe day ran until %s and the total miles ran was %0.3f\n"
          % (Utility.pretty_time_conversion(config.start_time), config.total_miles_driven))


# displays the status of a specific package at a specific time. Uses the simulation function with the specified
# time as the end time and then prints the specified package at the end using the hash table lookup.
# time complexity is O(n**2) due to the complexity of the simulation function.
def package_check_at_time(package_to_check, time_to_check):
    run_simulation_manual_loading(time_to_check)
    print("\nYour requested package status info below.")
    print(config.hash_table.search(package_to_check))


# displays the user interface for running the program. User inputs name and is greeted, then selects from running
# a full day, a partial day, or checking a specific package at a specific time. Interface runs until user inputs
# '4'. There is input validation requiring the user to input the correct numbers and times according to the given
# format.
# time complexity is O(n**2) due to the complexity of the simulation function.
def start_menu():
    user_name = input("What is your name? ")
    print("\nWelcome to the WGUPS program,", user_name)
    print('Designed exclusively by James Mills and c/o "Catch22 Software". ')
    print("Please read the following menu carefully and make your selection.")
    print("The work day begins at 08:00 regardless of time entered.")
    while True:
        print('\n1: Run full day "simulation". This will output all packages '
              'and their statuses as of EOD today -- 19:00')
        print('2: Check status of one package via package ID at a given time.')
        print('3: Check status of all packages at a given time of the day.')
        print('4: Exit the program.')
        try:
            selection = int(input("\nPlease make your selection: Numbers only please.\n"))
            if selection == 1:
                # run_simulation_optimization_version(1140) # this was version #1 of the simulation
                run_simulation_manual_loading(1140)
                continue
            elif selection == 2:
                print("Which package would you like to check?")
                print("Please use numbers to input package ID without any leading zeros.")
                package_to_check = int(input("Package #\n"))
                time_to_check = input("Please enter time to check status at: Use 12 hour time"
                                      " with a ':' between numbers and 'am' or 'pm' please.\n ")
                time_to_check = Utility.backwards_pretty_time_conversion(time_to_check)
                package_check_at_time(package_to_check, time_to_check)
                continue
            elif selection == 3:
                time_to_check = input("Please enter time to check status at: Use 12 hour time"
                                      " with a ':' between numbers and 'am' or 'pm' please.\n ")
                time_to_check = Utility.backwards_pretty_time_conversion(time_to_check)
                run_simulation_manual_loading(time_to_check)
                # run_simulation_optimization_version(time_to_check) # this was version #1 of the simulation
                continue
            elif selection == 4:
                print("Thank you for using the program!!! Have a curve-ball kinda day! ")
                sys.exit()
            else:
                print("Please try your selection again and read carefully.")
                continue
        except ValueError:
            print("Please try your selection again and read carefully.")
            continue


start_menu()
