# app.py

from flask import Flask, request, jsonify
from dashscope.assistants import Assistants
from dashscope.threads import Threads, Messages

app = Flask(__name__)

# 全局创建一个Assistant
GLOBAL_ASSISTANT = Assistants.create(
    model="qwen-plus", # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
    name="SharedAssistant",
    instructions="You are a helpful system."
)

@app.route("/chat/start", methods=["POST"])
def start_thread():
    user_id = request.json["user_id"]
    # 每个用户开启一个Thread
    thread = Threads.create(metadata={"owner": user_id})
    return jsonify({"thread_id": thread.id})

@app.route("/chat/send", methods=["POST"])
def send_message():
    data = request.json
    thread_id = data["thread_id"]
    content = data["content"]
    
    msg = Messages.create(
        thread_id=thread_id,
        content=content,
        role="user",
    )
    return jsonify({"message_id": msg.id})

@app.route("/chat/reply", methods=["POST"])
def get_reply():
    thread_id = request.json["thread_id"]
    from dashscope.threads import Runs
    run = Runs.create(
        thread_id=thread_id,
        assistant_id=GLOBAL_ASSISTANT.id
    )
    # 等待run完成
    final_run = Runs.wait(run_id=run.id, thread_id=thread_id, timeout_seconds=60)
    
    # 获取最后一条assistant消息
    from dashscope.threads import Messages
    msgs = Messages.list(thread_id=thread_id).items
    if msgs:
        last_msg = msgs[-1]
        return jsonify({"assistant_reply": last_msg.content})
    return jsonify({"assistant_reply": ""})