# VoxCPM TTS API 参考文档

本地接口地址：`http://localhost:8000/api/v1/tts`

## 接口列表

### POST /api/v1/tts

语音合成，支持三种模式：

| 模式 | 必填字段 |
|------|----------|
| 声音设计 | `text`, `control_instruction` |
| 声音克隆 | `text`, `reference_audio`, `control_instruction` |
| 声音续写 | `text`, `reference_audio`, `reference_text` |

#### 请求体

```json
{
  "text": "string - 要合成的文本",
  "control_instruction": "string - 声音描述 (声音设计/克隆模式)",
  "reference_audio": "string - base64编码的wav音频 (克隆/续写模式)",
  "reference_text": "string - 参考音频的原文 (续写模式)",
  "output_format": "string - 设为\"base64\"则返回base64而非文件"
}
```

#### 响应（base64 模式）

```json
{
  "success": true,
  "audio": "UklGRiQAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQAAAAA=",
  "sample_rate": 24000,
  "duration_seconds": 2.5,
  "mode": "design|clone|continuation",
  "model_id": "openbmb/VoxCPM2",
  "content_type": "audio/wav"
}
```

#### 声音描述指令（control_instruction）示例

- "年轻女性,温柔甜美"
- "中年男性,低沉稳重"
- "儿童音色,活泼可爱"
- "保持原有音色"

## 使用示例

### cURL

```bash
# 声音设计
curl -X POST "http://localhost:8000/api/v1/tts" \
  -H "Content-Type: application/json" \
  -d '{"text": "你好，这是语音合成测试", "control_instruction": "年轻女性,温柔甜美"}' -o synthesized.wav

# 声音克隆
curl -X POST "http://localhost:8000/api/v1/tts" \
  -H "Content-Type: application/json" \
  -d '{"text": "这是要克隆的声音说的话", "reference_audio": "<base64_wav_data>", "control_instruction": "保持原有音色"}' -o synthesized.wav

# 声音续写
curl -X POST "http://localhost:8000/api/v1/tts" \
  -H "Content-Type: application/json" \
  -d '{"text": "继续说下去的内容", "reference_audio": "<base64_wav_data>", "reference_text": "这是参考音频的原文内容"}' -o synthesized.wav

# 获取 base64 响应
curl -X POST "http://localhost:8000/api/v1/tts" \
  -H "Content-Type: application/json" \
  -d '{"text": "测试文本", "output_format": "base64"}'
```

### Python

```python
import requests
import base64

url = "http://localhost:8000/api/v1/tts"

# 声音设计
response = requests.post(url, json={
    "text": "你好，这是语音合成测试",
    "control_instruction": "年轻女性,温柔甜美"
})
with open("synthesized.wav", "wb") as f:
    f.write(response.content)

# 获取 base64 输出
response = requests.post(url, json={
    "text": "测试文本",
    "output_format": "base64"
})
data = response.json()
audio_bytes = base64.b64decode(data["audio"])
```
