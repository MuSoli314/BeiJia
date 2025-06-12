import base64
import numpy as np
from pydub import AudioSegment
from io import BytesIO

def webm_to_pcm(
    webm_data: bytes,          # 输入WebM二进制数据（或Base64字符串）
    return_numpy: bool = False, # 是否返回numpy数组（默认返回bytes）
    sample_rate: int = 16000   # 目标采样率
) -> tuple:
    """
    将WebM音频转换为16kHz单声道PCM数据
    
    参数:
        webm_data: WebM二进制数据，或Base64编码字符串
        return_numpy: 是否返回numpy数组（否则返回bytes）
        sample_rate: 目标采样率（默认16000Hz）
    
    返回:
        (pcm_data, sample_rate)
        pcm_data可能是bytes或numpy数组
    """
    try:
        # 如果是Base64字符串，先解码
        if isinstance(webm_data, str) and webm_data.startswith(('GkXfo', 'UklGR')):
            webm_data = base64.b64decode(webm_data)
        
        # 使用pydub加载WebM音频
        audio = AudioSegment.from_file(
            BytesIO(webm_data), 
            format="webm"
        )
        
        # 统一转换为16kHz单声道、16-bit PCM
        audio = audio.set_frame_rate(sample_rate)\
                    .set_channels(1)\
                    .set_sample_width(2)  # 16-bit = 2字节
        
        # 获取PCM数据
        pcm_bytes = audio.raw_data
        
        # 按需返回numpy数组或bytes
        if return_numpy:
            pcm_data = np.frombuffer(pcm_bytes, dtype=np.int16)
        else:
            pcm_data = pcm_bytes
        
        return pcm_data, sample_rate
        
    except Exception as e:
        raise ValueError(f"WebM转换失败: {str(e)}")


# 使用示例
if __name__ == "__main__":
    # 示例1：直接处理WebM二进制数据
    # with open("audio.webm", "rb") as f:
    #     webm_binary = f.read()
    
    # pcm_bytes, sr = webm_to_pcm(webm_binary)
    # print(f"PCM bytes长度: {len(pcm_bytes)}, 采样率: {sr}Hz")
    
    # 示例2：处理Base64编码的WebM
    # 从文件读取Base64编码的WebM数据
    with open("data/webm.txt", "r") as f:
        webm_base64 = f.read().strip()
    pcm_array, sr = webm_to_pcm(webm_base64, return_numpy=True)
    # print(f"PCM数组形状: {pcm_array.shape}, 采样率: {sr}Hz")
    # print(f"前10个样本值: {pcm_array[:10]}")

    # 将PCM二进制数据保存为WAV文件
    # 创建WAV文件头
    # import struct
    
    # # WAV文件参数
    # channels = 1
    # sample_width = 2  # 16-bit = 2 bytes
    # frame_rate = sr
    
    # # 计算数据长度
    # data_length = len(pcm_array)
    # file_length = data_length + 36
    
    # # 构建WAV文件头
    # wav_header = struct.pack('<4sI4s4sIHHIIHH4sI',
    #     b'RIFF',           # ChunkID
    #     file_length,       # ChunkSize
    #     b'WAVE',           # Format
    #     b'fmt ',           # Subchunk1ID
    #     16,                # Subchunk1Size (PCM)
    #     1,                 # AudioFormat (PCM)
    #     channels,          # NumChannels
    #     frame_rate,        # SampleRate
    #     frame_rate * channels * sample_width,  # ByteRate
    #     channels * sample_width,               # BlockAlign
    #     sample_width * 8,  # BitsPerSample
    #     b'data',           # Subchunk2ID
    #     data_length        # Subchunk2Size
    # )
    
    # # 合并WAV头和PCM数据
    # wav_data = wav_header + pcm_array

    wav_path = "data/pcm2wav.wav"
    with open(wav_path, "wb") as f:
        f.write(pcm_array.tobytes())
    print(f"PCM数据已保存为WAV文件: {wav_path}")