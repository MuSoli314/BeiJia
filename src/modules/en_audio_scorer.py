from datetime import datetime
from logging import error, info
import os
import librosa
import numpy as np
# import speech_recognition as sr
import whisper
from textstat import flesch_reading_ease
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
import re
from typing import Dict, Tuple
import warnings
from language_tool_python import LanguageTool
from dashscope.audio.asr import *

warnings.filterwarnings('ignore')

class EnglishAudioScorer:
    def __init__(self):
        """初始化评分系统"""
        # 下载必要的NLTK数据
        self._download_nltk_data()
        
        # 初始化Whisper模型用于语音识别
        self.whisper_model = whisper.load_model("base")
        self.translator = TranslationRecognizerRealtime(
            model="gummy-realtime-v1",
            format="wav",
            sample_rate=16000,
            translation_target_languages=["zh"],
            translation_enabled=True,
            callback=None,
        )
        # 创建语言工具对象
        self.grammar_tool = LanguageTool('en-US')
        
        # 语音特征阈值
        # self.pitch_std_threshold = 50  # 音调变化标准差阈值
        # self.energy_threshold = 0.01   # 能量阈值
    
    def _download_nltk_data(self):
        """下载必要的NLTK数据"""
        # 需要下载的资源列表
        nltk_resources = [
            ('tokenizers/punkt', 'punkt'),
            ('tokenizers/punkt_tab', 'punkt_tab'), 
            ('corpora/stopwords', 'stopwords')
        ]
        
        for resource_path, resource_name in nltk_resources:
            try:
                nltk.data.find(resource_path)
                # print(f"✓ NLTK资源已存在: {resource_name}")
            except LookupError:
                try:
                    print(f"正在下载NLTK资源: {resource_name}")
                    nltk.download(resource_name, quiet=True)
                    print(f"✓ NLTK资源下载成功: {resource_name}")
                except Exception as e:
                    print(f"⚠ NLTK资源下载失败: {resource_name}, 错误: {e}")
                    # 对于punkt_tab，如果下载失败，尝试使用punkt
                    if resource_name == 'punkt_tab':
                        try:
                            nltk.download('punkt', quiet=True)
                            print("✓ 使用punkt作为替代")
                        except:
                            pass
    
    def load_audio(self, wav_path: str) -> Tuple[np.ndarray, int]:
        """加载音频文件"""
        if not os.path.exists(wav_path):
            raise FileNotFoundError(f"音频文件不存在: {wav_path}")
        
        # 使用librosa加载音频
        audio, sr = librosa.load(wav_path, sr=16000)
        return audio, sr
    
    def transcribe_audio(self, wav_path: str) -> str:
        """使用Whisper进行语音转文本"""
        try:
            result = self.whisper_model.transcribe(wav_path)
            return result["text"].strip()
        except Exception as e:
            error(f"语音识别错误: {e}")
            return ""

        """使用Aliyun模型进行语音转文本"""
        # result = self.translator.call(wav_path)
        # if not result.error_message:
        #     print("request id: ", result.request_id)
        #     for transcription_result in result.transcription_result_list:
        #         print(f"transcription: {transcription_result.text}")
        #         return transcription_result.text
        #     for translation_result in result.translation_result_list:
        #         print(f"translation[zh]: : {translation_result.get_translation('zh').text}")
        # else:
        #     print("Error: ", result.error_message)
    
    async def check_grammar(self, text):
        """
        模块三：语法纠错模块
        检查并纠正语法错误
        """
        try:
            matches = self.grammar_tool.check(text)
            
            corrections = []
            corrected_text = text
            
            for match in matches:
                err_txt = text[match.offset : match.offset + match.errorLength]
                # print(f"错误: {match.ruleId}, 建议: {match.replacements}, 位置: {match.offset}-{match.offset + match.errorLength}: {err_txt}")
                error_info = {
                    'error': match.message,
                    'err_text': err_txt,
                    'suggestions': match.replacements[:3],  # 取前3个建议
                    'context': match.context,
                    # 'offset': match.offset,
                    # 'length': match.errorLength
                }
                corrections.append(error_info)
            
            # 修正文本
            corrected_text = self.grammar_tool.correct(text)
            # corrected_text = self.grammar_tool.correct(text, matches)
            
            return {
                'corrected': corrected_text,
                'errors': corrections,
                'error_count': len(corrections)
            }
        except Exception as e:
            print(f"语法检查错误: {e}")
            return {
                'corrected': text,
                'errors': [],
                'error_count': 0
            }
        
    async def analyze_pronunciation(self, audio: np.ndarray, sr: int, transcript: str) -> Dict:
        """分析发音质量"""
        # 提取音频特征
        # 1. 音调特征
        pitches, magnitudes = librosa.piptrack(y=audio, sr=sr)
        pitch_values = []
        for t in range(pitches.shape[1]):
            index = magnitudes[:, t].argmax()
            pitch = pitches[index, t]
            if pitch > 0:
                pitch_values.append(pitch)
        
        # 2. 频谱质心（音色特征）
        spectral_centroids = librosa.feature.spectral_centroid(y=audio, sr=sr)[0]
        
        # 3. 梅尔频率倒谱系数 (MFCC)
        mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
        
        # 4. 语音清晰度评估
        # 基于频谱对比度
        spectral_contrast = librosa.feature.spectral_contrast(y=audio, sr=sr)
        clarity_score = np.mean(spectral_contrast)
        
        # 5. 音调稳定性
        pitch_stability = 1 - (np.std(pitch_values) / np.mean(pitch_values) if pitch_values else 0)
        pitch_stability = max(0, min(1, pitch_stability))
        
        # 综合发音评分 (0-100)
        pronunciation_score = (
            clarity_score * 0.4 +
            pitch_stability * 0.3 +
            (1 - min(1, np.std(spectral_centroids) / 1000)) * 0.3
        ) * 100
        
        return {
            'score': max(1, min(100, pronunciation_score)),
            'pitch_stability': pitch_stability,
            'clarity_score': clarity_score,
            'details': {
                'avg_pitch': np.mean(pitch_values) if pitch_values else 0,
                'pitch_std': np.std(pitch_values) if pitch_values else 0,
                'spectral_centroid_mean': np.mean(spectral_centroids)
            }
        }
    
    async def analyze_fluency(self, audio: np.ndarray, sr: int, transcript: str) -> Dict:
        """分析流利度"""
        # 1. 语速分析
        duration = len(audio) / sr  # 音频时长（秒）
        words = word_tokenize(transcript.lower())
        word_count = len([w for w in words if w.isalpha()])
        
        if duration > 0:
            speaking_rate = word_count / duration * 60  # 每分钟单词数
        else:
            speaking_rate = 0
        
        # 2. 停顿分析
        # 检测静音段
        energy = librosa.feature.rms(y=audio)[0]
        silence_threshold = np.percentile(energy, 20)  # 使用20%分位数作为静音阈值
        silent_frames = energy < silence_threshold
        
        # 计算停顿次数和时长
        pause_count = 0
        pause_duration = 0
        in_pause = False
        
        for i, is_silent in enumerate(silent_frames):
            if is_silent and not in_pause:
                in_pause = True
                pause_count += 1
            elif not is_silent and in_pause:
                in_pause = False
            
            if in_pause:
                pause_duration += 1
        
        pause_duration = pause_duration / sr * len(audio) / len(silent_frames)  # 转换为秒
        
        # 3. 流利度评分
        # 理想语速: 150-180 WPM
        speed_score = 1 - abs(speaking_rate - 165) / 165 if speaking_rate > 0 else 0
        speed_score = max(0, min(1, speed_score))
        
        # 停顿合理性评分
        avg_pause_duration = pause_duration / pause_count if pause_count > 0 else 0
        pause_score = 1 - min(1, avg_pause_duration / 2)  # 停顿超过2秒开始扣分
        
        fluency_score = (speed_score * 0.6 + pause_score * 0.4) * 100
        
        return {
            'score': max(1, min(100, fluency_score)),
            'speaking_rate': speaking_rate,
            'pause_count': pause_count,
            'pause_duration': pause_duration,
            'details': {
                'word_count': word_count,
                'duration': duration,
                'avg_pause_duration': avg_pause_duration
            }
        }
    
    def calculate_overall_score(self, pronunciation: Dict, fluency: Dict) -> float:
        """计算综合评分"""
        # 权重分配：发音30%，流利度40%，地道性30%
        overall_score = (
            pronunciation['score'] * 0.4 +
            fluency['score'] * 0.6
        )
        return round(overall_score, 2)
    
    def score_audio(self, wav_path: str) -> Dict:
        """对音频文件进行综合评分"""
        print(f"正在分析音频文件: {wav_path}")
        
        # 1. 加载音频
        try:
            audio, sr = self.load_audio(wav_path)
            print("✓ 音频加载成功")
        except Exception as e:
            return {'error': f'音频加载失败: {e}'}
        
        # 2. 语音转文本
        try:
            transcript = self.transcribe_audio(wav_path)
            print(f"✓ 语音识别完成: {transcript[:50]}")
        except Exception as e:
            return {'error': f'语音识别失败: {e}'}
        
        if not transcript:
            return {'error': '无法识别语音内容'}
        print(f"==transcribe_audio=={datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")}")
        # transcript = "Hello, you is a good man, you know."
        
        # 3. 文本语法检查
        try:
            grammar_check = self.check_grammar(transcript)
            print(f"✓ 语法检查完成: {grammar_check}")
        except Exception as e:
            return {'error': f'语法检查失败: {e}'}
        
        # 4. 分析各维度
        try:
            pronunciation_result = self.analyze_pronunciation(audio, sr, transcript)
            print(f"✓ 发音分析完成: {pronunciation_result['score']:.1f}/100")
            
            fluency_result = self.analyze_fluency(audio, sr, transcript)
            print(f"✓ 流利度分析完成: {fluency_result['score']:.1f}/100")
            # print(fluency_result)
            
            # 4. 计算综合评分
            overall_score = self.calculate_overall_score(
                pronunciation_result, fluency_result, 
            )
            
            return {
                'overall_score': overall_score,
                'transcript': transcript,
                'grammar_check': grammar_check,
                'pronunciation': pronunciation_result,
                'fluency': fluency_result,
                'analysis_summary': self._generate_summary(
                    overall_score, pronunciation_result, fluency_result
                )
            }
            
        except Exception as e:
            return {'error': f'分析过程出错: {e}'}
    
    def _generate_summary(self, overall: float, pronunciation: Dict, fluency: Dict) -> str:
        """生成评分总结"""
        if overall >= 85:
            level = "优秀"
        elif overall >= 75:
            level = "良好"
        elif overall >= 60:
            level = "中等"
        elif overall >= 40:
            level = "及格"
        else:
            level = "需要改进"
        
        summary = f"综合评分: {overall:.1f}/100 ({level})\n\n"
        summary += f"发音评分: {pronunciation['score']:.1f}/100\n"
        summary += f"流利度评分: {fluency['score']:.1f}/100\n"
        
        # 改进建议
        suggestions = []
        if pronunciation['score'] < 70:
            suggestions.append("建议加强发音练习，注意音调稳定性")
        if fluency['score'] < 70:
            suggestions.append(f"当前语速: {fluency['speaking_rate']:.0f} WPM，建议保持在150-180 WPM")
        
        if suggestions:
            summary += "改进建议:\n" + "\n".join(f"• {s}" for s in suggestions)
        else:
            summary += "表现优秀！继续保持！"
        
        return summary

# 使用示例和备选方案
def en_audio_score():
    # 创建评分器实例
    try:
        scorer = EnglishAudioScorer()
        print("✓ 评分器初始化成功")
    except Exception as e:
        print(f"评分器初始化失败: {e}")
        print("请尝试手动安装NLTK资源:")
        print("python -c \"import nltk; nltk.download('punkt'); nltk.download('punkt_tab'); nltk.download('stopwords')\"")
        return
    
    # 评分示例
    wav_file = "data/output.wav"  # 替换为实际的音频文件路径
    
    if os.path.exists(wav_file):
        print(f"==1=={datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")}")
        result = scorer.score_audio(wav_file)
        print(f"==0=={datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")}")
        
        if 'error' in result:
            print(f"错误: {result['error']}")
        else:
            print("="*50)
            print("英语对话录音评分结果")
            print("="*50)
            print(result['analysis_summary'])
            print("\n" + "="*50)
            print(f"识别文本: {result['transcript']}")
    else:
        print("请提供有效的WAV文件路径")
        print("\n示例用法:")
        print("scorer = EnglishAudioScorer()")
        print("result = scorer.score_audio('your_audio_file.wav')")
        print("print(result['analysis_summary'])")

if __name__ == "__main__":
    en_audio_score()