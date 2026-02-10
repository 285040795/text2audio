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
