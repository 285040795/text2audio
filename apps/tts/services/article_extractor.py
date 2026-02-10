import logging
import uuid

import requests
from django.conf import settings

from .tts_service import _save_to_media

logger = logging.getLogger(__name__)


def extract_article(url):
    """Call third-party article extraction API and return the article text."""
    api_url = settings.ARTICLE_EXTRACT_API_URL
    api_key = settings.ARTICLE_EXTRACT_API_KEY

    if not api_url:
        raise ValueError("ARTICLE_EXTRACT_API_URL is not configured")

    response = requests.post(
        api_url,
        json={'url': url},
        headers={'Authorization': f'Bearer {api_key}'},
        timeout=60,
    )
    response.raise_for_status()

    data = response.json()
    text = data.get('text', '')

    # Save article text locally
    filename = f"article_{uuid.uuid4().hex}.txt"
    _save_to_media(text, filename)

    return text
