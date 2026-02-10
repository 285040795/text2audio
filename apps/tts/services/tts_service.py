import logging
import uuid

import requests
from django.conf import settings

from .utils import save_to_media

logger = logging.getLogger(__name__)


def text_to_speech(text, voice='default'):
    """Call third-party TTS API and return the audio file path."""
    api_url = settings.TTS_API_URL
    api_key = settings.TTS_API_KEY

    if not api_url:
        raise ValueError("TTS_API_URL is not configured")

    response = requests.post(
        api_url,
        json={'text': text, 'voice': voice},
        headers={'Authorization': f'Bearer {api_key}'},
        timeout=120,
    )
    response.raise_for_status()

    filename = f"tts_{uuid.uuid4().hex}.mp3"
    filepath = save_to_media(response.content, filename)
    return filepath, filename
