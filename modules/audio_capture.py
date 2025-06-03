import pyaudio
import numpy as np
import whisper
import wave
from language_tool_python import LanguageTool
import soundfile as sf

# 配置参数
FORMAT = pyaudio.paInt16  # 音频格式
CHANNELS = 1               # 单声道
RATE = 16000               # 采样率
CHUNK = 160                 # 每个缓冲区的样本数（10ms）
VAD_MODE = 3               # VAD 模式（0-3），3 为最严格
OUTPUT_FILENAME = "data/output1.mp3"  # 输出文件名

# 加载 Whisper 模型
# model = whisper.load_model("large")  # 可以选择其他模型，例如 "small", "medium", "large"

# def recognize_speech_from_frames(frames, language='zh'):
#     """
#     从音频帧数据中识别语音
    
#     Args:
#         frames (list): 音频帧数据列表
#         language (str): 识别语言，默认为中文
        
#     Returns:
#         str: 识别出的文本
#     """
#     try:
#         # 将所有帧合并为一个音频数组
#         audio_data = b''.join(frames)
#         audio_array = np.frombuffer(audio_data, dtype=np.int16)
        
#         # 将 NumPy 数组转换为浮点数并归一化
#         audio_float = audio_array.astype(np.float32) / 32768.0
        
#         # 使用 Whisper 模型进行转录
#         result = model.transcribe(audio_float, language=language, fp16=False)
#         return result['text']
        
#     except Exception as e:
#         print(f"语音识别失败: {e}")
#         return ""

def audio_fn():
    # 初始化 PyAudio
    p = pyaudio.PyAudio()

    # 打开音频流
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("开始捕获音频...")
    frames = []

    try:
        while True:
            # 读取音频数据
            audio_data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(audio_data)
    except KeyboardInterrupt:
        # 捕获 Ctrl+C 中断
        print("录音结束。")

    # 关闭流
    stream.stop_stream()
    stream.close()
    p.terminate()

    # 将音频数据转换为 NumPy 数组
    audio_data = b''.join(frames)
    audio_array = np.frombuffer(audio_data, dtype=np.int16)
    
    # 将 NumPy 数组转换为浮点数并归一化
    audio_float = audio_array.astype(np.float32) / 32768.0
    
    # 使用 librosa 保存为 MP3 格式
    sf.write(OUTPUT_FILENAME, audio_float, RATE, format='mp3')
    print(f"录音已保存为 {OUTPUT_FILENAME}")
    
    return frames

def paduan(text):
    text = "I'm a good boy"
    tool = LanguageTool('en-US')
    matches = tool.check(text)
    return matches

if __name__ == "__main__":
    frames = audio_fn()
    # text = recognize_speech_from_frames(frames)
    # print(text)
