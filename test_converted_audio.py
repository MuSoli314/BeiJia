#!/usr/bin/env python3
"""
测试转换后的音频文件 - 验证WAV文件并展示使用方法
"""

import os
import numpy as np
import librosa
import soundfile as sf
import matplotlib.pyplot as plt

def test_audio_file(wav_path):
    """
    测试音频文件的各种功能
    
    Args:
        wav_path (str): WAV文件路径
    """
    print(f"🎵 测试音频文件: {wav_path}")
    print("=" * 50)
    
    # 检查文件是否存在
    if not os.path.exists(wav_path):
        print(f"❌ 文件不存在: {wav_path}")
        return
    
    try:
        # 1. 使用librosa加载音频
        print("📖 使用librosa加载音频...")
        audio_data, sample_rate = librosa.load(wav_path, sr=None)
        
        print(f"✅ 加载成功!")
        print(f"  📊 采样率: {sample_rate} Hz")
        print(f"  📏 音频长度: {len(audio_data)} 样本")
        print(f"  ⏱️  时长: {len(audio_data) / sample_rate:.2f} 秒")
        print(f"  📈 数据类型: {audio_data.dtype}")
        print(f"  📊 数值范围: [{audio_data.min():.4f}, {audio_data.max():.4f}]")
        
        # 2. 音频特征分析
        print(f"\n🔍 音频特征分析:")
        
        # RMS能量
        rms = librosa.feature.rms(y=audio_data)[0]
        print(f"  🔊 RMS能量: 平均={np.mean(rms):.4f}, 最大={np.max(rms):.4f}")
        
        # 零交叉率
        zcr = librosa.feature.zero_crossing_rate(audio_data)[0]
        print(f"  🌊 零交叉率: 平均={np.mean(zcr):.4f}")
        
        # 频谱质心
        spectral_centroids = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)[0]
        print(f"  🎼 频谱质心: 平均={np.mean(spectral_centroids):.2f} Hz")
        
        # 3. 使用soundfile读取（验证格式）
        print(f"\n📖 使用soundfile验证...")
        sf_data, sf_sr = sf.read(wav_path)
        print(f"✅ SoundFile读取成功!")
        print(f"  📊 采样率: {sf_sr} Hz")
        print(f"  📏 形状: {sf_data.shape}")
        print(f"  📈 数据类型: {sf_data.dtype}")
        
        # 4. 保存音频片段示例
        print(f"\n💾 保存音频片段示例...")
        
        # 保存前1秒的音频
        if len(audio_data) > sample_rate:
            clip_data = audio_data[:sample_rate]  # 前1秒
            clip_path = "data/audio_clip_1sec.wav"
            sf.write(clip_path, clip_data, sample_rate)
            print(f"✅ 已保存1秒片段: {clip_path}")
        
        # 5. 简单的音频可视化
        print(f"\n📊 生成音频可视化...")
        try:
            plt.figure(figsize=(12, 8))
            
            # 时域波形
            plt.subplot(3, 1, 1)
            time_axis = np.linspace(0, len(audio_data) / sample_rate, len(audio_data))
            plt.plot(time_axis, audio_data)
            plt.title('音频波形 (时域)')
            plt.xlabel('时间 (秒)')
            plt.ylabel('振幅')
            plt.grid(True)
            
            # 频谱图
            plt.subplot(3, 1, 2)
            D = librosa.amplitude_to_db(np.abs(librosa.stft(audio_data)), ref=np.max)
            librosa.display.specshow(D, y_axis='hz', x_axis='time', sr=sample_rate)
            plt.title('频谱图')
            plt.colorbar(format='%+2.0f dB')
            
            # RMS能量
            plt.subplot(3, 1, 3)
            times = librosa.frames_to_time(np.arange(len(rms)), sr=sample_rate)
            plt.plot(times, rms)
            plt.title('RMS能量')
            plt.xlabel('时间 (秒)')
            plt.ylabel('RMS')
            plt.grid(True)
            
            plt.tight_layout()
            plot_path = "data/audio_analysis.png"
            plt.savefig(plot_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            print(f"✅ 可视化图表已保存: {plot_path}")
            
        except Exception as e:
            print(f"⚠️ 可视化生成失败: {e}")
        
        # 6. 音频质量检查
        print(f"\n🔍 音频质量检查:")
        
        # 检查是否有静音
        silence_threshold = 0.01
        silent_samples = np.sum(np.abs(audio_data) < silence_threshold)
        silence_ratio = silent_samples / len(audio_data)
        print(f"  🔇 静音比例: {silence_ratio:.2%}")
        
        # 检查是否有削波
        clipping_threshold = 0.95
        clipped_samples = np.sum(np.abs(audio_data) > clipping_threshold)
        clipping_ratio = clipped_samples / len(audio_data)
        print(f"  ✂️  削波比例: {clipping_ratio:.2%}")
        
        # 动态范围
        dynamic_range = 20 * np.log10(np.max(np.abs(audio_data)) / (np.mean(np.abs(audio_data)) + 1e-10))
        print(f"  📏 动态范围: {dynamic_range:.2f} dB")
        
        # 7. 使用建议
        print(f"\n💡 使用建议:")
        print(f"  - 音频质量: {'良好' if clipping_ratio < 0.01 and silence_ratio < 0.5 else '需要检查'}")
        print(f"  - 适合语音识别: {'是' if np.mean(rms) > 0.01 and silence_ratio < 0.7 else '可能需要预处理'}")
        print(f"  - 可以直接用于训练: {'是' if dynamic_range > 10 else '建议进行音频增强'}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试过程出错: {e}")
        return False

def demonstrate_usage():
    """
    演示如何在其他代码中使用转换后的音频
    """
    print(f"\n🚀 代码使用示例:")
    print("=" * 50)
    
    code_examples = [
        ("使用librosa加载", """
import librosa
audio, sr = librosa.load('data/converted_audio.wav')
print(f"音频长度: {len(audio)} 样本, 采样率: {sr} Hz")
"""),
        ("使用soundfile加载", """
import soundfile as sf
audio, sr = sf.read('data/converted_audio.wav')
print(f"音频形状: {audio.shape}, 采样率: {sr} Hz")
"""),
        ("提取MFCC特征", """
import librosa
audio, sr = librosa.load('data/converted_audio.wav')
mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
print(f"MFCC特征形状: {mfccs.shape}")
"""),
        ("语音识别", """
import speech_recognition as sr
r = sr.Recognizer()
with sr.AudioFile('data/converted_audio.wav') as source:
    audio = r.record(source)
    text = r.recognize_google(audio, language='zh-CN')
    print(f"识别结果: {text}")
"""),
        ("音频分段", """
import librosa
audio, sr = librosa.load('data/converted_audio.wav')
# 按1秒分段
segment_length = sr  # 1秒的样本数
segments = [audio[i:i+segment_length] for i in range(0, len(audio), segment_length)]
print(f"分成 {len(segments)} 段")
""")
    ]
    
    for title, code in code_examples:
        print(f"\n📝 {title}:")
        print(code.strip())

def main():
    """主函数"""
    wav_file = "data/converted_audio.wav"
    
    # 测试音频文件
    success = test_audio_file(wav_file)
    
    if success:
        # 演示使用方法
        demonstrate_usage()
        
        print(f"\n🎉 音频文件测试完成!")
        print(f"📁 主要输出文件:")
        print(f"  - 原始音频: {wav_file}")
        print(f"  - 音频片段: data/audio_clip_1sec.wav")
        print(f"  - 分析图表: data/audio_analysis.png")
    else:
        print(f"\n❌ 音频文件测试失败")

if __name__ == "__main__":
    main() 