import base64
from flask import Flask, request, jsonify
import wave
import os

from dashscope import Assistants
from dashscope.threads import Threads, Messages, Runs

from aliyun.agent_operate import AgentOp
from modules.en_audio_scorer import en_audio_score
from utils.add_logs import setup_logger

app = Flask(__name__)

setup_logger()

# WAV 文件参数
sample_rate = 16000  # 采样率
num_channels = 1     # 单声道
sample_width = 2     # 每个样本的字节数，16 位 PCM 为 2 字节

# 获取环境变量
dashscope_api_key = os.getenv('DASHSCOPE_API_KEY')
# 全局创建一个Assistant
GLOBAL_ASSISTANT = Assistants.get(assistant_id="asst_e35b3116-2886-4558-acc2-41e01daf03bd")

# 创建agent操作类型
# dashscope_api_key = "sk-8448e25c726e45b2ac57fbc1b801aa7d"
agent_op = AgentOp(dashscope_api_key)

# 智能体增删改查
@app.route('/api/agent', methods=['POST'])
def agent_creat():
    json_data = request.get_json()

    response = agent_op.creat(json_data)
    return jsonify(response.json()), response.status_code

@app.route('/api/agent', methods=['GET'])
def agent_list():
    # 获取查询参数
    limit = request.args.get('limit', default=10, type=int)  # 默认值为 10
    order = request.args.get('order', default='desc', type=str)  # 默认值为desc/asc

    response = agent_op.list(limit, order)
    return jsonify(response.json()), response.status_code

@app.route('/api/agent/<string:id>', methods=['GET'])
def agent_search(id):
    response = agent_op.search(id)
    return jsonify(response.json()), response.status_code

@app.route('/api/agent/<string:id>', methods=['POST'])
def agent_update(id):
    json_data = request.get_json()
    response = agent_op.update(id, json_data)
    return jsonify(response.json()), response.status_code

@app.route('/api/agent/<string:id>', methods=['DELETE'])
def agent_delete(id):
    response = agent_op.delete(id)
    return jsonify(response.json()), response.status_code

# 对话
@app.route("/api/chat/start", methods=["POST"])
def start_thread():
    user_id = request.json["user_id"]
    print(user_id)
    # 每个用户开启一个Thread
    thread = Threads.create(metadata={"owner": user_id})
    # thread_fb89e4bb-0313-4f1c-ad03-43a40180522c
    print(thread)
    return jsonify({"thread_id": thread.id})

@app.route("/api/chat/send", methods=["POST"])
def send_message():
    data = request.json
    thread_id = data["thread_id"]
    content = data["content"]
    role = data["role"]
    
    msg = Messages.create(
        thread_id=thread_id,
        content=content,
        role=role,
    )
    return jsonify({"message_id": msg.id})

@app.route("/api/chat/reply", methods=["POST"])
def get_reply():
    thread_id = request.json["thread_id"]
    run = Runs.create(
        thread_id=thread_id,
        assistant_id=GLOBAL_ASSISTANT.id
    )
    # 等待run完成
    final_run = Runs.wait(run_id=run.id, thread_id=thread_id, timeout_seconds=60)
    
    # 获取最后一条assistant消息
    msgs = Messages.list(thread_id=thread_id, limit=1, order='desc')
    # print(msgs)

    if msgs:
        content = msgs['data'][0]['content']
        return jsonify(content)# , msgs.status_code
    
    return jsonify({"assistant_reply": ""})

@app.route("/api/chat/list", methods=["GET"])
def get_chats():
    # 获取查询参数
    limit = request.args.get('limit', default=1, type=int)  # 默认值为 10
    order = request.args.get('order', default='desc', type=str)  # 默认值为desc/asc
    
    # 获取最后一条assistant消息  
    msgs = Messages.list(thread_id="thread_4974cfb8-f4d0-4bfd-9508-26316c3ac43a", limit=limit, order=order)

    if msgs:
        content = msgs['data'][0]['content']
        return jsonify(content)
    return jsonify({"assistant_reply": ""})


@app.route("/api/test", methods=["GET"])
def test():
    return jsonify({"data": "====Success!!!===="})


# export DASHSCOPE_API_KEY="sk-8448e25c726e45b2ac57fbc1b801aa7d"
# echo $DASHSCOPE_API_KEY
if __name__ == '__main__':
    # en_audio_score()
    # app.run(debug=True)

    app.run(host='0.0.0.0', port=5001, debug=True)

# scp -r src root@47.106.71.193://root/bjyy/src_new 7kW4Wq*k8j.iHbB