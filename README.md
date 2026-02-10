# text2audio

文字转语音 Django REST API 项目

## 功能

1. **文字转语音** — 粘贴文字后一键转语音
2. **文章链接转语音** — 输入文章 URL，提取正文后转语音
3. **视频链接转语音** — 输入视频 URL，下载视频、转文字后再转语音
4. **上传音视频转语音** — 上传 MP3/WAV/MP4 等文件，转文字后再转语音
5. **AI 改写** — 以上所有流程均支持可选的 AI 文字改写后再配音

所有接口均需 JWT Token 认证。

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 数据库迁移
python manage.py migrate

# 启动开发服务器
python manage.py runserver
```

## 环境变量配置

在 `.env` 文件或环境变量中设置以下第三方 API 配置：

| 变量名 | 说明 |
|---|---|
| `TTS_API_URL` | 文字转语音 API 地址 |
| `TTS_API_KEY` | 文字转语音 API 密钥 |
| `ARTICLE_EXTRACT_API_URL` | 文章提取 API 地址 |
| `ARTICLE_EXTRACT_API_KEY` | 文章提取 API 密钥 |
| `VIDEO_EXTRACT_API_URL` | 视频提取 API 地址 |
| `VIDEO_EXTRACT_API_KEY` | 视频提取 API 密钥 |
| `AUDIO_TO_TEXT_API_URL` | 音频转文字 API 地址 |
| `AUDIO_TO_TEXT_API_KEY` | 音频转文字 API 密钥 |
| `AI_REWRITE_API_URL` | AI 改写 API 地址 |
| `AI_REWRITE_API_KEY` | AI 改写 API 密钥 |
| `DJANGO_SECRET_KEY` | Django 密钥（生产环境必设） |
| `DJANGO_DEBUG` | 是否开启调试模式（默认 True） |
| `DJANGO_ALLOWED_HOSTS` | 允许的主机名，逗号分隔 |

## API 接口

### 认证

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/auth/register/` | 用户注册 |
| POST | `/api/auth/login/` | 用户登录 |
| POST | `/api/auth/token/refresh/` | 刷新 Token |

### 文字转语音

所有以下接口需要在请求头中携带 `Authorization: Bearer <access_token>`。

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/tts/text/` | 文字转语音 |
| POST | `/api/tts/article/` | 文章链接转语音 |
| POST | `/api/tts/video/` | 视频链接转语音 |
| POST | `/api/tts/upload/` | 上传文件转语音 |

#### 请求参数

**文字转语音 `/api/tts/text/`**
```json
{
    "text": "要转换的文字",
    "voice": "default",
    "ai_rewrite": false,
    "ai_prompt": ""
}
```

**文章链接转语音 `/api/tts/article/`**
```json
{
    "url": "https://example.com/article",
    "voice": "default",
    "ai_rewrite": false,
    "ai_prompt": ""
}
```

**视频链接转语音 `/api/tts/video/`**
```json
{
    "url": "https://example.com/video.mp4",
    "voice": "default",
    "ai_rewrite": false,
    "ai_prompt": ""
}
```

**上传文件转语音 `/api/tts/upload/`**（multipart/form-data）
- `file`: 音视频文件（支持 mp3, wav, mp4, m4a, flac, ogg）
- `voice`: 语音类型（可选）
- `ai_rewrite`: 是否 AI 改写（可选）
- `ai_prompt`: AI 改写提示词（可选）

#### 响应示例
```json
{
    "text": "转换后的文字内容",
    "audio_url": "http://localhost:8000/media/tts_xxx.mp3"
}
```

## 测试

```bash
python manage.py test apps
```

