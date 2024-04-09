# Numerator Python SDK

## Quickstart

1. Create a subclass of `NumeratorFeatureFlagProvider` and define feature flags:

```python
from numerator.config import NumeratorConfig
from numerator.context import SimpleContextProvider
from numerator.feature_flags import NumeratorFeatureFlagProvider


class ExampleFeatureFlagProvider(NumeratorFeatureFlagProvider):

    def __init__(self, config: NumeratorConfig):
        self.config = config
        self.context_provider = SimpleContextProvider()

        super().__init__(self.config, self.context_provider)

        self.init_feature_flag('basic_boolean_flag', False)
        self.init_feature_flag('basic_string_flag', 'Hello World')

    def is_basic_feature_enabled(self) -> bool:
        return self.get_feature_flag('basic_boolean_flag').value()

    def get_string_value_for_context(self, context: dict) -> str:
        return self.get_feature_flag('basic_string_flag').value(context)
```

2. Use the above feature flag accessors in code:

```python
feature_flags = ExampleFeatureFlagProvider(config)

if feature_flags.is_basic_feature_enabled():
    # feature enabled logic
    text = feature_flags.get_string_value_for_context({ 'user': '...' })
else:
    # feature disabled logic
```

## Advanced Usage

*TODO*
