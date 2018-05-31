from flask import Flask, request, make_response

from wisley.bus_layer import BL_Plants
from wisley.bus_layer import BL_GIS
from wisley.bus_layer import BL_Route
from wisley.models import Node

import jsonpickle

from voluptuous import Schema, MultipleInvalid, Coerce, Required


app = Flask(__name__)


@app.route('/route/plant')
def flower_bed_route():

    """@app.route('/route/plant') takes
    plant (plant name number, coercible to integer)
    lat (latitude, coercible to float)
    long (longitude, coercible to float)
    Returns a Route object containing information about the route from the location given in
    the lat and long parameters to the closest instance of the plant given in the plant parameter"""

    # Define validation schema
    schema = Schema({
        Required('plant'): Coerce(int),
        Required('lat'): Coerce(float),
        Required('long'): Coerce(float)
    })

    # Validate and return a Bad Request error if necessary
    try:
        schema(request.args.to_dict())

    except MultipleInvalid as err:

        resp = handle_exception(err, '400')

    else:

        # Call business layer method and return an Internal Server Error if anything goes wrong
        try:
            f_bed_route = bl.get_flower_bed_route(request.args['plant'], Node(0, request.args['long'],
                                                                              request.args['lat'], ''))
            resp = get_response(f_bed_route)

        except Exception as err:
            resp = handle_exception(err, '500')

    return resp


@app.route('/route/poi')
def poi_route():

    """@app.route('/route/poi') takes
    poi_id (point of interest id, coercible to integer)
    lat (latitude, coercible to float)
    long (longitude, coercible to float)
    Returns a Route object containing information about the route from the location given in
    the lat and long parameters to point of interest given in the  poi_id parameter"""

    # Define validation schema
    schema = Schema({
        Required('poi_id'): Coerce(int),
        Required('lat'): Coerce(float),
        Required('long'): Coerce(float)
    })

    # Validate and return a Bad Request error if necessary
    try:
        schema(request.args.to_dict())

    except MultipleInvalid as err:

        resp = handle_exception(err, '400')

    else:

        # Call business layer method and return an Internal Server Error if anything goes wrong
        try:
            route = bl.get_poi_route(request.args['poi_id'], Node(0, request.args['long'], request.args['lat'], ''))
            resp = get_response(route)

        except Exception as err:
            resp = handle_exception(err, '500')

    return resp


@app.route('/plant/exact')
def get_plant():

    """@app.route('/plant/exact') takes
    name (preferred common name, string)
    Returns a Plant object, fully populated if plant was found by matching name parameter (exact matching only),
    or an empty Plant object if the plant was not found"""

    # Define validation schema
    schema = Schema({
        Required('name'): str
    })

    # Validate and return a Bad Request error if necessary
    try:
        schema(request.args.to_dict())

    except MultipleInvalid as err:

        resp = handle_exception(err, '400')

    else:

        # Call business layer method and return an Internal Server Error if anything goes wrong
        try:
            plant = bl.get_plant(request.args['name'])
            resp = get_response(plant)

        except Exception as err:
            resp = handle_exception(err, '500')

    return resp




@app.route('/list/poi')
def points_of_int():
    """@app.route('/list/poi') takes
    lat (latitude, coercible to float)
    long (longitude, coercible to float)
    n (max number of items wanted, coercible to int, n=0 returns all)
    Returns a list of Node objects representing a maximum of n points of interest, sorted by proximity to lat and long,
    closest first"""

    # Define validation schema
    schema = Schema({
        Required('lat'): Coerce(float),
        Required('long'): Coerce(float),
        Required('n'): Coerce(int)
    })

    # Validate and return a Bad Request error if necessary
    try:
        schema(request.args.to_dict())

    except MultipleInvalid as err:

        resp = handle_exception(err, '400')

    else:

        # Call business layer method and return an Internal Server Error if anything goes wrong
        try:
            points = bl.get_points_of_interest(Node(0, request.args['long'], request.args['lat'], ''),
                                               request.args['n'])
            resp = get_response(points)

        except Exception as err:
            resp = handle_exception(err, '500')

    return resp


