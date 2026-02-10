import logging
import uuid

import requests
from django.conf import settings

from .tts_service import _save_to_media

logger = logging.getLogger(__name__)


def audio_to_text(filepath):
    """Call third-party audio/video-to-text API and return transcribed text."""
    api_url = settings.AUDIO_TO_TEXT_API_URL
    api_key = settings.AUDIO_TO_TEXT_API_KEY

    if not api_url:
        raise ValueError("AUDIO_TO_TEXT_API_URL is not configured")

    with open(filepath, 'rb') as f:
        response = requests.post(
            api_url,
            files={'file': f},
            headers={'Authorization': f'Bearer {api_key}'},
            timeout=180,
        )
    response.raise_for_status()

    data = response.json()
    text = data.get('text', '')

    # Save transcribed text locally
    filename = f"transcribed_{uuid.uuid4().hex}.txt"
    _save_to_media(text, filename)

    return text
