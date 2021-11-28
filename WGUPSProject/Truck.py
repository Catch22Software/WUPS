import Package
import Graph
import config
import Utility


# class that holds the Truck object that transports the Package objects in the delivery business.
class Truck:
    # time complexity O(1)
    def __init__(self, number=1):
        self.truck_number = number
        self.load = []
        self.max_load = 16
        self.miles_driven = float(0.0)
        self.current_location = Graph.Vertex("Western Governors University", "4001 South 700 East", True)
        self.speed = 18
        self.left_hub = False

    # returns current location of truck
    # time complexity O(1)
    def truck_location(self):
        return self.current_location.label

    # adds distance traveled to total miles for truck and moves truck to next position
    # gets the mile value from current location to next and updates the total miles driven and also updates
    # the current time after driving. If the ending time happens in the middle of driving to location, the truck
    # finishes the drive to the location but does not deliver since the workers are no longer getting paid.
    # time complexity O(1)
    def move_truck_to_position(self, vector_name, current_time_in_minutes):
        self.miles_driven += config.area_graph_object \
            .return_distance_between_two_vertices(self.current_location.label, vector_name)
        current_time_in_minutes += Utility.convert_time_taken_into_minutes((config.area_graph_object
                                                                            .return_distance_between_two_vertices
                                                                            (self.current_location.label,
                                                                             vector_name)))
        self.current_location = config.area_graph_object.lookup_vertex_by_label(vector_name)
        return current_time_in_minutes

    # returns total miles driven by truck at an instant
    # time complexity O(1)
    def truck_distance_driven(self):
        return self.miles_driven

    # returns True if truck has packages or False if empty
    # time complexity O(1)
    def truck_has_packages(self):
        if len(self.load) == 0:
            return False
        else:
            return True

    # loads the packages into the truck as long as the total load is less than 17
    # and checks that the package does not have a unmet truck requirement before loading.
    # time complexity O(n) due to one for loop based on package list length
    def load_packages_in_truck(self, list_of_packages):
        if len(self.load) + len(list_of_packages) < 17:
            for i in list_of_packages:
                holder = config.hash_table.search(i.id)
                if holder.status == Package.Status(1):
                    if not holder.truck_requirement:
                        if self.truck_number == 1:
                            holder.status = Package.Status(2)
                        else:
                            holder.status = Package.Status(3)
                        self.load.append(holder)
                    else:
                        if holder.truck_requirement == str(self.truck_number):
                            holder.status = Package.Status(3)
                            self.load.append(holder)
            return "SUCCESSFULLY LOADED"
        else:
            return "ERROR!! PACKAGE AMOUNT OVER MAX LOAD OF 16!!"

    # removes package list from truck load and changes delivery status to delivered and sets time delivered
    # failsafe that wont let you deliver a package twice due to utilizing the hash table copy.
    # also wont allow you to deliver a package not on a truck already
    # time complexity O(n) due to one loop based on load list length.
    def deliver_packages(self, current_time_in_mins):
        for i in self.load:
            if i.status == Package.Status(2) or i.status == Package.Status(3):
                if self.current_location.address == i.address:
                    i.status = Package.Status(4)
                    i.time_delivered = current_time_in_mins
                    self.load.remove(i)
            elif i.status == Package.Status(4):
                return "You can't deliver a package that already has been delivered!!"
            else:
                return "Package either still at Hub or unavailable currently."

    # simulates truck running a delivery route. Packages are listed from start to finish in the truck load list.
    # moves truck from location to location in order to deliver packages.
    # updates the current time at each stop and only delivers the packages if it is not past the cut off time.
    # truck returns to the hub after delivering the last package with a final updated time and miles recorded.
    # time complexity O(n) due to length of list of load
    def run_delivery_route(self, current_time_in_minutes, cut_off_time):
        if self.left_hub:
            return "You cannot take a truck out that is already out!!!"
        else:
            self.left_hub = True
            while self.truck_has_packages():
                value = config.master_addresses.index(self.load[0].address)
                location_to_move_to = config.master_names[value]
                current_time_in_minutes = self.move_truck_to_position(location_to_move_to, current_time_in_minutes)
                self.deliver_packages(current_time_in_minutes)
                if current_time_in_minutes > cut_off_time:
                    return current_time_in_minutes
            self.move_truck_to_position('Western Governors University', current_time_in_minutes)
            self.left_hub = False
            return current_time_in_minutes

    # simulates truck running a delivery route. Packages are listed from start to finish in the truck load list.
    # moves truck from location to location in order to deliver packages.
    # updates the current time at each stop and only delivers the packages if it is not past the cut off time.
    # truck stays put after delivering the last package with a final updated time and miles recorded.
    # does not return to the hub in order to conserve mileage.
    # time complexity O(n) due to length of list of load
    def run_delivery_route_make_driver_walk_back(self, current_time_in_minutes, cut_off_time):
        if self.left_hub:
            return "You cannot take a truck out that is already out!!!"
        else:
            self.left_hub = True
            while self.truck_has_packages():
                value = config.master_addresses.index(self.load[0].address)
                location_to_move_to = config.master_names[value]
                current_time_in_minutes = self.move_truck_to_position(location_to_move_to, current_time_in_minutes)
                self.deliver_packages(current_time_in_minutes)
                if current_time_in_minutes > cut_off_time:
                    return current_time_in_minutes
            return current_time_in_minutes
