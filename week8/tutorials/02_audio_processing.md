# 🎤 语音处理与Whisper

> **学习目标**：掌握语音识别与语音合成，构建语音交互应用

---

## 1. 语音AI技术栈

```
┌─────────────────────────────────────────────────────────────────┐
│                    语音AI技术栈                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────┐                   ┌─────────────────┐      │
│  │   语音识别       │                   │   语音合成       │      │
│  │   (ASR/STT)     │                   │   (TTS)         │      │
│  └────────┬────────┘                   └────────┬────────┘      │
│           │                                     │               │
│           ▼                                     ▼               │
│  ┌─────────────────┐         ┌─────────────────────────────┐   │
│  │  OpenAI Whisper │         │  语音合成选项                 │   │
│  │  - whisper-1    │         │  - OpenAI TTS                │   │
│  │  - whisper-v3   │         │  - Edge TTS (免费)           │   │
│  └─────────────────┘         │  - Azure Speech              │   │
│                              └─────────────────────────────┘   │
│                                                                  │
│  应用场景:                                                       │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐           │
│  │ 会议转录 │  │ 语音助手│  │ 有声书  │  │ 客服机器人│          │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Whisper语音识别

### 2.1 使用OpenAI API

```python
from openai import OpenAI
from pathlib import Path

client = OpenAI(
    api_key="your-api-key",
    base_url="https://api.openai.com/v1"  # 或其他兼容API
)

def transcribe_audio(audio_path: str, language: str = "zh") -> dict:
    """
    语音转文字
    
    Args:
        audio_path: 音频文件路径（支持mp3, mp4, wav, m4a等）
        language: 语言代码，zh=中文, en=英文
    
    Returns:
        包含转录文本和元数据的字典
    """
    with open(audio_path, "rb") as audio_file:
        response = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language=language,
            response_format="verbose_json",  # 获取详细信息
            timestamp_granularities=["segment", "word"]  # 获取时间戳
        )
    
    return {
        "text": response.text,
        "language": response.language,
        "duration": response.duration,
        "segments": [
            {
                "start": seg.start,
                "end": seg.end,
                "text": seg.text
            }
            for seg in response.segments
        ]
    }

# 使用
result = transcribe_audio("meeting.mp3", language="zh")
print(f"转录文本: {result['text']}")
print(f"时长: {result['duration']}秒")
```

### 2.2 带时间戳的字幕生成

```python
def generate_srt(audio_path: str, output_path: str):
    """生成SRT字幕文件"""
    result = transcribe_audio(audio_path)
    
    srt_content = []
    for i, segment in enumerate(result["segments"], 1):
        start_time = format_timestamp(segment["start"])
        end_time = format_timestamp(segment["end"])
        text = segment["text"].strip()
        
        srt_content.append(f"{i}")
        srt_content.append(f"{start_time} --> {end_time}")
        srt_content.append(text)
        srt_content.append("")
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(srt_content))

