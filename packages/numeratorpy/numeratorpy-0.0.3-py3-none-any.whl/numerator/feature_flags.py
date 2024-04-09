from __future__ import annotations

from typing import TypeVar, Generic

from .cache import PollingFeatureFlagCache
from .client import NumeratorClient
from .config import NumeratorConfig
from .context import ContextProvider, SimpleContextProvider
from .types import NumeratorException


T = TypeVar('T')


class NumeratorFeatureFlagProvider:

    def __init__(
            self,
            config: NumeratorConfig,
            context_provider: ContextProvider | None = None,
    ):
        self.config = config
        self.context_provider = context_provider or SimpleContextProvider()

        self.client = NumeratorClient(self.config, self.context_provider)
        self.cache = PollingFeatureFlagCache(self.client, self.context_provider, self.config.polling)

        self._known_feature_flags: dict[str, NumeratorFeatureFlag[T]] = {}

    def init_feature_flag(self, key: str, default: T) -> NumeratorFeatureFlag[T]:
        feature_flag = NumeratorFeatureFlag(key, default, self.client, self.cache)

        self._known_feature_flags[key] = feature_flag

        return feature_flag

    def get_feature_flag(self, key: str) -> NumeratorFeatureFlag[T] | None:
        return self._known_feature_flags.get(key)


class NumeratorFeatureFlag(Generic[T]):

    def __init__(self, key: str, default: T, client: NumeratorClient, cache: PollingFeatureFlagCache):
        self.key = key
        self.default = default
        self.client = client
        self.cache = cache

    def value(self, context: dict | None = None, use_default_context: bool = True) -> bool | str | int | float:
        if isinstance(self.default, bool):
            cached = self.cache.get(self.key, context)
            if cached:
                return cached.value.booleanValue or self.default

            return self.client.boolean_flag_variation_detail(self.key, self.default, context, use_default_context).value
        elif isinstance(self.default, str):
            cached = self.cache.get(self.key, context)
            if cached:
                return cached.value.stringValue or self.default

            return self.client.string_flag_variation_detail(self.key, self.default, context, use_default_context).value
        elif isinstance(self.default, int):
            cached = self.cache.get(self.key, context)
            if cached:
                return cached.value.longValue or self.default

            return self.client.long_flag_variation_detail(self.key, self.default, context, use_default_context).value
        elif isinstance(self.default, float):
            cached = self.cache.get(self.key, context)
            if cached:
                return cached.value.doubleValue or self.default

            return self.client.double_flag_variation_detail(self.key, self.default, context, use_default_context).value
        else:
            raise NumeratorException('Unsupported flag type {}'.format(type(self.default)))
