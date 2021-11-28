import copy
import enum
import Utility
import config


# class that holds the Package objects for the Truck objects to load and deliver
class Package:
    # time complexity O(1)
    def __init__(self, value):
        self.id = int(value)
        self.address = None
        self.city = None
        self.state = None
        self.zip = None
        self.deadline = None
        self.weight = None
        self.special_notes = "DNE"
        self.sister_packages = []
        self.status = Status(1)
        self.will_arrive_at = -1.0  # defaults to -1 to show not delivered or arrived at hub yet
        self.time_delivered = -1.0
        self.truck_requirement = False

    # checks for existence of sister packages that must be delivered together
    # and returns the list of package id's if available.
    # time complexity O(1)
    def has_sister_packages(self):
        if len(self.sister_packages) == 0:
            return False
        else:
            return self.sister_packages

    # returns status of package if it was delivered on time, late or never delivered.
    # time complexity O(1)
    def was_package_late(self):
        if self.status == Status(4):
            if self.time_delivered <= self.deadline:
                return "Met deadline!!"
            else:
                return "PACKAGE LATE!!! BAD DRIVER!!"
        elif self.time_delivered == -1:
            return "PACKAGE NEVER MADE IT :("
        else:
            "Package never delivered!"  # should NEVER happen

    # returns package id for given package
    # time complexity O(1)
    def get_package_id(self):
        return self.id

    # overridden str method to return package info nicely
    # time complexity O(1)
    def __str__(self):
        if self.status == Status(4):
            return "\nPackage ID: %d Package address: %s Package city: %s Package zip code: %s \n" \
                   "Package weight: %s Package DeadLine: %s Delivery Status: %s Time delivered: %s" \
                   % (self.id, self.address, self.city, self.zip, self.weight
                      , Utility.pretty_time_conversion(self.deadline)
                      , self.status, Utility.pretty_time_conversion(self.time_delivered))
        else:
            return "Package ID: %d Package address: %s Package city: %s Package zip code: %s \n" \
                   "Package weight: %s Package DeadLine: %s Delivery Status: %s" \
                   % (self.id, self.address, self.city, self.zip, self.weight
                      , Utility.pretty_time_conversion(self.deadline)
                      , self.status)

    # updates package info if it has not arrived at hub yet and updates special notes if applicable.
    # time complexity O(1)
    def update_package_at_time(self, current_time_in_minutes):
        if self.status == Status(0) and self.will_arrive_at <= current_time_in_minutes:
            self.status = Status(1)
            self.will_arrive_at = -1
            self.special_notes = "DNE"
        if self.get_package_id() in config.sister_package_list:
            self.special_notes = "SISTER PACKAGES INCLUDED"
            self.sister_packages = copy.deepcopy(config.sister_package_list)

    # takes special notes section from CSV file and parses it correctly and fills out the special notes attribute
    # along with other related ones correctly.
    # time complexity O(n) based on size of notes_string
    def handle_special_notes(self, notes_string):
        if "Delayed" in notes_string:
            notes = notes_string.split(" ")
            time = ' '.join([notes[-2], notes[-1]])
            updated_time = Utility.backwards_pretty_time_conversion(time)
            self.special_notes = "DELAYED"
            self.status = Status(0)
            self.will_arrive_at = updated_time
            return
        elif "delivered with" in notes_string:
            others = notes_string.split(",")
            check = others[0].split(" ")
            if check[-1].isdigit() and check[-1].isdigit() not in self.sister_packages:
                self.sister_packages.append(int(check[-1]))
                if check[-1] not in config.sister_package_list:
                    config.sister_package_list.append(int(check[-1]))
            if check[-2].isdigit() and check[-2].isdigit() not in self.sister_packages:
                self.sister_packages.append(int(check[-2]))
                if check[-2] not in config.sister_package_list:
                    config.sister_package_list.append(int(check[-2]))
            if check[-3].isdigit() and check[-3].isdigit() not in self.sister_packages:
                self.sister_packages.append(int(check[-3]))
                if check[-3] not in config.sister_package_list:
                    config.sister_package_list.append(int(check[-3]))
            if self.get_package_id() not in config.sister_package_list:
                config.sister_package_list.append(self.id)
            config.sister_package_list.sort()
            self.sister_packages.sort()
            self.special_notes = "SISTER PACKAGES INCLUDED"
        elif "truck" in notes_string:
            others = notes_string.split(" ")
            self.truck_requirement = others[-1]
            self.special_notes = "Truck # : %s" % others[-1]
        elif len(notes_string) <= 1:
            self.status = Status(1)
        else:
            self.special_notes = "INCORRECT ADDRESS"
            self.status = Status(0)
            self.will_arrive_at = 620.0

    # overrides the 'in' operator for package objects to determine containment.
    # time complexity O(n) at most if item is a list
    def __contains__(self, item):
        answer = False
        if isinstance(item, list):
            for i in range(len(list)):
                if isinstance(item[i], Package):
                    answer = item[i].id in self.id
                elif isinstance(item[i], int):
                    answer = item[i] in self.id
                else:
                    answer = False
                    break
            return answer
        else:
            if isinstance(item, Package):
                answer = item.id in self.id
            elif isinstance(item, int):
                answer = item in self.id
            else:
                pass
        return answer


# Delivery status options defined as an enum
class Status(enum.Enum):

    # time complexity O(1)
    def __str__(self):
        return str(self.name)

    AWAITING_ARRIVAL_TO_HUB = 0
    AT_HUB = 1
    EN_ROUTE_TRUCK_1 = 2
    EN_ROUTE_TRUCK_2 = 3
    DELIVERED = 4
