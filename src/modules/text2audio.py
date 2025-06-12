import base64
import os

# coding=utf-8
import sys
from dashscope.audio.tts import SpeechSynthesizer

import wave
import sys

# https://help.aliyun.com/zh/model-studio/sambert-python-api?spm=a2c4g.11186623.help-menu-2400256.d_2_5_1_1.37b94b04100tG4#8d44ae4006hrb
def text2audio4aly(text, model="sambert-donne-v1", file_path=None):
    # 调用语音合成服务
    result = SpeechSynthesizer.call(
        model='sambert-zhigui-v1',
        text=text,
        sample_rate=48000,
        format='wav'
    )
    audio_data = result.get_audio_data()

    if audio_data is not None:
        if file_path is not None:
            with open(file_path, 'wb') as f:
                f.write(audio_data)
                
        audio = base64.b64encode(audio_data).decode('utf-8')
        return audio
    else:
        print('ERROR: response is %s' % (result.get_response()))
        return None

if __name__=="__main__":
    # 同步调用
    # audio_path = 'data/text2audio.wav'
    text = "You are so cool, you know. You are so cool, you know."
    file_path = "data/test.wav"
    text2audio4aly(text, None, file_path)
    # os.system("afplay data/text2audio.wav")  # macOS