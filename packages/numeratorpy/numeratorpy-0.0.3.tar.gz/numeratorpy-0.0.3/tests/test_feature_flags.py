import time
import unittest
import requests
import requests_mock
import json

from requests import Session
from unittest.mock import patch
from numerator.client import NumeratorClient
from numerator.config import NumeratorConfig
from numerator.context import SimpleContextProvider
from numerator.feature_flags import NumeratorFeatureFlagProvider

class ExampleFeatureFlagProvider(NumeratorFeatureFlagProvider):

    def __init__(self, config: NumeratorConfig):
        self.config = config
        self.context_provider = SimpleContextProvider()

        super().__init__(self.config, self.context_provider)

        self.init_feature_flag('feature_a', False)
        self.init_feature_flag('feature_b_text', 'Hello World')
        self.init_feature_flag('test_string', 'yyy')

    def is_feature_a_enabled(self) -> bool:
        return self.get_feature_flag('feature_a').value()

    def feature_b_display_text(self) -> str:
        return self.get_feature_flag('feature_b_text').value()

    def test_string_text(self) -> str:
        return self.get_feature_flag('test_string').value()
    
    def test_get_mock(self):
        return self.test_ff_mock()

class TestNumeratorFeatureFlags(unittest.TestCase):
    RESPONSE_FOLDER = 'tests/response/feature_flags'

    def mock_session(self) -> Session:
        session = requests.session()
        adapter = requests_mock.Adapter()
        session.mount('http://', adapter)

        with open('tests/response/feature_flags/polling_flag.json') as file:
            content = json.load(file)
            adapter.register_uri('POST', 'http://localhost:8080/api/sdk/feature-flag/polling', json=content, status_code=200)

        return session

    @patch.object(NumeratorClient, '_build_session', mock_session)
    def setUp(self):
        self.config = NumeratorConfig(
            apiKey='test-api-key',
            baseUrl='http://localhost:8080'
        )

        self.flag_provider = ExampleFeatureFlagProvider(self.config)

    def test_feature_a(self):
        result = self.flag_provider.is_feature_a_enabled()

        self.assertFalse(result)

    def test_feature_b_text(self):
        result = self.flag_provider.feature_b_display_text()

        self.assertEqual(result, 'Hello World')

    def test_string_from_cache(self):
        time.sleep(2)

        result = self.flag_provider.test_string_text()

        print(result)
