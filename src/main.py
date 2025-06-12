import base64
from logging import error, info
import time
from flask import Flask, request, jsonify
import os

from dashscope.threads import Threads, Messages, Runs
from flask_cors import CORS
from flask_sock import Sock

from dashscope.audio.tts import SpeechSynthesizer
from aliyun.agent_operate import AgentOp
from db.pg_select import DbPool
from modules.audio2text import *
from modules.check_score import check_score
from modules.text2audio import text2audio4aly
from utils.add_logs import setup_logger
from utils.base64_to_wav import base64_to_wav
from utils.webm_to_pcm import webm_to_pcm

app = Flask(__name__)
# 允许所有来源访问（开发环境使用，生产环境应指定具体域名）
CORS(app, resources={r"/*": {"origins": "*"}})

sock = Sock(app)

logger = setup_logger()

DATA_FOLDER = 'data'
os.makedirs(DATA_FOLDER, exist_ok=True)

# 创建数据库连接池
db_pool = DbPool()
# 获取user_id agents_id threads_id
threads = db_pool.select_data("threads", "*", True, None)
threads_dict = db_pool.convert_threads(threads)

# 获取环境变量
dashscope_api_key = os.getenv('DASHSCOPE_API_KEY')
# dashscope_api_key = "sk-8448e25c726e45b2ac57fbc1b801aa7d"
# 创建agent操作类型
agent_op = AgentOp(dashscope_api_key)

# 智能体创建
@app.route('/api/agent', methods=['POST'])
def agent_creat():
    json_data = request.get_json()

    response = agent_op.creat(json_data)

    response_json, status_code = response.json(), response.status_code

    # 插入数据库 默认sambert-donna-v1 教育女声
    if status_code==200:
        db_pool.ins_agents(response_json.get("id"), response_json.get("model"), response_json.get("audio_model", "sambert-donna-v1"), response_json.get("name"), response_json.get("description"))

    return jsonify(response_json), status_code

# 智能体列表
@app.route('/api/agent', methods=['GET'])
def agent_list():
    # 获取查询参数
    agents_list = db_pool.select_data("agents", "*", True)

    if agents_list is not None:
        return jsonify(agents_list), 200
    else:
        return jsonify({"error": "server is error"}), 500

# 智能体检索
@app.route('/api/agent/<string:id>', methods=['GET'])
def agent_search(id):
    response = agent_op.search(id)
    # return response #
    return jsonify(response.json()), response.status_code

# 智能体更新
@app.route('/api/agent/<string:id>', methods=['POST'])
def agent_update(id):
    json_data = request.get_json()

    response = agent_op.update(id, json_data)

    response_json, status_code = response.json(), response.status_code

    # 更新数据库
    if status_code==200:
        if "model" in json_data \
        or "name" in json_data \
        or "description" in json_data\
        or "audio_model" in json_data:
            db_pool.update_agents(response_json.get("id"), response_json.get("model"), response_json.get("name"), response_json.get("description"), response_json.get("audio_model"))

    return jsonify(response_json), status_code

# 智能体删除
@app.route('/api/agent/<string:id>', methods=['DELETE'])
def agent_delete(id):
    response = agent_op.delete(id)

    response_json, status_code = response.json(), response.status_code

    # 更新数据库
    if status_code==200:
        db_pool.del_agents(id)

    return jsonify(response_json), status_code

# 线程创建, 并获取历史对话
@app.route("/api/threads", methods=["POST"])
def thread_creat():
    agent_id = request.json["agent_id"]
    user_id = request.json["user_id"]
    # 每个用户开启一个Thread
    # 判断用户是否有进程,如果没有则创建
    thread_id = threads_dict.get(f"{agent_id}__{user_id}", None)
    if thread_id==None:
        # 每个用户开启一个Thread
        thread = Threads.create(metadata={"owner": user_id})
        thread_id = thread.id
        threads_dict[f"{agent_id}__{user_id}"] = thread_id
        # 插入数据库
        db_pool.ins_threads(thread_id, agent_id, user_id)
    info(f"==thread==create success")

    # 获取历史对话
    msgs = Messages.list(thread_id=thread_id, limit=10, order="desc").data
    cnv_msgs = []
    if msgs:
        for msg in msgs:
            text = msg.content[0].text.value
            metadata = msg.metadata
            cnv_msgs.append({
                "text": text,
                "audio": metadata.get("audio"),
                "check": metadata.get("check")
            })
    return jsonify({
        "thread_id": thread_id,
        "msgs": cnv_msgs
    })

