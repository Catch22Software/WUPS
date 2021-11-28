# class to create Vertex objects to fill Graph ( map ) object. ( Lysecky & Vahid, 2018 )
class Vertex:
    # time complexity O(1)
    def __init__(self, label, address, answer=False):
        self.label = label
        self.address = address
        self.is_hub_location = answer

    # time complexity O(1)
    def __str__(self):
        return str(self.label)


# class to create Graph object and hold adjacency lists along with weights ( distances ) between items.
# ( Lysecky & Vahid, 2018 )
class Graph:
    # time complexity O(1)
    def __init__(self):
        self.adjacency_list = {}
        self.edge_weights = {}

    # time complexity O(1)
    def add_vertex(self, new_vertex):
        self.adjacency_list[new_vertex] = []

    # time complexity O(1)
    def add_directed_edge(self, from_vertex, to_vertex, weight=1):
        self.edge_weights[(from_vertex, to_vertex)] = weight
        if to_vertex not in self.adjacency_list[from_vertex]:
            self.adjacency_list[from_vertex].append(to_vertex)

    # time complexity O(1)
    def add_undirected_edge(self, vertex_a, vertex_b, weight=1):
        self.add_directed_edge(vertex_a, vertex_b, weight)
        self.add_directed_edge(vertex_b, vertex_a, weight)

    # time complexity O(n) due to looping through distance table keys once
    def lookup_vertex_by_label(self, search_label):
        for i in self.adjacency_list.keys():
            if i.label == search_label:
                return i

    # time complexity O(n) due to calling the lookup function twice
    def return_distance_between_two_vertices(self, location_1, location_2):
        try:
            return float(self.edge_weights[self.lookup_vertex_by_label(location_1),
                                           self.lookup_vertex_by_label(location_2)])
        except KeyError:
            return 0.0
