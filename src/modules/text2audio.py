import base64
import os

# coding=utf-8
import sys
from dashscope.audio.tts import SpeechSynthesizer

import wave
import sys

# https://help.aliyun.com/zh/model-studio/sambert-python-api?spm=a2c4g.11186623.help-menu-2400256.d_2_5_1_1.37b94b04100tG4#8d44ae4006hrb
def text2audio4aly(text, file_path):
    # 调用语音合成服务
    result = SpeechSynthesizer.call(
        model='sambert-zhigui-v1',
        text=text,
        sample_rate=48000,
        format='wav'
    )
    audio_data = result.get_audio_data()

    if audio_data is not None:
        with open(file_path, 'wb') as f:
            f.write(audio_data)
        return audio_data
    else:
        print('ERROR: response is %s' % (result.get_response()))

if __name__=="__main__":
    # 同步调用
    # audio_path = 'data/text2audio.wav'
    text = "You are so cool, you know. You are so cool, you know."
    text = "hello world, 这里是阿里巴巴语音实验室。"
    file_path = "data/test.wav"
    text2audio4aly(text, file_path)
    # os.system("afplay data/text2audio.wav")  # macOS