@app.route('/list/flower_bed')
def flower_bed_list():
    """@app.route('/list/flower_bed') takes
    plant (plant name number, coercible to integer)
    lat (latitude, coercible to float)
    long (longitude, coercible to float)
    n (max number of items wanted, coercible to int, n=0 returns all)
    Returns a list of Node objects representing a maximum of n flower beds which contain the given plant,
    sorted by proximity to lat and long, closest first"""

    # Define validation schema
    schema = Schema({
        Required('plant'): Coerce(int),
        Required('lat'): Coerce(float),
        Required('long'): Coerce(float),
        Required('n'): Coerce(int)
    })

    # Validate and return a Bad Request error if necessary
    try:
        schema(request.args.to_dict())

    except MultipleInvalid as err:

        resp = handle_exception(err, '400')

    else:

        # Call business layer method and return an Internal Server Error if anything goes wrong
        try:
            flower_beds = bl.get_flower_beds(Node(0, request.args['long'], request.args['lat'], ''),
                                             request.args['plant'], request.args['n'])
            resp = get_response(flower_beds)

        except Exception as err:
            resp = handle_exception(err, '500')

    return resp

# *********

@app.route('/plants')
def get_plants():

    """@app.route('/plant/list') takes
    search_string (search string, string)
    n (max number of records required, coercible to int, n=0 returns all
    Searches the Preferred Common Name, Accepted Botanical Name, Synonyms and Common Names fields for the given search
    string (not case sensitive.  Returns a list of populated Plant objects, representing the first n instances found.
    If the search_string is not found, an empty list is returned.  If n=0, all matches are returned."""

    # Define validation schema
    schema = Schema({
        Required('search_string'): str,
        Required('n'): Coerce(int)
    })

    # Validate and return a Bad Request error if necessary
    try:
        schema(request.args.to_dict())

    except MultipleInvalid as err:

        resp = handle_exception(err, '400')

    else:

        # Call business layer method and return an Internal Server Error if anything goes wrong
        try:
            bl = BL_Plants()
            plants = bl.get_plant_list(request.args['search_string'], request.args['n'])
            resp = get_response(plants)

        except Exception as err:
            resp = handle_exception(err, '500')

    return resp

@app.route('/beds')
def get_beds():

    bl = BL_GIS(Node(0, request.args['long'], request.args['lat'], ''))

    beds = bl.get_flower_beds(request.args['name'], request.args['n'])

    resp = get_response(beds)

    return resp


@app.route('/places')
def get_places():

    bl = BL_GIS(Node(0, request.args['long'], request.args['lat'], ''))

    places = bl.get_places(request.args['n'])

    resp = get_response(places)

    return resp


@app.route('/route/bed')
def route_bed():

    bl = BL_Route(Node(0, request.args['long'], request.args['lat'], ''))

    route = bl.get_bed_route(request.args['id'])

    resp = get_response(route)

    return resp


@app.route('/route/place')
def route_place():

    bl = BL_Route(Node(0, request.args['long'], request.args['lat'], ''))

    route = bl.get_place_route(request.args['id'])

    resp = get_response(route)

    return resp


@app.route('/plants/seasonal')
def plants_seasonal():

    schema = Schema({
        Required('month'): Coerce(int),
        Required('n'): Coerce(int)
    })

    # Validate and return a Bad Request error if necessary
    try:
        schema(request.args.to_dict())

    except MultipleInvalid as err:

        resp = handle_exception(err, '400')

    else:

        # Call business layer method and return an Internal Server Error if anything goes wrong
        try:

            bl = BL_GIS(Node(0,'','',''))

            plants = bl.get_seasonal_plants(request.args['month'], request.args['n'])

            resp = get_response(plants)

        except Exception as err:

            resp = handle_exception(err, '500')

    return resp


@app.route('/plants/seasonal/near_me')
def plants_seasonal_near_me():

    schema = Schema({
        Required('month'): Coerce(int),
        Required('lat'): Coerce(float),
        Required('long'): Coerce(float),
        Required('n'): Coerce(int)
    })

    # Validate and return a Bad Request error if necessary
    try:
        schema(request.args.to_dict())

    except MultipleInvalid as err:

        resp = handle_exception(err, '400')

    else:

        # Call business layer method and return an Internal Server Error if anything goes wrong
        try:

            bl = BL_GIS(Node(0, request.args['long'], request.args['lat'], ''))

            plants = bl.get_seasonal_plants_near_me(request.args['month'], request.args['n'])

            resp = get_response(plants)

        except Exception as err:

            resp = handle_exception(err, '500')

    return resp


def get_response(resp_obj):

    # Success!  Encode response and set up a Response object
    # Status code will be 200
    resp = make_response(jsonpickle.encode(resp_obj))
    resp.mimetype = 'application/json'

    return resp


def handle_exception(err, code):

    # Failure! Encode error message and set up status
    print("Exception: ", err)

    resp = make_response(jsonpickle.encode(str(err)))
    resp.mimetype = 'application/json'
    resp.status = code

    return resp


if __name__ == '__main__':
    app.run()
