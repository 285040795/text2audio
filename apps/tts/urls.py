from django.urls import path

from . import views

urlpatterns = [
    path('tts/text/', views.TextToSpeechView.as_view(), name='tts_text'),
    path('tts/article/', views.ArticleToSpeechView.as_view(), name='tts_article'),
    path('tts/video/', views.VideoToSpeechView.as_view(), name='tts_video'),
    path('tts/upload/', views.UploadToSpeechView.as_view(), name='tts_upload'),
]
