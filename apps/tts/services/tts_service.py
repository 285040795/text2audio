import logging
import os
import uuid

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def _save_to_media(content, filename):
    """Save content to a file under MEDIA_ROOT and return the file path."""
    os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
    filepath = os.path.join(settings.MEDIA_ROOT, filename)
    mode = 'wb' if isinstance(content, bytes) else 'w'
    encoding = None if isinstance(content, bytes) else 'utf-8'
    with open(filepath, mode, encoding=encoding) as f:
        f.write(content)
    return filepath


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
    filepath = _save_to_media(response.content, filename)
    return filepath, filename
