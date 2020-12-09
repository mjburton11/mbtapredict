#!api_objects.py
import jsonapi_requests

from mbtapredict.common import MbtaBase

mbta_api_config = jsonapi_requests.orm.OrmApi.config({
    'API_ROOT': 'https://api-v3.mbta.com',
})

class Stop(jsonapi_requests.orm.ApiModel, MbtaBase):
    class Meta:
        type = 'stop'
        path = 'stops'
        api = mbta_api_config

    name = jsonapi_requests.orm.AttributeField('name')
    @classmethod
    def filter(cls, **kwargs):
        return cls.get_list(params=cls.json_filter_params(**kwargs))

class Route(jsonapi_requests.orm.ApiModel, MbtaBase):
    class Meta:
        type = 'route'
        path = 'routes'
        api = mbta_api_config

    route_dict = {'LightRail': '0', 'HeavyRail': '1', 'CommuterRail': '2',
                  'Bus': '3', 'Ferry': '4'}

    long_name = jsonapi_requests.orm.AttributeField('long_name')
    rtype = jsonapi_requests.orm.AttributeField('type')
    direction_names = jsonapi_requests.orm.AttributeField('direction_names')
    direction_destinations = jsonapi_requests.orm.AttributeField('direction_destinations')

    @property
    def name(self):
        return self.long_name

    # create a sepaate method that wraps the filter method and
    # specifically is meant to handle the route types since they
    # are returned by json as a integer but are commonly referred to
    # as a string
    @classmethod
    def filter_route_types(cls, route_types='all'):
        if route_types == 'all':
            return cls.filter()

        if isinstance(route_types, str):
            route_types = [route_types]
        if not isinstance(route_types, list):
            raise ValueError('`route types must be list of strings or string`')

        route_inds = [cls.route_dict[k] for k in route_types]
        return cls.filter(type=route_inds)

    @classmethod
    def filter(cls, **kwargs):
        return cls.get_list(params=cls.json_filter_params(**kwargs))

class Prediction(jsonapi_requests.orm.ApiModel, MbtaBase):
    class Meta:
        type = 'prediction'
        path = 'predictions'
        api = mbta_api_config

    departure_time = jsonapi_requests.orm.AttributeField('departure_time')
    # don't actually need this but it is a way to unit test that it was called
    # correctly
    direction_id = jsonapi_requests.orm.AttributeField('direction_id')

    @property
    def departure_time_str(self):
        # depature time format is always 'YYYY-mm-ddTHH:MM:SS-MM:SS'
        # this will just return the hour, minute and second
        return self.departure_time.split('T')[-1].split('-')[0]

    # I want a separate method that will return the next prediction
    # and is different from the more general filter method
    @classmethod
    def filter_next_prediction(cls, **kwargs):
        params = cls.json_filter_params(**kwargs)
        params['page[limit]'] = 1
        pred = cls.get_list(params=params)

        # if the T is not running pred is an empty list
        if not pred:
            return None
        else:
            return pred[0]

    @classmethod
    def filter(cls, **kwargs):
        return cls.get_list(params=cls.json_filter_params(**kwargs))
