import logging
import uuid

import requests
from django.conf import settings

from .tts_service import _save_to_media

logger = logging.getLogger(__name__)


def extract_video(url):
    """Call third-party video extraction API, download video, and return file path."""
    api_url = settings.VIDEO_EXTRACT_API_URL
    api_key = settings.VIDEO_EXTRACT_API_KEY

    if not api_url:
        raise ValueError("VIDEO_EXTRACT_API_URL is not configured")

    response = requests.post(
        api_url,
        json={'url': url},
        headers={'Authorization': f'Bearer {api_key}'},
        timeout=120,
    )
    response.raise_for_status()

    filename = f"video_{uuid.uuid4().hex}.mp4"
    filepath = _save_to_media(response.content, filename)
    return filepath
