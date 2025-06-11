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

def main():
    """主函数"""
    print("🎵 Base64音频转换器")
    print("=" * 50)
    
    # 输入和输出文件路径
    base64_file = "data/base64.txt"
    output_mp3 = "data/converted_audio.mp3"
    
    # 检查输入文件是否存在
    if not os.path.exists(base64_file):
        print(f"❌ 输入文件不存在: {base64_file}")
        return
    
    # 创建输出目录
    os.makedirs(os.path.dirname(output_mp3), exist_ok=True)
    
    # 读取base64数据
    with open(base64_file, 'r') as f:
        base64_data = f.read().strip()
    
    # 执行转换
    success = base64_to_wav(base64_data, output_mp3)
    
    if success:
        print(f"\n🎉 转换成功!")
        print(f"📁 输出文件: {output_mp3}")
        
        # 分析转换后的音频文件
        # analyze_audio_file(output_mp3)
        
        # print(f"\n💡 使用建议:")
        # print(f"  - 可以使用音频播放器播放: {output_mp3}")
        # print(f"  - 可以在代码中使用librosa加载: librosa.load('{output_mp3}')")
        
    else:
        print(f"\n❌ 转换失败")
        print(f"💡 建议:")
        print(f"  - 检查base64数据是否完整")
        print(f"  - 安装ffmpeg: brew install ffmpeg")
        print(f"  - 安装pydub: pip install pydub")

if __name__ == "__main__":
    main() 