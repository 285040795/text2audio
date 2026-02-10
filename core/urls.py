from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

urlpatterns = [
    # Auth endpoints
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Text-to-speech endpoints
    path('tts/text/', views.TextToSpeechView.as_view(), name='tts_text'),
    path('tts/article/', views.ArticleToSpeechView.as_view(), name='tts_article'),
    path('tts/video/', views.VideoToSpeechView.as_view(), name='tts_video'),
    path('tts/upload/', views.UploadToSpeechView.as_view(), name='tts_upload'),
]
