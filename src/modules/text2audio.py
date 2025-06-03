from gtts import gTTS
from pydub import AudioSegment
import os

# 示例文本
text = "Hello, this is a text to speech conversion example."
text = "Hello, you is a good man, you know"

# 选择语言
language = 'en'

# 创建 gTTS 对象
tts = gTTS(text=text, lang=language, slow=False)

mp3_file_path = "data/output.mp3"
# 保存为音频文件
tts.save(mp3_file_path)

# 使用 pydub 将 MP3 文件转换为 WAV 格式
audio = AudioSegment.from_mp3(mp3_file_path)
output_wav_path = "data/output.wav"
audio.export(output_wav_path, format="wav", codec="pcm_s16le")  # 保存为 PCM 编码的 WAV 文件

# 播放音频（在支持的系统上）
# os.system("start output.mp3")  # Windows
os.system("afplay data/output.wav")  # macOS
# os.system("mpg321 output.mp3")  # Linux



# import pyttsx3

# # 初始化 TTS 引擎
# engine = pyttsx3.init()

# # 获取可用的声音列表
# voices = engine.getProperty('voices')

# # 列出可用的声音
# for index, voice in enumerate(voices):
#     print(f"Voice {index}: {voice.name} - {voice.languages}")

# # 选择一个声音（例如选择第一个声音）
# engine.setProperty('voice', voices[135].id)  # 你可以根据需要更改索引

# # 设置语速（可选）
# engine.setProperty('rate', 200)

# # 设置音量（可选）
# engine.setProperty('volume', 1.0)  # 范围是 0.0 到 1.0

# # 示例文本
# text = "Hello, this is a text to speech example with a custom voice."

# # 转换文本为语音
# engine.say(text)

# # 等待语音播放完毕
# engine.runAndWait()
