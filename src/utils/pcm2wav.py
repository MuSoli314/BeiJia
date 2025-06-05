import numpy as np
import wave

def pcm_to_wav(pcm_file_path, wav_file_path, num_channels=1, sample_width=2, frame_rate=44100):
    """
    将 PCM 文件转换为 WAV 文件

    :param pcm_file_path: 输入 PCM 文件路径
    :param wav_file_path: 输出 WAV 文件路径
    :param num_channels: 声道数，默认为单声道（1）
    :param sample_width: 采样宽度，默认为 2 字节（16 位）
    :param frame_rate: 采样率，默认为 44100 Hz
    """
    # 读取 PCM 数据
    with open(pcm_file_path, 'rb') as pcm_file:
        pcm_data = pcm_file.read()

    # 将 PCM 数据转换为 numpy 数组
    audio_data = np.frombuffer(pcm_data, dtype=np.int16)

    # 创建 WAV 文件
    with wave.open(wav_file_path, 'wb') as wav_file:
        wav_file.setnchannels(num_channels)  # 设置声道数
        wav_file.setsampwidth(sample_width)   # 设置采样宽度
        wav_file.setframerate(frame_rate)      # 设置采样率
        wav_file.writeframes(audio_data.tobytes())  # 写入数据

# 示例调用
if __name__ == "__main__":
    pcm_file_path = 'data/input.pcm'  # 替换为你的 PCM 文件路径
    wav_file_path = 'data/output_pcm.wav'  # 输出 WAV 文件路径
    pcm_to_wav(pcm_file_path, wav_file_path)
    print("转换完成！")
