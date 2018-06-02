class BL_Plants(object):

    # Business logic class for dealing with the corresponding DAO_Plants data layer object.
    # Handles requests for list of plants that only involve the XML data source.

    def __init__(self):

        from wisley.data_access import DAO_Plants

        # Set up data access object (does not require location or database connection).
        self.db = DAO_Plants()

    def get_plant_list(self, search_string, n):

        # Pass parameters to corresponding data layer method.
        # Returns - a list of populated Plant objects, or an empty list if the search string was not found.

        plants = self.db.get_plants(search_string, n)

        return plants


class BL_PlantLists(object):

    # Business logic class for dealing with the corresponding DAO_PlantLists data layer object.
    # Handles requests for lists of plants with no spatial component.

    def __init__(self):

        from wisley.data_access import DAO_PlantLists

        # Set up a data access object and connect to db.
        self.db = DAO_PlantLists()

    def get_seasonal_plants(self, month, n):

        # Pass parameters to corresponding data layer method.
        # Returns - a list of Plant Objects representing the n seasonal plants,
        # or an empty list if the plant was not found.

        plants = self.db.get_seasonal_plants(month, n)

        return plants

    def get_bed_plants(self, id, n):

        # Pass parameters to corresponding data layer method.
        # Returns - a list of Plant Objects representing the n plant in bed with id,
        # or an empty list if the bed was not found or was empty.

        plants = self.db.get_bed_plants(id, n)

        return plants


class BL_GIS(object):

    # Business logic class for dealing with the corresponding DAO_GIS data layer object.
    # Handles requests for lists of flower beds and places near a location.

    def __init__(self, location):

        from wisley.data_access import DAO_GIS

        # Set up a data access object with location and connect to db.
        self.db = DAO_GIS(location)

    def get_flower_beds(self, plant, n):

        # Pass parameters to corresponding data layer method.
        # Returns - a list of Node Objects representing the n flower beds, or an empty list if the plant was not found.

        flower_beds = self.db.get_flower_beds(plant, n)

        self.db.db_close()

        return flower_beds

    def get_places(self, n):

        # Pass parameters to corresponding data layer method.
        # Returns - a list of Place Objects representing the n places, or an empty list not found.

        places = self.db.get_places(n)

        self.db.db_close()

        return places


class BL_Route(object):

    # Business logic class for dealing with the corresponding DAO_Route data layer object.
    # Handles requests for routes to flower beds and places.

    def __init__(self, location):

        from wisley.data_access import DAO_Route

        # Set up a data access object with location and connect to db
        self.db = DAO_Route(location)

    def get_place_route(self, id):

        # Get node closest to place and calculate route between location and given place
        route = self._get_route(self.db.find_nearest_place_node_id(id))
        # Populate destination details
        route.destination = self.db.get_place(id)

        return route

    def get_bed_route(self, id):

        # Get node closest to flower bed and calculate route between location and given flower bed
        route = self._get_route(self.db.find_nearest_bed_node_id(id))
        # Populate destination details
        route.destination = self.db.get_bed_centre(id)

        return route

    def _get_route(self, destination_node_id):

        import networkx as nx
        from wisley.models import Route

        # Arguments:
        # destination_node_id - identity of destination node
        # Returns - a Route object populated with the shortest route between location and destination_node_id

        # Read in network from database
        G = self.db.get_graph()

        # Find node closet to location for starting point
        start_node = self.db.find_nearest_node()

        route = Route()

        # Calculate shortest route and route length
        nodes = nx.astar_path(G, start_node.id, destination_node_id)
        route.length = nx.astar_path_length(G, start_node.id, destination_node_id)

        node1 = 0

        # Loop through nodes getting full details and directions from database

        for node in nodes:

            route.nodes.append(self.db.get_node_details(node))

            node2 = node

            if len(route.nodes) > 1:
                route.directions.append(self.db.get_directions(node1, node2))

            node1 = node

        return route
