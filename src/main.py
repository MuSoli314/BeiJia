import asyncio
from logging import error, info
from flask import Flask, request, jsonify
import os

from dashscope import Assistants
from dashscope.threads import Threads, Messages, Runs

from aliyun.agent_operate import AgentOp
from modules.en_audio_scorer import EnglishAudioScorer
from utils.add_logs import setup_logger

app = Flask(__name__)

logger = setup_logger()

logger.info("==begin==")
scorer = EnglishAudioScorer()
info("✓ 评分器初始化成功")

# WAV 文件参数
sample_rate = 16000  # 采样率
num_channels = 1     # 单声道
sample_width = 2     # 每个样本的字节数，16 位 PCM 为 2 字节

# 获取环境变量
dashscope_api_key = os.getenv('DASHSCOPE_API_KEY')
# 全局创建一个Assistant
GLOBAL_ASSISTANT = Assistants.get(assistant_id="asst_453a1a31-2795-4b8b-a347-7fc3cb44f7a6")

# 创建agent操作类型
# dashscope_api_key = "sk-8448e25c726e45b2ac57fbc1b801aa7d"
agent_op = AgentOp(dashscope_api_key)

# 智能体创建
@app.route('/api/agent', methods=['POST'])
def agent_creat():
    json_data = request.get_json()

    response = agent_op.creat(json_data)
    return jsonify(response.json()), response.status_code

# 智能体列表
@app.route('/api/agent', methods=['GET'])
def agent_list():
    # 获取查询参数
    limit = request.args.get('limit', default=10, type=int)  # 默认值为 10
    order = request.args.get('order', default='desc', type=str)  # 默认值为desc/asc

    response = agent_op.list(limit, order)
    return jsonify(response.json()), response.status_code

# 智能体检索
@app.route('/api/agent/<string:id>', methods=['GET'])
def agent_search(id):
    response = agent_op.search(id)
    return jsonify(response.json()), response.status_code

# 智能体更新
@app.route('/api/agent/<string:id>', methods=['POST'])
def agent_update(id):
    json_data = request.get_json()
    response = agent_op.update(id, json_data)
    return jsonify(response.json()), response.status_code

# 智能体删除
@app.route('/api/agent/<string:id>', methods=['DELETE'])
def agent_delete(id):
    response = agent_op.delete(id)
    return jsonify(response.json()), response.status_code

# 线程创建
@app.route("/api/threads", methods=["POST"])
def thread_creat():
    user_id = request.json["user_id"]
    # 每个用户开启一个Thread
    thread = Threads.create(metadata={"owner": user_id})
    return jsonify(thread)

# 线程检索
@app.route("/api/threads/<string:thread_id>", methods=["GET"])
def thread_search(thread_id):
    thread = Threads.retrieve(thread_id)
    return jsonify(thread)

# 线程删除
@app.route("/api/threads/<string:thread_id>", methods=["DELETE"])
def start_delete(thread_id):
    response = Threads.delete(thread_id)
    return jsonify(response)

# 消息创建
@app.route("/api/threads/<string:thread_id>/messages", methods=["POST"])
def message_creat(thread_id):
    data = request.json
    content = data["content"]
    role = data["role"]
    
    msg = Messages.create(
        thread_id=thread_id,
        content=content,
        role=role,
    )
    return jsonify(msg)

# 消息列表
@app.route("/api/threads/<string:thread_id>/messages", methods=["GET"])
def message_list(thread_id):
    # 获取查询参数
    limit = request.args.get('limit', default=10, type=int)  # 默认值为 10
    order = request.args.get('order', default='desc', type=str)  # 默认值为desc/asc
    
    # 获取最后一条assistant消息  
    msgs = Messages.list(thread_id=thread_id, limit=limit, order=order)

    if msgs:
        contents = []

        for msg_data in msgs['data']:
            contents.append(msg_data['content'])

        return jsonify(contents)
    return jsonify({"assistant_reply": ""})

