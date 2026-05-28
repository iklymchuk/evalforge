
import pytest
from evalforge.providers.anthropic import AnthropicProvider
from evalforge.providers.openai import OpenAIProvider
from evalforge.providers.together import TogetherProvider
from evalforge.models import ProviderResponse

@pytest.mark.integration
@pytest.mark.parametrize("provider_cls", [AnthropicProvider, OpenAIProvider, TogetherProvider])
def test_provider_returns_valid_response(provider_cls):
    provider = provider_cls()
    response = provider.complete("Say hello in 5 words.")
    assert isinstance(response, ProviderResponse)
    assert response.text
    assert response.usage.input_tokens > 0
    assert response.usage.output_tokens > 0
    assert response.latency_ms > 0
    assert response.raw is not None
