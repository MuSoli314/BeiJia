from logging import info
import speech_recognition as sr
from deep_translator import GoogleTranslator
import whisper

def audio_to_text4sr(wav_file_path):
    """
    模块一：语音识别(转文本)模块
    将语音转换为文本
    """
    if wav_file_path is None:
        return None
    
    # 创建一个语音识别器
    recognizer = sr.Recognizer()
        
    try:
        # 打开 WAV 文件
        with sr.AudioFile(wav_file_path) as source:
            # 记录音频数据
            audio = recognizer.record(source)
        # 使用Google语音识别
        text = recognizer.recognize_google(audio, language='en-US')
        print(f"识别结果: {text}")
        return text
    except sr.UnknownValueError:
        print("无法识别语音，请重试")
        return None
    except Exception as e:
        print(f"语音识别服务错误: {e}")
        # 备用方案：使用离线识别
        try:
            text = recognizer.recognize_sphinx(audio)
            print(f"离线识别结果: {text}")
            return text
        except:
            return None

def audio_to_text4whisper(wav_path):
    # 初始化Whisper模型用于语音识别
    whisper_model = whisper.load_model("base") # 可以选择其他模型，例如 "small", "medium", "large"
    result = whisper_model.transcribe(wav_path)
    text = result["text"].strip()
    return text

if __name__=="__main__":
    print("--1--")
    wav_path = "data/output.wav"
    # text = audio_to_text4sr(wav_path)
    text = audio_to_text4whisper(wav_path)
    print("--2--")
    print(text)