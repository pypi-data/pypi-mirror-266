from __future__ import annotations

import threading
import time

from .client import NumeratorClient
from .config import PollingConfig
from .context import ContextProvider
from .types import FlagVariationValue


class PollingFeatureFlagCache:

    def __init__(
            self,
            client: NumeratorClient,
            context_provider: ContextProvider,
            config: PollingConfig = PollingConfig.default(),
    ):
        self.client = client
        self.context_provider = context_provider

        self.feature_flags = {}
        self.current_etag = None

        self.config = config
        self._interrupted = False

        if self.config.start_immediately:
            self.start()

    def start(self):
        if self.config.enabled:
            thread = threading.Thread(target=self.run, args=())
            thread.daemon = True
            thread.start()

    def stop(self):
        self._interrupted = True

    def run(self):
        while not self._interrupted:
            feature_flags = self.client.polling(context=self.context_provider.context(), etag=self.current_etag)

            if feature_flags:
                self.current_etag = feature_flags.etag
                self.feature_flags = {flag.key: flag for flag in feature_flags.flags}

            time.sleep(self.config.interval)

    def get(self, key: str, context: dict | None = None) -> FlagVariationValue | None:
        if not self.config.enabled:
            return None

        if context == self.context_provider.context():
            return self.feature_flags.get(key)

        return None
