from google import genai
from app.config import settings

_client = None

def get_gemini_client():
    global _client
    if not settings.gemini_api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured. Add it to .env before generating a comic."
        )
    if _client is None:
        _client = genai.Client(api_key=settings.gemini_api_key)
    return _client
