from logging import info
import whisper
from datetime import datetime

from dashscope.audio.asr import *
# 若没有将API Key配置到环境变量中，需将your-api-key替换为自己的API Key
# dashscope.api_key = "your-api-key"

def audio2text4aly(wav_path):
    format = wav_path.rsplit('.', 1)[-1]
    translator = TranslationRecognizerRealtime(
        model="gummy-chat-v1", # gummy-realtime-v1/gummy-chat-v1
        format=format,
        sample_rate=16000,
        translation_target_languages=["en"],
        translation_enabled=False,
        callback=None,
    )

    print(f"==1=={wav_path}--{datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")}")
    result = translator.call(wav_path)
    if not result.error_message:
        for transcription_result in result.transcription_result_list:
            return transcription_result.text
    else:
        print("Error: ", result.error_message)

def audio_to_text4whisper(wav_path):
    # 初始化Whisper模型用于语音识别
    whisper_model = whisper.load_model("base") # 可以选择其他模型，例如 base/small/medium/large
    
    print(f"==1=={datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")}")
    result = whisper_model.transcribe(wav_path)

    print(f"==2=={datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")}")
    text = result["text"].strip()
    
    return text

if __name__=="__main__":
    wav_path = "data/test.wav"
    # wav_path = "data/audio_1749628824.wav"

    # print(f"==1=={datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")}")

    text = audio2text4aly(wav_path)
    # text = audio_to_text4whisper(wav_path)
    
    # print(f"==2=={datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")}")
    print(text)