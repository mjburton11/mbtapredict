import unittest
from unittest.mock import patch, Mock
import numpy as np
import sys
import os
import contextlib

from jsonapi_requests.request_factory import ApiClientError

from mbtapredict.api_objects import Stop, Route, Prediction
from mbtapredict.common import MbtaBase
from mbtapredict.predict_departure import user_input_function, predict_departure

@contextlib.contextmanager
def suppress_stdout(suppress=True, filename=os.devnull):
    std_ref = sys.stdout
    if suppress:
        sys.stdout = open(filename, 'w')
        yield
    sys.stdout.close()
    sys.stdout = std_ref

class StopTester(unittest.TestCase):
    def test_basic_functionality(self):
        stp = Stop.filter(id='place-harsq')[0]
        self.assertEqual('Harvard', stp.name)
        self.assertEqual('place-harsq', stp.id)

    def test_get_list(self):
        stps = Stop.filter(route='Red')
        stp_names = [st.name for st in stps]
        master_names = [
            'Alewife', 'Davis', 'Porter', 'Harvard', 'Central',
            'Kendall/MIT', 'Charles/MGH', 'Park Street',
            'Downtown Crossing', 'South Station',
            'Broadway', 'Andrew', 'JFK/UMass', 'Savin Hill',
            'Fields Corner', 'Shawmut', 'Ashmont', 'North Quincy',
            'Wollaston', 'Quincy Center', 'Quincy Adams',
            'Braintree']

        self.assertListEqual(stp_names, master_names)

class RouteTester(unittest.TestCase):
    def test_basic_functionality(self):
        rt = Stop.filter(id='1')[0]
        self.assertEqual('Washington St opp Ruggles St', rt.name)
        self.assertEqual('1', rt.id)

    def test_get_list(self):
        rts = Route.filter(type='0')
        rt_ids = [rt.id for rt in rts]
        master_ids = [
            'Mattapan', 'Green-B', 'Green-C', 'Green-D',
            'Green-E']
        self.assertListEqual(rt_ids, master_ids)

    def test_filter_route_types_all(self):
        rts = Route.filter_route_types()
        rt_types = list(np.unique([rt.rtype for rt in rts]))
        self.assertListEqual(rt_types, [0, 1, 2, 3, 4])

    def test_filter_route_types_single(self):
        rts = Route.filter_route_types(route_types='LightRail')
        rt_types = list(np.unique([rt.rtype for rt in rts]))
        self.assertListEqual(rt_types, [0])

    def test_filter_route_types_double(self):
        rts = Route.filter_route_types(
            route_types=['LightRail', 'HeavyRail'])
        rt_types = list(np.unique([rt.rtype for rt in rts]))
        self.assertListEqual(rt_types, [0, 1])

    def test_filter_route_types_bad_input(self):
        self.assertRaises(
            ValueError, Route.filter_route_types, 1)

    def test_filter_route_types_empty(self):
        self.assertRaises(
            KeyError, Route.filter_route_types, 'x')

class PredictionTester(unittest.TestCase):
    def test_basic_functionality(self):
        pred = Prediction.filter_next_prediction(stop='place-harsq', direction_id='West')
        self.assertEqual(0, pred.direction_id)
    def test_basic_filter_functionality(self):
        preds = Prediction.filter(stop='place-harsq', direction_id='West')
        self.assertTrue(isinstance(preds, list))
    def test_filter_error(self):
        self.assertRaises(ApiClientError, Prediction.filter)

class CommonTests(unittest.TestCase):
    def test_json_filter_params_func(self):
        params = MbtaBase.json_filter_params(test1='1', test2='2')
        params_master = {'filter[test1]': '1', 'filter[test2]': '2'}
        self.assertDictEqual(params, params_master)

    def test_json_filter_params_list(self):
        params = MbtaBase.json_filter_params(test1=['1', '2'])
        params_master = {'filter[test1]': '1,2'}
        self.assertDictEqual(params, params_master)

    def test_json_filter_params_list_error(self):
        params = MbtaBase.json_filter_params(test1=['1', '2'])
        params_master = {'filter[test1]': '1,2'}
        self.assertDictEqual(params, params_master)

class UserInputTests(unittest.TestCase):

    @patch('builtins.input', return_value='Alewife')
    def test_user_stop_input_function(self, mock_input):
        with suppress_stdout():
            stop = user_input_function(Stop.filter, 'stop', route='Red')
            self.assertEqual(stop.name, 'Alewife')

    @patch('builtins.input', return_value='x')
    def test_user_bad_user_input_function(self, mock_input):
        with suppress_stdout():
            self.assertRaises(
                ValueError, user_input_function, Stop.filter, 'stop', route='Red')

    @patch('builtins.input', return_value='Red Line')
    def test_user_route_input_function(self, mock_input):
        with suppress_stdout():
            route = user_input_function(Route.filter_route_types, 'route',
                                        route_types=['LightRail', 'HeavyRail'])
            self.assertEqual(route.id, 'Red')

class PredictionRunTests(unittest.TestCase):

    @patch('builtins.input', return_value=Mock())
    def test_predict_departure_function(self, mock_input):
        filename = 'test_predict_departure_function_answer.txt'
        self.base_predict_function(mock_input, filename, ['Red Line', 'Harvard', 'Alewife'])

    @patch('builtins.input', return_value=Mock())
    def test_predict_departure_function_end(self, mock_input):
        filename = 'test_predict_departure_function_end_answer.txt'
        self.base_predict_function(mock_input, filename, ['Red Line', 'Alewife'])

    def base_predict_function(self, mock_input, filename, user_inputs):
        # filename = 'test_predict_departure_function_answer.txt'
        if os.path.exists(filename):
            os.remove(filename)

        # mock_input.side_effect = ['Red Line', 'Harvard', 'Alewife']
        mock_input.side_effect = user_inputs
        with suppress_stdout(filename=filename):
            predict_departure()

        f = open(filename, 'r')
        answer_lines = f.readlines()
        f.close()

        keyfile = filename.replace('answer', 'key')
        f = open(keyfile, 'r')
        key_lines = f.readlines()
        f.close()

        self.assertEqual(key_lines[:-1], answer_lines[:-1])
        final_answer = ''.join([c for c in answer_lines[-1] if not c.isdigit() and c != ':'])
        final_key = ''.join([c for c in key_lines[-1] if not c.isdigit() and c != ':'])
        self.assertEqual(final_key.replace(' ', ''), final_answer.replace(' ', ''))

        # remove it again
        os.remove(filename)

if __name__ == '__main__':
    unittest.main()
