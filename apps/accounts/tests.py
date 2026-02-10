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
