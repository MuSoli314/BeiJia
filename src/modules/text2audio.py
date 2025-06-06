# from gtts import gTTS
# from pydub import AudioSegment
import os

# # 示例文本
# text = "Hello, this is a text to speech conversion example."
# text = "Hello, you is a good man, you know"

# # 选择语言
# language = 'en'

# # 创建 gTTS 对象
# tts = gTTS(text=text, lang=language, slow=False)

# mp3_file_path = "data/output.mp3"
# # 保存为音频文件
# tts.save(mp3_file_path)

# # 使用 pydub 将 MP3 文件转换为 WAV 格式
# audio = AudioSegment.from_mp3(mp3_file_path)
# output_wav_path = "data/output.wav"
# audio.export(output_wav_path, format="wav", codec="pcm_s16le")  # 保存为 PCM 编码的 WAV 文件

# # 播放音频（在支持的系统上）
# # os.system("start output.mp3")  # Windows
# os.system("afplay data/output.wav")  # macOS
# # os.system("mpg321 output.mp3")  # Linux

# coding=utf-8
import sys
from dashscope.audio.tts import SpeechSynthesizer
# 若没有将API Key配置到环境变量中，需将apiKey替换为自己的API Key
# import dashscope
# dashscope.api_key = "apiKey"
# 音色列表连接如下
# https://help.aliyun.com/zh/model-studio/sambert-python-api?spm=a2c4g.11186623.help-menu-2400256.d_2_5_1_1.37b94b04100tG4#8d44ae4006hrb
def text2audio4aly(audio_path):
    result = SpeechSynthesizer.call(
        model='sambert-zhichu-v1', # /sambert-zhinan-v1/sambert-zhiqi-v1/
        text='You are so cool.',
        sample_rate=48000,
        format='wav')
    
    if result.get_audio_data() is not None:
        with open(audio_path, 'wb') as f:
            f.write(result.get_audio_data())
        print('SUCCESS: get audio data: %dbytes in output.wav' %
            (sys.getsizeof(result.get_audio_data())))
    else:
        print('ERROR: response is %s' % (result.get_response()))
    

if __name__=="__main__":
    audio_path = 'data/text2audio.wav'
    text2audio4aly(audio_path)
    os.system("afplay data/text2audio.wav")  # macOS