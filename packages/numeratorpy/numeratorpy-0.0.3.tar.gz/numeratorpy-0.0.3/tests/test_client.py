import unittest
import requests
import requests_mock
import json

from requests import Session
from unittest.mock import patch
from numerator.client import NumeratorClient
from numerator.config import NumeratorConfig
from numerator.feature_flags import NumeratorException

adapter = None

class TestNumeratorClient(unittest.TestCase):
    RESPONSE_FOLDER = 'tests/response'
    BASE_URL = 'http://localhost:8080/api/sdk/feature-flag'

    def mock_session(self) -> Session:
        global adapter

        session = requests.session()
        adapter = requests_mock.Adapter()
        session.mount('http://', adapter)

        return session

    def __prepare_endpoint(self, path: str, response_json_path: str, status_code: int = 200):
        if status_code == 401:
            adapter.register_uri('POST', f'{self.BASE_URL}/{path}', status_code=status_code)
        else:
            with open(f'{self.RESPONSE_FOLDER}/{response_json_path}') as file:
                adapter.register_uri('POST', f'{self.BASE_URL}/{path}', json=json.load(file), status_code=status_code)
            

    @patch.object(NumeratorClient, '_build_session', mock_session)
    def setUp(self):
        self.client = NumeratorClient(NumeratorConfig(
            apiKey='your API Key here',
            baseUrl='http://localhost:8080'
        ))

    def test_all_flags(self):
        self.__prepare_endpoint(path='listing', response_json_path="feature_flags/listing.json")
        result = self.client.feature_flags(0, 10)

        print(result)

    def test_flag_details(self):
        self.__prepare_endpoint(path='detail-by-key?key=test_boolean', response_json_path="feature_flags/boolean_detail.json")
        result = self.client.feature_flag_details('test_boolean')

        print(result)

    def test_boolean_flag_value(self):
        result = self.client.boolean_flag_variation_detail('', True)

        print(result)

    def test_long_variation_by_key(self):
        self.__prepare_endpoint(path='by-key', response_json_path='feature_flags/long_flag_variation.json')
        result = self.client.flag_value_by_key('test_long', context=None).value.longValue

        self.assertEqual(result, 10)

    def test_string_variation_by_key(self):
        self.__prepare_endpoint(path='by-key', response_json_path='feature_flags/string_flag_variation.json')
        result = self.client.flag_value_by_key('test_string', context=None).value.stringValue

        self.assertEqual(result, 'abc')

    def test_double_variation_by_key(self):
        self.__prepare_endpoint(path='by-key', response_json_path='feature_flags/double_flag_variation.json')
        result = self.client.flag_value_by_key('test_double', context=None).value.doubleValue

        self.assertEqual(result, 1.0)

    def test_boolean_variation_by_key(self):
        self.__prepare_endpoint(path='by-key', response_json_path='feature_flags/boolean_flag_variation.json')
        result = self.client.flag_value_by_key('test_boolean', context=None).value.booleanValue

        self.assertEqual(result, True)

    def test_variation_not_found(self):
        self.__prepare_endpoint(path='by-key', response_json_path='feature_flags/flag_not_found.json', status_code=404)
        with self.assertRaises(Exception) as context:
            result = self.client.flag_value_by_key('test_not_found', context=None)
        self.assertTrue(type(context.exception) is NumeratorException)

    def test_use_wrong_sdk_key(self):
        self.__prepare_endpoint(path='by-key', response_json_path='', status_code=401)
        with self.assertRaises(Exception) as context:
            result = self.client.flag_value_by_key('wrong_api_key', context=None)
        self.assertTrue("Numerator API response 401" in context.exception.args[0])

    def test_polling(self):
        self.__prepare_endpoint(path='polling', response_json_path="feature_flags/polling_flag.json")
        result = self.client.polling({})

        self.assertIsNone(result.etag)
        self.assertIsNotNone(result.flags)

    def test_polling_not_modified(self):
        with open(f'{self.RESPONSE_FOLDER}/feature_flags/polling_flag.json') as file:
            content = json.load(file)
            adapter.register_uri('POST', f'{self.BASE_URL}/polling', [{'json': content, 'status_code': 200},
                                                                      {'json': content, 'status_code': 304}])
                                                                                                
            old_result = self.client.polling({})
            new_result = self.client.polling({}, etag=old_result.etag)

        self.assertIsNone(new_result)

    def test_get_version(self):
        version = self.client.version()
        
        self.assertIsNotNone(version)