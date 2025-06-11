from logging import info
from datetime import datetime

from dashscope.audio.asr import *
# import whisper
# 若没有将API Key配置到环境变量中，需将your-api-key替换为自己的API Key
# dashscope.api_key = "your-api-key"

def audio2text4aly(wav_path, sample_rate=48000):
    file_format = wav_path.rsplit('.', 1)[-1]
    translator = TranslationRecognizerRealtime(
        model="gummy-realtime-v1", # gummy-realtime-v1/gummy-chat-v1
        format=file_format,
        sample_rate=sample_rate, # 这个参数要和wva文件一致 ffmpeg -i data/audio_1749618717.wav
        source_language="en",
        transcription_enabled=True,
        callback=None,
    )

    print(f"==1=={wav_path}--{datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")}")
    result = translator.call(wav_path)
    if not result.error_message:
        for transcription_result in result.transcription_result_list:
            return transcription_result.text
        
        for translation_result in result.translation_result_list:
            print(translation_result.get_translation('zh').text)
    else:
        print("Error: ", result.error_message)

# impoet whisper
# def audio_to_text4whisper(wav_path):
#     whisper_model = whisper.load_model("base")
#     # print(f"==1=={datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")}")
#     result = whisper_model.transcribe(wav_path)
#     # print(f"==2=={datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")}")
#     text = result["text"].strip()
#     return text

if __name__=="__main__":
    # wav_path = "data/test.wav"
    # wav_path = "data/asr_example.wav"
    wav_path = "data/audio_1749630457.wav"

    print(f"==1=={datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")}")

    text = audio2text4aly(wav_path)

    # 初始化Whisper模型用于语音识别
    # text = audio_to_text4whisper(wav_path)
    
    print(f"==2=={datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")}")
    print(text)