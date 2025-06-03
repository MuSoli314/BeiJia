import base64
from flask import Flask, request, jsonify
import wave

from utils.add_logs import setup_logger

app = Flask(__name__)

setup_logger()

# WAV 文件参数
sample_rate = 16000  # 采样率
num_channels = 1     # 单声道
sample_width = 2     # 每个样本的字节数，16 位 PCM 为 2 字节

@app.route('/api/upload-audio', methods=['POST'])
def upload_audio():
    data = request.json
    audio_data = data.get('audio_data')

    # 将 Base64 解码并保存为文件
    audio_bytes = base64.b64decode(audio_data)
    with wave.open("data/uploaded_audio.wav", "wb") as wav_file:
        wav_file.setnchannels(num_channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_bytes)

    return jsonify({"message": "音频文件已接收"})

if __name__ == '__main__':
    app.run(debug=True)
    # app.run(host='0.0.0.0', port=5000, debug=True)
