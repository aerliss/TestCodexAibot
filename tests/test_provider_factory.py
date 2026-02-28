from worker.app.providers.gemini_media import GeminiProvider
from worker.app.services.processor import build_provider


def test_provider_default_is_gemini():
    provider = build_provider()
    assert isinstance(provider, GeminiProvider)
