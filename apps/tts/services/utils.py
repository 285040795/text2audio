import os

from django.conf import settings


def save_to_media(content, filename):
    """Save content to a file under MEDIA_ROOT and return the file path."""
    os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
    filepath = os.path.join(settings.MEDIA_ROOT, filename)
    mode = 'wb' if isinstance(content, bytes) else 'w'
    encoding = None if isinstance(content, bytes) else 'utf-8'
    with open(filepath, mode, encoding=encoding) as f:
        f.write(content)
    return filepath
