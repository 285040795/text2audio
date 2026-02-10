import logging
import uuid

import requests
from django.conf import settings

from .tts_service import _save_to_media

logger = logging.getLogger(__name__)


def ai_rewrite(text, prompt=''):
    """Call third-party AI rewrite API and return modified text."""
    api_url = settings.AI_REWRITE_API_URL
    api_key = settings.AI_REWRITE_API_KEY

    if not api_url:
        raise ValueError("AI_REWRITE_API_URL is not configured")

    response = requests.post(
        api_url,
        json={'text': text, 'prompt': prompt},
        headers={'Authorization': f'Bearer {api_key}'},
        timeout=120,
    )
    response.raise_for_status()

    data = response.json()
    rewritten = data.get('text', text)

    # Save rewritten text locally
    filename = f"rewritten_{uuid.uuid4().hex}.txt"
    _save_to_media(rewritten, filename)

    return rewritten
