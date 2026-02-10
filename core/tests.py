import io
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient


@override_settings(
    TTS_API_URL='http://mock-tts.example.com/api/tts',
    TTS_API_KEY='test-key',
    ARTICLE_EXTRACT_API_URL='http://mock-article.example.com/api/extract',
    ARTICLE_EXTRACT_API_KEY='test-key',
    VIDEO_EXTRACT_API_URL='http://mock-video.example.com/api/extract',
    VIDEO_EXTRACT_API_KEY='test-key',
    AUDIO_TO_TEXT_API_URL='http://mock-a2t.example.com/api/transcribe',
    AUDIO_TO_TEXT_API_KEY='test-key',
    AI_REWRITE_API_URL='http://mock-ai.example.com/api/rewrite',
    AI_REWRITE_API_KEY='test-key',
)
class BaseTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123', email='test@example.com'
        )

    def _auth(self):
        response = self.client.post('/api/auth/login/', {
            'username': 'testuser',
            'password': 'testpass123',
        })
        token = response.data['tokens']['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')


class AuthTests(BaseTestCase):
    def test_register(self):
        response = self.client.post('/api/auth/register/', {
            'username': 'newuser',
            'password': 'newpass123',
            'email': 'new@example.com',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        self.assertIn('refresh', response.data['tokens'])

    def test_register_duplicate_username(self):
        response = self.client.post('/api/auth/register/', {
            'username': 'testuser',
            'password': 'anotherpass',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_success(self):
        response = self.client.post('/api/auth/login/', {
            'username': 'testuser',
            'password': 'testpass123',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)

    def test_login_invalid_credentials(self):
        response = self.client.post('/api/auth/login/', {
            'username': 'testuser',
            'password': 'wrongpass',
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_missing_fields(self):
        response = self.client.post('/api/auth/login/', {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_token_refresh(self):
        login_resp = self.client.post('/api/auth/login/', {
            'username': 'testuser',
            'password': 'testpass123',
        })
        refresh_token = login_resp.data['tokens']['refresh']
        response = self.client.post('/api/auth/token/refresh/', {
            'refresh': refresh_token,
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_unauthenticated_access(self):
        response = self.client.post('/api/tts/text/', {'text': 'hello'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TextToSpeechTests(BaseTestCase):
    @patch('core.services.requests.post')
    def test_text_to_speech(self, mock_post):
        mock_response = MagicMock()
        mock_response.content = b'fake audio data'
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        self._auth()
        response = self.client.post('/api/tts/text/', {
            'text': 'Hello world',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('audio_url', response.data)
        self.assertEqual(response.data['text'], 'Hello world')

    @patch('core.services.requests.post')
    def test_text_to_speech_with_ai_rewrite(self, mock_post):
        # First call: AI rewrite, second call: TTS
        ai_response = MagicMock()
        ai_response.json.return_value = {'text': 'Rewritten hello world'}
        ai_response.raise_for_status = MagicMock()

        tts_response = MagicMock()
        tts_response.content = b'fake audio data'
        tts_response.raise_for_status = MagicMock()

        mock_post.side_effect = [ai_response, tts_response]

        self._auth()
        response = self.client.post('/api/tts/text/', {
            'text': 'Hello world',
            'ai_rewrite': True,
            'ai_prompt': 'Make it formal',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['text'], 'Rewritten hello world')

    def test_text_to_speech_empty_text(self):
        self._auth()
        response = self.client.post('/api/tts/text/', {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ArticleToSpeechTests(BaseTestCase):
    @patch('core.services.requests.post')
    def test_article_to_speech(self, mock_post):
        article_response = MagicMock()
        article_response.json.return_value = {'text': 'Article content here'}
        article_response.raise_for_status = MagicMock()

        tts_response = MagicMock()
        tts_response.content = b'fake audio data'
        tts_response.raise_for_status = MagicMock()

        mock_post.side_effect = [article_response, tts_response]

        self._auth()
        response = self.client.post('/api/tts/article/', {
            'url': 'https://example.com/article',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('audio_url', response.data)
        self.assertEqual(response.data['text'], 'Article content here')

    def test_article_invalid_url(self):
        self._auth()
        response = self.client.post('/api/tts/article/', {
            'url': 'not-a-url',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class VideoToSpeechTests(BaseTestCase):
    @patch('core.services.requests.post')
    def test_video_to_speech(self, mock_post):
        video_response = MagicMock()
        video_response.content = b'fake video data'
        video_response.raise_for_status = MagicMock()

        transcribe_response = MagicMock()
        transcribe_response.json.return_value = {'text': 'Transcribed text'}
        transcribe_response.raise_for_status = MagicMock()

        tts_response = MagicMock()
        tts_response.content = b'fake audio data'
        tts_response.raise_for_status = MagicMock()

        mock_post.side_effect = [video_response, transcribe_response, tts_response]

        self._auth()
        response = self.client.post('/api/tts/video/', {
            'url': 'https://example.com/video.mp4',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('audio_url', response.data)
        self.assertEqual(response.data['text'], 'Transcribed text')


class UploadToSpeechTests(BaseTestCase):
    @patch('core.services.requests.post')
    def test_upload_mp3(self, mock_post):
        transcribe_response = MagicMock()
        transcribe_response.json.return_value = {'text': 'Transcribed from upload'}
        transcribe_response.raise_for_status = MagicMock()

        tts_response = MagicMock()
        tts_response.content = b'fake audio data'
        tts_response.raise_for_status = MagicMock()

        mock_post.side_effect = [transcribe_response, tts_response]

        self._auth()
        audio_file = io.BytesIO(b'fake mp3 data')
        audio_file.name = 'test.mp3'
        response = self.client.post('/api/tts/upload/', {
            'file': audio_file,
        }, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('audio_url', response.data)
        self.assertEqual(response.data['text'], 'Transcribed from upload')

    def test_upload_unsupported_format(self):
        self._auth()
        bad_file = io.BytesIO(b'fake data')
        bad_file.name = 'test.txt'
        response = self.client.post('/api/tts/upload/', {
            'file': bad_file,
        }, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_upload_no_file(self):
        self._auth()
        response = self.client.post('/api/tts/upload/', {}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