@app.route('/api/agent/message/audio_text', methods=["POST"])
def test():
    # 获取查询参数
    json_data = request.json
    thread_id = json_data.get("thread_id")
    types = json_data.get("types")
    content = json_data.get("content")
    audio_model = json_data.get("audio_model", "sambert-donne-v1")

    if types=='audio':
        # 创建唯一的音频文件名
        filename = f"data/audio_{int(time.time())}.wav"
        if base64_to_wav(content, filename, 48000):
            text = audio2text4aly(filename, 48000)
            if text is not None:
                # 创建信息
                msg = Messages.create(
                    thread_id=thread_id,
                    content=text,
                    role="user",
                    metadata={
                        "audio": content,
                    }
                )

                os.remove(filename) # 删除临时音频文件
                
                return {
                    "text": text,
                    "audio": None,
                    "msg_id": msg.id,
                }, 200
            else:
                return {"error": "text is None"}, 200
    elif types=='text':
        audio = text2audio4aly(content, audio_model)
        
        # 创建信息
        msg = Messages.create(
            thread_id=thread_id,
            content=content,
            role="user",
            metadata={
                "audio": audio,
            }
        )

        return {
            "text": content,
            "audio": audio,
            "msg_id": msg.id,
        }, 200
        
    return {"error": "fail"}, 500

# 纠错和评分
@app.route('/api/agent/message/check', methods=['POST'])
def check():
    json_data = request.json
    thread_id = json_data.get('thread_id')
    msg_id = json_data.get('msg_id')
    text = json_data.get('text')

    # 纠错和评分
    check_res = check_score(text)
    info("语法检查完毕")
    
    # 检索消息
    message = Messages.retrieve(
        message_id=msg_id,
        thread_id=thread_id,
    )
    # 更新metadata
    metadata = message.metadata
    metadata['check'] = check_res
    # 更新msg
    thread = Messages.update(
        message_id=msg_id,
        thread_id=thread_id,
        metadata=metadata
    )

    return jsonify(check_res)

# 运行任务创建、执行
@app.route("/api/agent/message/send", methods=["POST"])
async def get_reply():
    json_data = request.json

    agent_id = json_data.get('agent_id')
    thread_id = json_data.get('thread_id')
    audio_model = request.json.get('audio_model', 'sambert-donna-v1')
    text = json_data["text"]

    # 新建run
    run = Runs.create(
        thread_id=thread_id,
        assistant_id=agent_id,
        # stream=True,
        # instructions=False,
    )
    info(f"==run==create success")

    error_msg = ""
    # 等待run完成
    final_run = Runs.wait(run_id=run.id, thread_id=thread_id, timeout_seconds=60)
    # 获取最后一条assistant消息
    msgs = Messages.list(thread_id=thread_id).data
    if msgs:
        last_msg = msgs[0]
        text = last_msg.content[0].text.value
        msg_id = last_msg.id
        print(msg_id)

        # 调用语音合成服务
        audio = text2audio4aly(text, audio_model)
        
        # 将音频数据更新到msg
        thread = Messages.update(
            message_id=msg_id,
            thread_id=thread_id,
            metadata={'audio': audio}
        )

        return jsonify({
            "reply": text,
            "audio": audio,
            # "info": error_msg
        })

    return jsonify({"info": "fail"}), 500

# 将文本转语音
@app.route('/api/agent/message/text2audio', methods=['POST'])
def synthesize():
    # 获取前端传递的文本参数
    audio_model = request.json.get('audio_model', 'sambert-donna-v1')
    text = request.json.get('text', '')

    if text!='':
        # 调用语音合成服务
        audio_data = text2audio4aly(text, model=audio_model)

        if audio_data is not None:
            return {
                "status": "success",
                "audio": audio_data,
                "message": "音频数据已成功生成"
            }, 200
        else:
            return "response", 500
        
    return {'error': "Not find text"}, 400
    
# export DASHSCOPE_API_KEY="sk-8448e25c726e45b2ac57fbc1b801aa7d"
# echo $DASHSCOPE_API_KEY
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)    
# scp -r src root@47.106.71.193://root/bjyy/src_new ZX.9X@mT4JmWsQT