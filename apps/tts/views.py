import logging
import os
import uuid

from django.conf import settings
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    ArticleToSpeechSerializer,
    TextToSpeechSerializer,
    UploadToSpeechSerializer,
    VideoToSpeechSerializer,
)
from .services import (
    ai_rewrite,
    audio_to_text,
    extract_article,
    extract_video,
    text_to_speech,
)

logger = logging.getLogger(__name__)


def _maybe_ai_rewrite(text, do_rewrite, prompt=''):
    """Optionally rewrite text using AI before TTS."""
    if do_rewrite:
        text = ai_rewrite(text, prompt=prompt)
    return text


class TextToSpeechView(APIView):
    """Endpoint 1: Paste text → TTS (with optional AI rewrite)."""

    def post(self, request):
        serializer = TextToSpeechSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        text = data['text']
        text = _maybe_ai_rewrite(text, data.get('ai_rewrite', False), data.get('ai_prompt', ''))

        try:
            filepath, filename = text_to_speech(text, voice=data.get('voice', 'default'))
        except Exception as e:
            logger.exception("TTS failed")
            return Response({'error': str(e)}, status=status.HTTP_502_BAD_GATEWAY)

        audio_url = request.build_absolute_uri(f'{settings.MEDIA_URL}{filename}')
        return Response({
            'text': text,
            'audio_url': audio_url,
        })


class ArticleToSpeechView(APIView):
    """Endpoint 2: Article URL → extract text → TTS (with optional AI rewrite)."""

    def post(self, request):
        serializer = ArticleToSpeechSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            text = extract_article(data['url'])
        except Exception as e:
            logger.exception("Article extraction failed")
            return Response({'error': str(e)}, status=status.HTTP_502_BAD_GATEWAY)

        text = _maybe_ai_rewrite(text, data.get('ai_rewrite', False), data.get('ai_prompt', ''))

        try:
            filepath, filename = text_to_speech(text, voice=data.get('voice', 'default'))
        except Exception as e:
            logger.exception("TTS failed")
            return Response({'error': str(e)}, status=status.HTTP_502_BAD_GATEWAY)

        audio_url = request.build_absolute_uri(f'{settings.MEDIA_URL}{filename}')
        return Response({
            'text': text,
            'audio_url': audio_url,
        })


class VideoToSpeechView(APIView):
    """Endpoint 3: Video URL → download → transcribe → TTS (with optional AI rewrite)."""

    def post(self, request):
        serializer = VideoToSpeechSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            video_path = extract_video(data['url'])
        except Exception as e:
            logger.exception("Video extraction failed")
            return Response({'error': str(e)}, status=status.HTTP_502_BAD_GATEWAY)

        try:
            text = audio_to_text(video_path)
        except Exception as e:
            logger.exception("Audio-to-text transcription failed")
            return Response({'error': str(e)}, status=status.HTTP_502_BAD_GATEWAY)

        text = _maybe_ai_rewrite(text, data.get('ai_rewrite', False), data.get('ai_prompt', ''))

        try:
            filepath, filename = text_to_speech(text, voice=data.get('voice', 'default'))
        except Exception as e:
            logger.exception("TTS failed")
            return Response({'error': str(e)}, status=status.HTTP_502_BAD_GATEWAY)

        audio_url = request.build_absolute_uri(f'{settings.MEDIA_URL}{filename}')
        return Response({
            'text': text,
            'audio_url': audio_url,
        })


class UploadToSpeechView(APIView):
    """Endpoint 4: Upload audio/video file → transcribe → TTS (with optional AI rewrite)."""
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = UploadToSpeechSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        uploaded_file = data['file']
        ext = uploaded_file.name.rsplit('.', 1)[-1] if '.' in uploaded_file.name else 'bin'
        filename = f"upload_{uuid.uuid4().hex}.{ext}"
        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
        upload_path = os.path.join(settings.MEDIA_ROOT, filename)
        with open(upload_path, 'wb') as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)

        try:
            text = audio_to_text(upload_path)
        except Exception as e:
            logger.exception("Audio-to-text transcription failed")
            return Response({'error': str(e)}, status=status.HTTP_502_BAD_GATEWAY)

        text = _maybe_ai_rewrite(text, data.get('ai_rewrite', False), data.get('ai_prompt', ''))

        try:
            filepath, tts_filename = text_to_speech(text, voice=data.get('voice', 'default'))
        except Exception as e:
            logger.exception("TTS failed")
            return Response({'error': str(e)}, status=status.HTTP_502_BAD_GATEWAY)

        audio_url = request.build_absolute_uri(f'{settings.MEDIA_URL}{tts_filename}')
        return Response({
            'text': text,
            'audio_url': audio_url,
        })
