#!/usr/bin/env python3
"""
Base64音频数据转换器 - 将base64编码的音频数据转换为WAV文件
"""

import base64
import os
import tempfile
import subprocess
from pathlib import Path

def base64_to_wav(base64_data, output_wav_path):
    """
    将base64编码的音频文件转换为WAV格式
    
    Args:
        base64_file_path (str): base64文件路径
        output_wav_path (str): 输出WAV文件路径
    
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
        cmd = ['ffmpeg', '-i', temp_path, '-y', output_wav_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # 清理临时文件
        os.unlink(temp_path)
        
        return result.returncode == 0
    except Exception:
        return False

def analyze_audio_file(file_path):
    """
    分析音频文件信息
    """
    try:
        print(f"\n🔍 分析音频文件: {file_path}")
        
        # 使用ffprobe获取音频信息
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            file_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            import json
            info = json.loads(result.stdout)
            
            print("📊 音频信息:")
            if 'format' in info:
                format_info = info['format']
                print(f"  格式: {format_info.get('format_name', 'Unknown')}")
                print(f"  时长: {float(format_info.get('duration', 0)):.2f} 秒")
                print(f"  比特率: {format_info.get('bit_rate', 'Unknown')} bps")
            
            if 'streams' in info:
                for stream in info['streams']:
                    if stream.get('codec_type') == 'audio':
                        print(f"  编解码器: {stream.get('codec_name', 'Unknown')}")
                        print(f"  采样率: {stream.get('sample_rate', 'Unknown')} Hz")
                        print(f"  声道数: {stream.get('channels', 'Unknown')}")
                        break
        else:
            print("⚠️ 无法获取详细音频信息")
            
    except Exception as e:
        print(f"⚠️ 分析音频文件时出错: {e}")

def main():
    """主函数"""
    print("🎵 Base64音频转换器")
    print("=" * 50)
    
    # 输入和输出文件路径
    base64_file = "data/base64.txt"
    output_wav = "data/converted_audio.wav"
    
    # 检查输入文件是否存在
    if not os.path.exists(base64_file):
        print(f"❌ 输入文件不存在: {base64_file}")
        return
    
    # 创建输出目录
    os.makedirs(os.path.dirname(output_wav), exist_ok=True)
    
    # 执行转换
    success = base64_to_wav(base64_file, output_wav)
    
    if success:
        print(f"\n🎉 转换成功!")
        print(f"📁 输出文件: {output_wav}")
        
        # 分析转换后的音频文件
        # analyze_audio_file(output_wav)
        
        # print(f"\n💡 使用建议:")
        # print(f"  - 可以使用音频播放器播放: {output_wav}")
        # print(f"  - 可以在代码中使用librosa加载: librosa.load('{output_wav}')")
        
    else:
        print(f"\n❌ 转换失败")
        print(f"💡 建议:")
        print(f"  - 检查base64数据是否完整")
        print(f"  - 安装ffmpeg: brew install ffmpeg")
        print(f"  - 安装pydub: pip install pydub")

if __name__ == "__main__":
    main() 