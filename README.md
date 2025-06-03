# 英语助教系统 / English Teaching Assistant

一个基于语音识别和AI分析的英语学习助手系统。

## 功能特点 / Features

- 🎤 **语音采集模块** - 实时录音和音频处理
- 🔊 **语音识别模块** - 将语音转换为文本
- 📝 **文本处理模块** - 文本清理和预处理
- 📊 **评分分析模块** - 发音准确性和流利度评估
- 💬 **反馈生成模块** - 智能学习建议生成
- 📋 **结果输出模块** - 详细的学习报告

## 系统架构 / System Architecture

```
用户语音输入 → 语音采集模块 → 语音识别模块 → 文本处理模块 → 评分分析模块 → 反馈生成模块 → 结果输出
```

## 安装说明 / Installation

1. 克隆项目
```bash
git clone <repository-url>
cd BeiJia
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 下载NLTK数据
```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

4. 运行系统
```bash
python main.py
```

## 使用方法 / Usage

1. 启动Web界面：`python app.py`
2. 打开浏览器访问：`http://localhost:5000`
3. 点击录音按钮开始练习
4. 查看评分和反馈建议

## 项目结构 / Project Structure

```
BeiJia/
├── modules/
│   ├── audio_capture.py      # 语音采集模块
│   ├── speech_recognition.py # 语音识别模块
│   ├── text_processing.py    # 文本处理模块
│   ├── scoring_analysis.py   # 评分分析模块
│   ├── feedback_generator.py # 反馈生成模块
│   └── result_output.py      # 结果输出模块
├── static/                   # 静态文件
├── templates/                # HTML模板
├── main.py                   # 主程序
├── app.py                    # Web应用
└── requirements.txt          # 依赖包
```

## 技术栈 / Tech Stack

- **语音识别**: OpenAI Whisper, SpeechRecognition
- **文本处理**: NLTK, TextBlob
- **机器学习**: scikit-learn, transformers
- **Web框架**: Flask
- **音频处理**: PyAudio, librosa, pydub 