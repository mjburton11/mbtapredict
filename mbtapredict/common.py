
class MbtaBase(object):
    @staticmethod
    def json_filter_params(**kwargs):
        """
        This will take keywords arguments and assign them to a parameter dict
        for a json_request filter call, i.e.
            keyword1=value1, keyword2=value2
            params={'filter[keyword1]': value1, 'filter[keyword2]': value2}

            if value of a keyword is a list it will assign a the value in the
            parameter dict a single string of the combined list separated by a
            comma
        :param kwargs: keyword arguments to be filters for json_request parameters
        :return dict: parameters for json_request call
        """

        params = dict()
        for kw, value in kwargs.items():
            # if I have a list, the json mbta parameter call expects the list to be a
            # single string separated by commas
            if isinstance(value, list):
                value = ','.join(value)
            if not isinstance(value, str):
                raise ValueError('keyword parameter must a string')

            params['filter[%s]' % kw] = value

        return params