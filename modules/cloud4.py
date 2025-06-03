import speech_recognition as sr
import pyttsx3
# import openai
import json
import time
from datetime import datetime
import threading
import queue
import pyaudio
import wave
import language_tool_python
from textblob import TextBlob
import requests

class EnglishTutorAI:
    def __init__(self):
        # 初始化各个模块
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.tts_engine = pyttsx3.init()
        self.grammar_tool = language_tool_python.LanguageTool('en-US')
        
        # 配置TTS引擎
        self.setup_tts()
        
        # OpenAI API配置 (需要设置你的API密钥)
        # openai.api_key = "sk-16d6dc8e440940cabd9f3d9658d81fef"
        
        # 音频队列
        self.audio_queue = queue.Queue()
        
        print("英语口语AI助教初始化完成!")
    
    def setup_tts(self):
        """配置文本转语音引擎"""
        voices = self.tts_engine.getProperty('voices')
        # 尝试设置英语女声
        for voice in voices:
            if 'english' in voice.name.lower() or 'zira' in voice.name.lower():
                self.tts_engine.setProperty('voice', voice.id)
                break
        
        self.tts_engine.setProperty('rate', 150)  # 语速
        self.tts_engine.setProperty('volume', 0.8)  # 音量
    
    def record_audio(self, duration=5):
        """
        模块一：语音采集模块
        录制用户语音
        """
        print(f"开始录音，请说话... ({duration}秒)")
        
        try:
            with self.microphone as source:
                # 调整环境噪音
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                print("请开始说话...")
                
                # 录音
                audio = self.recognizer.listen(source, timeout=duration, phrase_time_limit=duration)
                print("录音完成!")
                return audio
                
        except sr.WaitTimeoutError:
            print("录音超时，请重试")
            return None
        except Exception as e:
            print(f"录音错误: {e}")
            return None
    
    def speech_to_text(self, audio):
        """
        模块二：语音识别(转文本)模块
        将语音转换为文本
        """
        if audio is None:
            return None
            
        try:
            # 使用Google语音识别
            text = self.recognizer.recognize_google(audio, language='en-US')
            print(f"识别结果: {text}")
            return text
            
        except sr.UnknownValueError:
            print("无法识别语音，请重试")
            return None
        except sr.RequestError as e:
            print(f"语音识别服务错误: {e}")
            # 备用方案：使用离线识别
            try:
                text = self.recognizer.recognize_sphinx(audio)
                print(f"离线识别结果: {text}")
                return text
            except:
                return None
    
    def check_grammar(self, text):
        """
        模块三：语法纠错模块
        检查并纠正语法错误
        """
        try:
            matches = self.grammar_tool.check(text)
            corrections = []
            corrected_text = text
            
            for match in matches:
                error_info = {
                    'error': match.message,
                    'suggestions': match.replacements[:3],  # 取前3个建议
                    'context': match.context,
                    'offset': match.offset,
                    'length': match.errorLength
                }
                corrections.append(error_info)
            
            # 应用修正
            corrected_text = language_tool_python.utils.correct(text, matches)
            
            return {
                'original': text,
                'corrected': corrected_text,
                'errors': corrections,
                'error_count': len(corrections)
            }
            
        except Exception as e:
            print(f"语法检查错误: {e}")
            return {
                'original': text,
                'corrected': text,
                'errors': [],
                'error_count': 0
            }
    
    def score_pronunciation(self, text, audio=None):
        """
        模块四：打分模块
        对发音进行评分
        """
        try:
            # 基础评分指标
            score_metrics = {
                'fluency': 0,      # 流利度
                'accuracy': 0,     # 准确度
                'completeness': 0, # 完整度
                'grammar': 0,      # 语法
                'overall': 0       # 总体评分
            }
            
            if not text or len(text.strip()) == 0:
                return score_metrics
            
            # 1. 完整度评分 (基于文本长度和单词数)
            words = text.split()
            word_count = len(words)
            if word_count >= 5:
                score_metrics['completeness'] = min(100, word_count * 10)
            else:
                score_metrics['completeness'] = word_count * 20
            
            # 2. 语法评分
            grammar_result = self.check_grammar(text)
            error_penalty = grammar_result['error_count'] * 10
            score_metrics['grammar'] = max(0, 100 - error_penalty)
            
            # 3. 流利度评分 (基于TextBlob情感分析的置信度)
            try:
                blob = TextBlob(text)
                # 使用句子数量和平均单词长度来评估流利度
                sentences = blob.sentences
                avg_sentence_length = len(words) / max(len(sentences), 1)
                score_metrics['fluency'] = min(100, avg_sentence_length * 15)
            except:
                score_metrics['fluency'] = 70  # 默认分数
            
            # 4. 准确度评分 (基于识别置信度，这里简化处理)
            score_metrics['accuracy'] = 85  # 简化的准确度评分
            
            # 5. 总体评分
            weights = {
                'fluency': 0.3,
                'accuracy': 0.3,
                'completeness': 0.2,
                'grammar': 0.2
            }
            
            score_metrics['overall'] = sum(
                score_metrics[metric] * weight 
                for metric, weight in weights.items()
            )
            
            return score_metrics
            
        except Exception as e:
            print(f"评分错误: {e}")
            return score_metrics
    
    def generate_feedback(self, text, grammar_result, scores):
        """
        模块五：回复模块
        生成个性化反馈
        """
        try:
            feedback_parts = []
            
            # 总体评价
            overall_score = scores['overall']
            if overall_score >= 90:
                feedback_parts.append("Excellent! Your English is very good.")
            elif overall_score >= 75:
                feedback_parts.append("Good job! Your English is quite good.")
            elif overall_score >= 60:
                feedback_parts.append("Not bad! Keep practicing to improve.")
            else:
                feedback_parts.append("Keep practicing! You're making progress.")
            
            # 语法反馈
            if grammar_result['error_count'] > 0:
                feedback_parts.append(f"I found {grammar_result['error_count']} grammar error(s).")
                feedback_parts.append(f"Original: {grammar_result['original']}")
                feedback_parts.append(f"Corrected: {grammar_result['corrected']}")
                
                # 具体错误提示
                for error in grammar_result['errors'][:2]:  # 只提及前2个错误
                    if error['suggestions']:
                        feedback_parts.append(f"Suggestion: {error['suggestions'][0]}")
            
            # 具体建议
            if scores['fluency'] < 70:
                feedback_parts.append("Try to speak more fluently and naturally.")
            
            if scores['grammar'] < 70:
                feedback_parts.append("Pay attention to grammar rules.")
            
            if scores['completeness'] < 50:
                feedback_parts.append("Try to express complete thoughts.")
            
            return "\n ".join(feedback_parts)
            
        except Exception as e:
            print(f"反馈生成错误: {e}")
            return "Thank you for practicing! Keep up the good work."
    
    def text_to_speech(self, text):
        """
        模块六：回复文本转语音模块
        将反馈文本转换为语音
        """
        try:
            print(f"AI反馈: {text}")
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            
        except Exception as e:
            print(f"语音合成错误: {e}")
    
    def practice_session(self):
        """完整的练习会话"""
        print("\n=== 英语口语练习开始 ===")
        print("请准备好开始说英语，我会帮你纠错和评分!")
        
        # 欢迎语音
        welcome_text = "Hello! Welcome to English speaking practice. Please speak in English for 5 seconds."
        self.text_to_speech(welcome_text)
        
        while True:
            try:
                print("\n" + "="*50)
                choice = input("按Enter开始录音，输入'q'退出: ").strip().lower()
                
                if choice == 'q':
                    break
                
                # 1. 语音采集
                audio = self.record_audio(duration=8)
                if audio is None:
                    continue
                
                # 2. 语音识别
                text = self.speech_to_text(audio)
                if text is None:
                    error_msg = "Sorry, I couldn't understand what you said. Please try again."
                    self.text_to_speech(error_msg)
                    continue
                
                # 3. 语法纠错
                grammar_result = self.check_grammar(text)
                
                # 4. 打分
                scores = self.score_pronunciation(text, audio)
                
                # 5. 生成反馈
                feedback = self.generate_feedback(text, grammar_result, scores)
                
                # 显示详细结果
                print(f"\n📝 你说的话: {text}")
                print(f"📊 评分详情:")
                print(f"   - 总体得分: {scores['overall']:.1f}/100")
                print(f"   - 流利度: {scores['fluency']:.1f}/100")
                print(f"   - 准确度: {scores['accuracy']:.1f}/100")
                print(f"   - 完整度: {scores['completeness']:.1f}/100")
                print(f"   - 语法: {scores['grammar']:.1f}/100")
                
                if grammar_result['error_count'] > 0:
                    print(f"✏️  语法纠正: {grammar_result['corrected']}")
                
                # 6. 语音反馈
                self.text_to_speech(feedback)
                
                print(f"\n🤖 AI反馈: {feedback}")
                
            except KeyboardInterrupt:
                print("\n练习被中断")
                break
            except Exception as e:
                print(f"会话错误: {e}")
                continue
        
        # 结束语
        goodbye_text = "Thank you for practicing! Keep up the good work. Goodbye!"
        print(f"\n{goodbye_text}")
        self.text_to_speech(goodbye_text)

def main():
    """主函数"""
    try:
        # 创建AI助教实例
        tutor = EnglishTutorAI()
        
        # 开始练习会话
        tutor.practice_session()
        
    except Exception as e:
        print(f"程序运行错误: {e}")
        print("请确保已安装所有必要的依赖包")

if __name__ == "__main__":
    main()