# 运行任务创建、执行
@app.route("/api/threads/<string:thread_id>/reply", methods=["GET"])
def get_reply(thread_id):
    run = Runs.create(
        thread_id=thread_id,
        assistant_id=GLOBAL_ASSISTANT.id
    )
    # 等待run完成
    final_run = Runs.wait(run_id=run.id, thread_id=thread_id, timeout_seconds=60)
    
    # 获取最后一条assistant消息
    msgs = Messages.list(thread_id=thread_id, limit=1, order='desc')
    # info(msgs)

    if msgs:
        content = msgs['data'][0]['content']
        return jsonify(content)# , msgs.status_code
    
    return jsonify({"assistant_reply": ""})

@app.route("/api/threads/<string:thread_id>/send_pcm", methods=["POST"])
async def send_pcm():
    # data = request.json
    # thread_id = data["thread_id"]
    # content = data["content"]
    # role = data["role"]
    info("==0==")

    return_data = {
        "text": "",
        "corrected": "",
        "pronunciation": 0,
        "fluency": 0,
    }

    try:
        # 将pcm编码转换成音频文本

        # 将音频转文本
        wav_path = "data/output.wav"
        info(f"✓ 语音识别开始")
        transcript = scorer.transcribe_audio(wav_path)
        info(f"✓ 语音识别完成: {transcript[:50]}")
        return_data['text'] = transcript

        # 加载
        audio, sr = scorer.load_audio(wav_path)
        info("✓ 音频加载成功")

        # 创建异步任务
        # 语法检查纠错
        grammar_check_task = asyncio.create_task(scorer.check_grammar(transcript))
        # 发音打分
        pronunciation_task = asyncio.create_task(scorer.analyze_pronunciation(audio, sr, transcript))
        # 流利度打分
        fluency_task = asyncio.create_task(scorer.analyze_fluency(audio, sr, transcript))

        # 等待所有任务完成
        grammar_check = await grammar_check_task
        info(f"✓ 语法检查完成: {grammar_check['corrected']}")
        return_data['corrected'] = grammar_check['corrected']
        return_data['correct_errs'] = grammar_check

        pronunciation_res = await pronunciation_task
        info(f"✓ 发音分析完成: {pronunciation_res['score']:.1f}/100")
        return_data['pronunciation'] = int(pronunciation_res['score'])

        fluency_res = await fluency_task
        info(f"✓ 流利度分析完成: {fluency_res['score']:.1f}/100")
        return_data['fluency'] = int(fluency_res['score'])

        # pronunciation_res = scorer.analyze_pronunciation(audio, sr, transcript)
        # info(f"✓ 发音分析完成: {pronunciation_res['score']:.1f}/100")
        # return_data['pronunciation'] = int(pronunciation_res['score'])
        
        # fluency_res = scorer.analyze_fluency(audio, sr, transcript)
        # info(f"✓ 流利度分析完成: {fluency_res['score']:.1f}/100")
        # return_data['fluency'] = int(fluency_res['score'])
    except Exception as e:
        error(f"error: {e}")

    info(f"==1==")
    return jsonify(return_data)

    # 创建msg
    # msg = Messages.create(
    #     thread_id=thread_id,
    #     content=content,
    #     role=role,
    # )

    # # 创建run
    # run = Runs.create(
    #     thread_id=thread_id,
    #     assistant_id=GLOBAL_ASSISTANT.id
    # )
    # # 等待run完成
    # final_run = Runs.wait(run_id=run.id, thread_id=thread_id, timeout_seconds=60)
    
    # # 获取最后一条assistant消息  
    # msgs = Messages.list(thread_id="thread_4974cfb8-f4d0-4bfd-9508-26316c3ac43a", limit=limit, order=order)

    # if msgs:
    #     content = msgs['data'][0]['content']
    #     return jsonify(content)
    # return jsonify({"assistant_reply": ""})

@app.route("/api/test", methods=["GET"])
def test():
    return jsonify({"data": "====Success!!!===="})

# export DASHSCOPE_API_KEY="sk-8448e25c726e45b2ac57fbc1b801aa7d"
# echo $DASHSCOPE_API_KEY
if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host='127.0.0.1', port=5001, debug=True)

# scp -r src root@47.106.71.193://root/bjyy/src_new 7kW4Wq*k8j.iHbB