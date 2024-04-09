from __future__ import annotations

from dataclasses import dataclass, field

@dataclass
class PollingConfig:
    enabled: bool = True
    interval: int = 300
    start_immediately: bool = True

    @classmethod
    def default(cls) -> PollingConfig:
        return PollingConfig()

    @classmethod
    def delayed(cls) -> PollingConfig:
        return PollingConfig(start_immediately=False)

    @classmethod
    def disabled(cls) -> PollingConfig:
        return PollingConfig(enabled=False)


@dataclass
class NumeratorConfig:
    apiKey: str
    baseUrl: str = "https://service-platform.dev.numerator.io"
    polling: PollingConfig = field(default_factory=lambda: PollingConfig.default())