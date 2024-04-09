from __future__ import annotations

import pkg_resources
import requests
from requests import Response, PreparedRequest, Session
from urllib.parse import urljoin

from .config import NumeratorConfig
from .context import ContextProvider, SimpleContextProvider
from .types import FlagEvaluationDetail, FeatureFlag, NumeratorException, FlagVariationValue, \
    PollingFeatureFlagResponse


class NumeratorClient:

    def __init__(self, config: NumeratorConfig, context_provider: ContextProvider | None = None):
        self.config = config
        self.defaultContextProvider = context_provider or SimpleContextProvider()

        self.session = self._build_session()
        self.session.headers['X-NUM-API-KEY'] = config.apiKey
        self.session.headers['Content-Type'] = 'application/json'
        self.session.headers['Accept'] = 'application/json'

    def version(self) -> str:
        version = pkg_resources.require("numeratorpy")[0].version

        return version

    def get_context_provider(self) -> ContextProvider | None:
        """
            Get the context provider 
            Context provider is used to provide context conditions for feature flag evaluation
        """
        return self.defaultContextProvider

    def set_context_provider(self, context: ContextProvider):
        """
            Set the context provider 
            Context provider is used to provide context conditions for feature flag evaluation
        """
        self.defaultContextProvider = context

    def feature_flags(self, page: int, size: int) -> list[FeatureFlag]:
        """ Get a list of feature flags in the current project """
        resp = self._request('/api/sdk/feature-flag/listing', {
            'page': page,
            'size': size,
        })

        json = resp.json()

        flags = map(
            FeatureFlag.from_dict,
            json.get('data', [])
        )

        return list(flags)

    def feature_flag_details(self, flag_key: str) -> FeatureFlag:
        """ Get details of a single feature flag """
        resp = self._request('/api/sdk/feature-flag/detail-by-key', {}, {'key': flag_key})

        return FeatureFlag.from_dict(resp.json())

    def boolean_flag_variation_detail(
            self,
            flag_key: str,
            default: bool,
            context: dict | None = None,
            use_default_context: bool = True
    ) -> FlagEvaluationDetail[bool]:
        """ Retrieve the `FlagEvaluationDetail[bool]` object """
        request_context = self.defaultContextProvider.context() if use_default_context else {}
        if context:
            request_context = request_context | context

        try:
            variation = self.flag_value_by_key(flag_key, request_context)

            return FlagEvaluationDetail(
                key=flag_key,
                value=variation.value.booleanValue or default,
                reason=None
            )
        except Exception as e:
            return FlagEvaluationDetail(
                key=flag_key,
                value=default,
                reason=None
            )

    def string_flag_variation_detail(
            self,
            flag_key: str,
            default: str,
            context: dict | None = None,
            use_default_context: bool = True
    ) -> FlagEvaluationDetail[str]:
        """ Retrieve the `FlagEvaluationDetail[str]` object """
        request_context = self.defaultContextProvider.context() if use_default_context else {}
        if context:
            request_context = request_context | context

        try:
            variation = self.flag_value_by_key(flag_key, request_context)

            return FlagEvaluationDetail(
                key=flag_key,
                value=variation.value.stringValue or default,
                reason=None
            )
        except Exception as e:
            return FlagEvaluationDetail(
                key=flag_key,
                value=default,
                reason=None
            )

    def long_flag_variation_detail(
            self,
            flag_key: str,
            default: int,
            context: dict | None = None,
            use_default_context: bool = True
    ) -> FlagEvaluationDetail[int]:
        """ Retrieve the `FlagEvaluationDetail[int]` object """
        request_context = self.defaultContextProvider.context() if use_default_context else {}
        if context:
            request_context = request_context | context

        try:
            variation = self.flag_value_by_key(flag_key, request_context)

            return FlagEvaluationDetail(
                key=flag_key,
                value=variation.value.longValue or default,
                reason=None
            )
        except Exception as e:
            return FlagEvaluationDetail(
                key=flag_key,
                value=default,
                reason=None
            )

    def double_flag_variation_detail(
            self,
            flag_key: str,
            default: float,
            context: dict | None = None,
            use_default_context: bool = True
    ) -> FlagEvaluationDetail[float]:
        """ Retrieve the `FlagEvaluationDetail[float]` object """
        request_context = self.defaultContextProvider.context() if use_default_context else {}
        if context:
            request_context = request_context | context

        try:
            variation = self.flag_value_by_key(flag_key, request_context)

            return FlagEvaluationDetail(
                key=flag_key,
                value=variation.value.doubleValue or default,
                reason=None
            )
        except Exception as e:
            return FlagEvaluationDetail(
                key=flag_key,
                value=default,
                reason=None
            )

    def flag_value_by_key(self, key: str, context: dict | None) -> FlagVariationValue:
        """ Get variation of the feature flag. """
        resp = self._request('/api/sdk/feature-flag/by-key', {
            'key': key,
            'context': context if context else {}
        })

        return FlagVariationValue.from_dict(resp.json())

    def polling(self, context: dict | None = None, etag: str | None = None) -> PollingFeatureFlagResponse | None:
        resp = self._request(
            url='/api/sdk/feature-flag/polling',
            json={
                'context': context or {},
            },
            headers={
                'If-None-Match': etag or '',
            },
        )

        # not modified
        if resp.status_code == 304:
            return None

        return PollingFeatureFlagResponse.from_dict(resp.json(), resp.headers.get('ETag'))

    def _request(self, url: str, json: dict, params: dict | None = None, headers: dict | None = None) -> Response:
        resp = self.session.post(self._build_url(url, params), json=json, headers=headers)

        if not resp.ok:
            raise NumeratorException('Numerator API response {}: {}'.format(resp.status_code, resp.text))

        return resp

    def _build_url(self, endpoint: str, params: dict | None = None):
        url = urljoin(self.config.baseUrl, endpoint)

        if params:
            req = PreparedRequest()
            req.prepare_url(url, params)
            url = req.url

        return url

    def _build_session(self) -> Session:
        return requests.session()
