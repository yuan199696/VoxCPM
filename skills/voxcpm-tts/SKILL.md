---
name: voxcpm-tts
description: "VoxCPM 语音合成，通过本地 API 生成语音。适用场景：(1) 根据语音描述指令生成语音，(2) 基于参考音频克隆音色，(3) 基于参考音频和文本续写语音。接口地址：http://localhost:8000/api/v1/tts"
---

# VoxCPM 语音合成

## 快速开始

向 `http://localhost:8000/api/v1/tts` 发送 POST 请求，JSON 格式请求体。

### 语音描述生成（无参考音频）

```json
{
  "text": "要合成的文本",
  "control_instruction": "年轻女性,温柔甜美"
}
```

### 语音克隆（提供参考音频）

```json
{
  "text": "要合成的文本",
  "reference_audio": "<base64_wav>",
  "control_instruction": "保持原有音色"
}
```

### 语音续写（参考音频 + 文本）

```json
{
  "text": "续写的内容",
  "reference_audio": "<base64_wav>",
  "reference_text": "参考音频的原文"
}
```

**完整工作流程：**

1. **生成语音时**（非续写/克隆）：
   - 请求 TTS 时使用 `output_format: "base64"` 获取 base64 音频
   - 将 base64 数据保存为 `voice_base64.txt`
   - 同时生成 WAV 文件 `voice_reply.wav`
   - 使用 ffmpeg 转换为 Opus 格式 `voice_reply.opus`
   - 使用 `MEDIA: ./voice_reply.opus` 发送

2. **仅当用户明确提出要续写语音时**，才进行续写操作：
   - 读取已保存的 `voice_base64.txt` 作为 `reference_audio`
   - 进行续写生成
   - 续写生成的音频文件名添加后缀 `_continuation`
   - 保存为 `voice_reply_continuation.wav` 和 `voice_reply_continuation.opus`

3. **仅当用户明确提出要克隆声音时**，才进行克隆操作：
   - 使用用户提供的参考音频作为 `reference_audio`
   - 克隆生成的音频文件名添加后缀 `_clone`
   - 保存为 `voice_reply_clone.wav` 和 `voice_reply_clone.opus`

### 输出格式

添加 `"output_format": "base64"` 可获取 base64 编码的音频，而非二进制 WAV 文件。

**重要：进行语音续写时，建议同时生成 base64 文件用于后续参考。** 可以在请求时同时发送二进制音频输出（用于转 Opus 发送）和 base64 输出（用于保存参考音频）。

## 响应字段

- `success`：布尔值，表示是否成功
- `audio`：base64 编码的音频数据（仅在 output_format=base64 时返回）
- `sample_rate`：采样率，固定为 24000
- `duration_seconds`：音频时长（秒）
- `mode`：模式，"design" | "clone" | "continuation"
- `model_id`：模型 ID，"openbmb/VoxCPM2"

## 完整 API 文档

参见 [references/api.md](references/api.md)

---

## 飞书语音消息发送流程

### 格式转换

飞书语音消息要求 **Opus 格式**（48kHz, 64kbps）。因此，TTS 生成的音频（通常是 MP3）必须使用 ffmpeg 等工具转换为 Opus 格式：

```bash
ffmpeg -i output.mp3 -ac 1 -ar 48000 -b:a 64k -c:a libopus voice_reply.opus
```

关键参数：
- `-ac 1`：单声道
- `-ar 48000`：48kHz 采样率
- `-b:a 64k`：64kbps 码率
- `-c:a libopus`：使用 Opus 编码器

### 发送指令

最后，通过以下指令让机器人发送转换好的音频文件：

```
MEDIA: ./voice_reply.opus
```

注意：opus 文件名必须为 `voice_reply.opus`，且路径为当前工作目录。
