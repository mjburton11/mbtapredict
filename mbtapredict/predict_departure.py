from mbtapredict.api_objects import Route, Prediction, Stop

def predict_departure():
    """
    This is the primary function that will prompt the user to select a route,
    stop and direction and will return the next departing time
    :return:
    """

    route = user_input_function(Route.filter_route_types, 'route',
                                route_types=['LightRail', 'HeavyRail'],
                                )
    stop = user_input_function(Stop.filter, 'stop', route=route.id,
                               )

    direction_names = route.direction_names
    direction_destinations = route.direction_destinations

    # if I'm at one of the end points of the line force me to go the other way
    # otherwise ask the user
    if stop.name in direction_destinations:
        loc_ind = direction_destinations.index(stop.name)
        dest_ind = 1 if loc_ind == 0 else 0
        direction = Direction(direction_destinations[dest_ind])
        print('You are at the end of the line at %s stop going to %s\n' % (stop.name, direction.name))

    else:
        direction = user_input_function(direction_func, 'direction',
                                        direction_destinations=direction_destinations,
                                        )

    direction_id = direction_names[direction_destinations.index(direction.name)]

    pred = Prediction.filter_next_prediction(stop=stop.id, direction_id=direction_id)
    if not pred:
        print('No available departure times at %s stop going to %s' % (stop.name, direction.name))
    else:
        print('The next train from %s stop going to %s is departing at %s' % (
            stop.name, direction.name, pred.departure_time_str))


# create a dummy class and function to work the the user_input_fuction nicely
class Direction:
    def __init__(self, name):
        self.name = name


def direction_func(direction_destinations=None):
    return [Direction(dd) for dd in direction_destinations]


def user_input_function(api_function, ux_word, user_input=None, **kwargs):
    """
    This function will take user inputs and return the desired api object

    :param api_function: the function that will return list of possible api objects
    :param ux_word: the word that the user will see when prompted (i.e. `stop`)
    :param user_input: to avoid direction typing in something everytime while
                       developing use this for convenience
    :param kwargs: kwargs for api_function call
    :return api_object: returns the api_object of whatever the user has selected
    """

    obj = api_function(**kwargs)
    obj_names = [oj.name for oj in obj]

    print('Which %s are you taking?' % ux_word)
    print('\n'.join(['%s' % nm for nm in obj_names]))

    if user_input is None:
        user_input = input('Please enter one of the %ss as a string: \n' % ux_word)

    if user_input not in obj_names:
        raise ValueError('%s is not in the list of available %ss' % (user_input, ux_word))
    else:
        print('You entered: %s\n' % user_input)

    # for some reason using [obj_names == user_input] didn't work for me
    # this seems a safer option for now
    return obj[obj_names.index(user_input)]


if __name__ == "__main__":

    predict_departure()

    # stps = Route.filter(type='0')
    # for st in stps: print(st.id)

