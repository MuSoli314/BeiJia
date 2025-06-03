#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
英语音频MP3评分系统
包含流利度、完整度、准确度、发音分四个维度的评估
"""

import librosa
import numpy as np
import speech_recognition as sr
from pydub import AudioSegment
import tempfile
import os
from textstat import flesch_reading_ease
import re
from difflib import SequenceMatcher
import json
from datetime import datetime

class EnglishAudioScorer:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        
    def convert_mp3_to_wav(self, mp3_path):
        """将MP3文件转换为WAV格式以便处理"""
        try:
            audio = AudioSegment.from_mp3(mp3_path)
            temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            audio.export(temp_wav.name, format="wav")
            return temp_wav.name
        except Exception as e:
            print(f"音频转换错误: {e}")
            return None
    
    def extract_audio_features(self, audio_path):
        """提取音频特征用于评分"""
        try:
            y, sr = librosa.load(audio_path)
            
            # 音频长度
            duration = librosa.get_duration(y=y, sr=sr)
            
            # 音频能量和静音检测
            energy = np.sum(y ** 2) / len(y)
            
            # 语音活动检测 (简单的能量阈值)
            frame_length = 2048
            hop_length = 512
            energy_frames = []
            
            for i in range(0, len(y) - frame_length, hop_length):
                frame_energy = np.sum(y[i:i+frame_length] ** 2)
                energy_frames.append(frame_energy)
            
            energy_frames = np.array(energy_frames)
            threshold = np.mean(energy_frames) * 0.1
            speech_frames = np.sum(energy_frames > threshold)
            speech_ratio = speech_frames / len(energy_frames) if len(energy_frames) > 0 else 0
            
            # 基频分析
            pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
            pitch_values = []
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                if pitch > 0:
                    pitch_values.append(pitch)
            
            pitch_variation = np.std(pitch_values) if pitch_values else 0
            
            # 语速计算 (粗略估计)
            zero_crossings = librosa.zero_crossings(y).sum()
            speaking_rate = zero_crossings / duration if duration > 0 else 0
            
            return {
                'duration': duration,
                'energy': energy,
                'speech_ratio': speech_ratio,
                'pitch_variation': pitch_variation,
                'speaking_rate': speaking_rate
            }
        except Exception as e:
            print(f"音频特征提取错误: {e}")
            return None
    
    def speech_to_text(self, wav_path):
        """语音转文字"""
        try:
            with sr.AudioFile(wav_path) as source:
                audio = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio, language='en-US')
                return text
        except sr.UnknownValueError:
            return ""
        except sr.RequestError as e:
            print(f"语音识别服务错误: {e}")
            return ""
        except Exception as e:
            print(f"语音转文字错误: {e}")
            return ""
    
    def calculate_fluency_score(self, audio_features, recognized_text):
        """计算流利度分数 (0-100)"""
        try:
            # 语音活动比例 (40%)
            speech_activity_score = min(audio_features['speech_ratio'] * 100, 100) * 0.4
            
            # 语速适中性 (30%) - 理想语速约150-200词/分钟
            if audio_features['duration'] > 0:
                word_count = len(recognized_text.split())
                words_per_minute = (word_count / audio_features['duration']) * 60
                # 优化的语速评分
                if 120 <= words_per_minute <= 180:
                    speed_score = 100
                elif 100 <= words_per_minute < 120 or 180 < words_per_minute <= 200:
                    speed_score = 80
                elif 80 <= words_per_minute < 100 or 200 < words_per_minute <= 220:
                    speed_score = 60
                else:
                    speed_score = 40
            else:
                speed_score = 0
            speed_score *= 0.3
            
            # 停顿合理性 (30%) - 基于语音连续性
            pause_score = min(audio_features['speech_ratio'] * 120, 100) * 0.3
            
            total_score = speech_activity_score + speed_score + pause_score
            return round(min(max(total_score, 0), 100))
            
        except Exception as e:
            print(f"流利度计算错误: {e}")
            return 0
    
    def calculate_completeness_score(self, recognized_text, reference_text=None):
        """计算完整度分数 (0-100)"""
        try:
            if not recognized_text.strip():
                return 0
            
            # 文本长度评估 (50%)
            word_count = len(recognized_text.split())
            if word_count >= 50:
                length_score = 100
            elif word_count >= 30:
                length_score = 80
            elif word_count >= 15:
                length_score = 60
            elif word_count >= 5:
                length_score = 40
            else:
                length_score = 20
            length_score *= 0.5
            
            # 句子完整性 (30%)
            sentences = re.split(r'[.!?]+', recognized_text)
            complete_sentences = [s.strip() for s in sentences if len(s.strip().split()) >= 3]
            sentence_score = min(len(complete_sentences) * 25, 100) * 0.3
            
            # 语法结构复杂性 (20%)
            complexity_indicators = [
                'because', 'although', 'however', 'therefore', 'moreover',
                'furthermore', 'nevertheless', 'consequently', 'meanwhile'
            ]
            complexity_count = sum(1 for word in complexity_indicators 
                                 if word in recognized_text.lower())
            complexity_score = min(complexity_count * 20, 100) * 0.2
            
            # 如果有参考文本，计算覆盖度
            if reference_text:
                similarity = SequenceMatcher(None, recognized_text.lower(), 
                                           reference_text.lower()).ratio()
                coverage_bonus = similarity * 20  # 最多20分奖励
            else:
                coverage_bonus = 0
            
            total_score = length_score + sentence_score + complexity_score + coverage_bonus
            return round(min(max(total_score, 0), 100))
            
        except Exception as e:
            print(f"完整度计算错误: {e}")
            return 0
    
    def calculate_accuracy_score(self, recognized_text, reference_text=None):
        """计算准确度分数 (0-100)"""
        try:
            if not recognized_text.strip():
                return 0
            
            # 语法正确性评估 (40%)
            # 简单的语法检查规则
            grammar_score = 80  # 基础分
            
            # 检查常见语法错误
            text_lower = recognized_text.lower()
            
            # 主谓一致性检查 (简化版)
            singular_subjects = ['he', 'she', 'it']
            for subj in singular_subjects:
                pattern = rf'\b{subj}\s+(\w+)'
                matches = re.findall(pattern, text_lower)
                for verb in matches:
                    if verb in ['have', 'are', 'do'] and subj in ['he', 'she', 'it']:
                        grammar_score -= 5
            
            grammar_score = max(grammar_score, 40) * 0.4
            
            # 词汇使用准确性 (35%)
            words = recognized_text.split()
            unique_words = set(word.lower().strip('.,!?";') for word in words)
            vocabulary_diversity = len(unique_words) / len(words) if words else 0
            vocab_score = min(vocabulary_diversity * 150, 100) * 0.35
            
            # 与参考文本的匹配度 (25%)
            if reference_text:
                similarity = SequenceMatcher(None, recognized_text.lower(), 
                                           reference_text.lower()).ratio()
                reference_score = similarity * 100 * 0.25
            else:
                # 无参考文本时基于文本质量评估
                readability = flesch_reading_ease(recognized_text) if len(recognized_text) > 10 else 50
                reference_score = min(max(readability, 0), 100) * 0.25
            
            total_score = grammar_score + vocab_score + reference_score
            return round(min(max(total_score, 0), 100))
            
        except Exception as e:
            print(f"准确度计算错误: {e}")
            return 0
    
    def calculate_pronunciation_score(self, audio_features, recognized_text):
        """计算发音分数 (0-100)"""
        try:
            # 语音清晰度 (40%) - 基于语音识别成功率
            if recognized_text.strip():
                clarity_score = min(len(recognized_text.split()) * 5, 100) * 0.4
            else:
                clarity_score = 0
            
            # 音调变化 (30%) - 自然的语调起伏
            pitch_score = min(audio_features['pitch_variation'] * 2, 100) * 0.3
            
            # 语音能量稳定性 (30%)
            energy_score = min(audio_features['energy'] * 10000, 100) * 0.3
            
            total_score = clarity_score + pitch_score + energy_score
            return round(min(max(total_score, 0), 100))
            
        except Exception as e:
            print(f"发音分数计算错误: {e}")
            return 0
    
    def evaluate_audio(self, mp3_path, reference_text=None):
        """主评估函数"""
        print("开始评估音频文件...")
        
        # 转换音频格式
        wav_path = self.convert_mp3_to_wav(mp3_path)
        if not wav_path:
            return None
        
        try:
            # 提取音频特征
            print("提取音频特征...")
            audio_features = self.extract_audio_features(wav_path)
            if not audio_features:
                return None
            
            # 语音转文字
            print("进行语音识别...")
            recognized_text = self.speech_to_text(wav_path)
            print(f"识别文本: {recognized_text}")
            
            # 计算各项评分
            print("计算评分...")
            fluency_score = self.calculate_fluency_score(audio_features, recognized_text)
            completeness_score = self.calculate_completeness_score(recognized_text, reference_text)
            accuracy_score = self.calculate_accuracy_score(recognized_text, reference_text)
            pronunciation_score = self.calculate_pronunciation_score(audio_features, recognized_text)
            
            # 综合评分
            overall_score = (fluency_score + completeness_score + 
                           accuracy_score + pronunciation_score) / 4
            
            # 构建结果
            result = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'audio_file': os.path.basename(mp3_path),
                'recognized_text': recognized_text,
                'audio_features': {
                    'duration': round(audio_features['duration'], 2),
                    'speech_ratio': round(audio_features['speech_ratio'], 3)
                },
                'scores': {
                    'fluency': round(fluency_score, 1),
                    'completeness': round(completeness_score, 1),
                    'accuracy': round(accuracy_score, 1),
                    'pronunciation': round(pronunciation_score, 1),
                    'overall': round(overall_score, 1)
                },
                'grade': self.get_grade(overall_score)
            }
            
            return result
            
        finally:
            # 清理临时文件
            if os.path.exists(wav_path):
                os.unlink(wav_path)
    
    def get_grade(self, score):
        """根据分数获取等级"""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
    
    def save_result(self, result, output_file='audio_evaluation_result.json'):
        """保存评估结果到文件"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"评估结果已保存到: {output_file}")
        except Exception as e:
            print(f"保存结果错误: {e}")
    
    def print_result(self, result):
        """打印评估结果"""
        if not result:
            print("评估失败")
            return
            
        print("\n" + "="*50)
        print("英语音频评估结果")
        print("="*50)
        print(f"文件: {result['audio_file']}")
        print(f"评估时间: {result['timestamp']}")
        print(f"音频时长: {result['audio_features']['duration']}秒")
        print(f"语音活动比例: {result['audio_features']['speech_ratio']:.1%}")
        print("\n识别文本:")
        print(f"  {result['recognized_text']}")
        print(f"\n评分结果:")
        print(f"  流利度: {result['scores']['fluency']}/100")
        print(f"  完整度: {result['scores']['completeness']}/100")
        print(f"  准确度: {result['scores']['accuracy']}/100")
        print(f"  发音分: {result['scores']['pronunciation']}/100")
        print(f"  综合评分: {result['scores']['overall']}/100")
        print(f"  等级: {result['grade']}")
        print("="*50)


def main():
    """主函数示例"""
    scorer = EnglishAudioScorer()
    
    # 使用示例
    mp3_file = "data/output1.mp3"  # 替换为实际的音频文件路径
    reference_text = "Hi, it's great to catch up again. Do you want to continue our discussion about the food you sold?"  # 可选的参考文本
    
    # 检查文件是否存在
    if not os.path.exists(mp3_file):
        print(f"错误: 找不到音频文件 {mp3_file}")
        print("请确保音频文件路径正确")
        return
    
    # 评估音频
    result = scorer.evaluate_audio(mp3_file, reference_text)
    
    if result:
        # 显示结果
        scorer.print_result(result)
        
        # 保存结果
        scorer.save_result(result, "data/audio_evaluation_result.json")
    else:
        print("音频评估失败")


if __name__ == "__main__":
    # 安装依赖提示
    print("请确保已安装以下依赖包:")
    print("pip install librosa speechrecognition pydub textstat")
    print("还需要安装ffmpeg用于音频处理")
    print("-" * 50)
    
    main()