def format_timestamp(seconds: float) -> str:
    """将秒数转换为SRT时间格式"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

# 使用
generate_srt("video.mp4", "subtitles.srt")
```

---

## 3. 本地Whisper模型

### 3.1 安装开源Whisper

```bash
pip install openai-whisper
# 或更快的实现
pip install faster-whisper
```

### 3.2 本地转录

```python
from faster_whisper import WhisperModel

class LocalWhisperService:
    """本地Whisper服务"""
    
    def __init__(self, model_size: str = "medium"):
        """
        初始化模型
        
        Args:
            model_size: tiny, base, small, medium, large-v3
        """
        self.model = WhisperModel(
            model_size,
            device="cuda",  # 或 "cpu"
            compute_type="float16"  # GPU加速
        )
    
    def transcribe(self, audio_path: str, language: str = "zh") -> dict:
        """转录音频"""
        segments, info = self.model.transcribe(
            audio_path,
            language=language,
            beam_size=5,
            word_timestamps=True
        )
        
        result_segments = []
        full_text = []
        
        for segment in segments:
            result_segments.append({
                "start": segment.start,
                "end": segment.end,
                "text": segment.text
            })
            full_text.append(segment.text)
        
        return {
            "text": " ".join(full_text),
            "language": info.language,
            "duration": info.duration,
            "segments": result_segments
        }

# 使用
whisper = LocalWhisperService(model_size="medium")
result = whisper.transcribe("audio.wav")
print(result["text"])
```

---

## 4. 语音合成 (TTS)

### 4.1 OpenAI TTS

```python
def text_to_speech(
    text: str,
    output_path: str,
    voice: str = "alloy",
    speed: float = 1.0
):
    """
    文字转语音
    
    Args:
        text: 要转换的文本
        output_path: 输出音频路径
        voice: 声音选项 (alloy, echo, fable, onyx, nova, shimmer)
        speed: 语速 (0.25 - 4.0)
    """
    response = client.audio.speech.create(
        model="tts-1",  # 或 tts-1-hd 高清版
        voice=voice,
        input=text,
        speed=speed
    )
    
    response.stream_to_file(output_path)
    print(f"音频已保存到: {output_path}")

# 使用
text_to_speech(
    "欢迎学习AI工程师训练营！今天我们来学习语音处理技术。",
    "welcome.mp3",
    voice="nova"
)
```

### 4.2 Edge TTS（免费方案）

```bash
pip install edge-tts
```

```python
import edge_tts
import asyncio

async def edge_text_to_speech(
    text: str,
    output_path: str,
    voice: str = "zh-CN-XiaoxiaoNeural"
):
    """
    使用Edge TTS（免费）
    
    常用中文声音:
    - zh-CN-XiaoxiaoNeural (女声)
    - zh-CN-YunxiNeural (男声)
    - zh-CN-XiaoyiNeural (女声)
    """
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)

# 使用
asyncio.run(edge_text_to_speech(
    "这是一个免费的语音合成方案，效果也很不错！",
    "edge_tts_output.mp3"
))

# 获取所有可用声音
async def list_voices():
    voices = await edge_tts.list_voices()
    zh_voices = [v for v in voices if v["Locale"].startswith("zh")]
    for v in zh_voices:
        print(f"{v['ShortName']}: {v['Gender']}")

asyncio.run(list_voices())
```

---

## 5. 实战：语音对话助手

```python
from openai import OpenAI
import tempfile
import os

class VoiceAssistant:
    """语音对话助手"""
    
    def __init__(self):
        self.client = OpenAI()
        self.conversation_history = []
    
    async def process_voice(self, audio_path: str) -> str:
        """处理语音输入，返回语音回复路径"""
        # 1. 语音转文字
        user_text = self.transcribe(audio_path)
        print(f"用户说: {user_text}")
        
        # 2. AI对话
        ai_response = self.chat(user_text)
        print(f"AI回复: {ai_response}")
        
        # 3. 文字转语音
        output_path = tempfile.mktemp(suffix=".mp3")
        self.text_to_speech(ai_response, output_path)
        
        return output_path
    
    def transcribe(self, audio_path: str) -> str:
        """语音转文字"""
        with open(audio_path, "rb") as f:
            response = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                language="zh"
            )
        return response.text
    
    def chat(self, user_message: str) -> str:
        """AI对话"""
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "你是一个友好的语音助手，回答要简洁。"},
                *self.conversation_history
            ]
        )
        
        ai_message = response.choices[0].message.content
        self.conversation_history.append({
            "role": "assistant",
            "content": ai_message
        })
        
        return ai_message
    
    def text_to_speech(self, text: str, output_path: str):
        """文字转语音"""
        response = self.client.audio.speech.create(
            model="tts-1",
            voice="nova",
            input=text
        )
        response.stream_to_file(output_path)

# 使用
assistant = VoiceAssistant()
reply_audio = await assistant.process_voice("user_input.mp3")
print(f"回复音频: {reply_audio}")
```

---

## 6. FastAPI语音接口

```python
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import tempfile
import os

app = FastAPI()
assistant = VoiceAssistant()

@app.post("/api/voice/chat")
async def voice_chat(audio: UploadFile = File(...)):
    """语音对话接口"""
    # 保存上传的音频
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
        content = await audio.read()
        tmp.write(content)
        input_path = tmp.name
    
    try:
        # 处理语音
        output_path = await assistant.process_voice(input_path)
        
        # 返回语音回复
        return FileResponse(
            output_path,
            media_type="audio/mpeg",
            filename="response.mp3"
        )
    finally:
        os.unlink(input_path)

@app.post("/api/voice/transcribe")
async def transcribe(audio: UploadFile = File(...)):
    """仅语音转文字"""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
        content = await audio.read()
        tmp.write(content)
        input_path = tmp.name
    
    try:
        text = assistant.transcribe(input_path)
        return {"text": text}
    finally:
        os.unlink(input_path)
```

---

## 7. 学习检查清单

- [ ] 能够使用Whisper API进行语音转文字
- [ ] 能够生成带时间戳的字幕文件
- [ ] 会使用OpenAI TTS或Edge TTS进行语音合成
- [ ] 能够构建语音对话接口

---

## 继续学习

📌 **Week 8 学习顺序**：
1. ✅ Vision模型使用
2. ✅ 语音处理与Whisper（本教程）
3. ➡️ 多模态RAG系统
