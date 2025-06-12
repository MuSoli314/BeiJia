#!/usr/bin/env python3
"""
Base64音频数据转换器 - 将base64编码的音频数据转换为WAV或MP3文件
"""

import base64
import os
import tempfile
import subprocess
from pathlib import Path
import wave

def base64_to_wav(base64_data, output_wav_path, sample_rate):
    """
    将base64编码的音频文件转换为WAV格式
    
    Args:
        base64_file_path (str): base64文件路径
        output_wav_path (str): 输出WAV文件路径
        sample_rate (int): 采样率
        channels (int): 声道数
        bit_depth (int): 位深度
    Returns:
        bool: 转换是否成功
    """
    try:
        audio_data = base64.b64decode(base64_data)
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as temp_file:
            temp_file.write(audio_data)
            temp_path = temp_file.name
        
        # 使用ffmpeg转换为WAV
        cmd = ['ffmpeg', '-i', temp_path, '-y', '-ar', str(sample_rate), '-f', 'wav', output_wav_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # 清理临时文件
        os.unlink(temp_path)
        
        return result.returncode == 0
    except Exception:
        return False
