from rest_framework import serializers


class TextToSpeechSerializer(serializers.Serializer):
    text = serializers.CharField()
    voice = serializers.CharField(default='default', required=False)
    ai_rewrite = serializers.BooleanField(default=False, required=False)
    ai_prompt = serializers.CharField(default='', required=False, allow_blank=True)


class ArticleToSpeechSerializer(serializers.Serializer):
    url = serializers.URLField()
    voice = serializers.CharField(default='default', required=False)
    ai_rewrite = serializers.BooleanField(default=False, required=False)
    ai_prompt = serializers.CharField(default='', required=False, allow_blank=True)


class VideoToSpeechSerializer(serializers.Serializer):
    url = serializers.URLField()
    voice = serializers.CharField(default='default', required=False)
    ai_rewrite = serializers.BooleanField(default=False, required=False)
    ai_prompt = serializers.CharField(default='', required=False, allow_blank=True)


class UploadToSpeechSerializer(serializers.Serializer):
    file = serializers.FileField()
    voice = serializers.CharField(default='default', required=False)
    ai_rewrite = serializers.BooleanField(default=False, required=False)
    ai_prompt = serializers.CharField(default='', required=False, allow_blank=True)

    def validate_file(self, value):
        allowed_extensions = ('.mp3', '.wav', '.mp4', '.m4a', '.flac', '.ogg')
        ext = value.name.lower().rsplit('.', 1)[-1] if '.' in value.name else ''
        if f'.{ext}' not in allowed_extensions:
            raise serializers.ValidationError(
                f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            )
        return value
