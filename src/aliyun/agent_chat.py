from dashscope import Assistants, Threads, Messages, Runs

def init_assistant() -> str:
    """创建并返回一个assistant_id"""
    assistant = Assistants.create(
        model="qwen-plus",  # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
        name="ChatAssistant",
        instructions="You are a helpful assistant.",
        metadata={"env": "test"}
    )
    return assistant.id

def start_session(assistant_id: str, user_input: str) -> str:
    """创建线程并发送第一条用户消息"""
    # 创建一个线程
    thread = Threads.create(
        metadata={"session_owner": "User123"}
    )
    # 发送用户的第一条消息
    Messages.create(
        thread_id=thread.id,
        content=user_input,
        role="user"
    )
    return thread.id

def get_assistant_reply(assistant_id: str, thread_id: str) -> str:
    """让assistant在该thread上生成回复并返回文本"""
    run = Runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id,
        # 可以覆盖model, instructions等
        model="qwen-plus"
    )
    print(f"=====run===:{run}")
    # 等待run完成
    final_run = Runs.wait(run.id, thread_id=thread_id, timeout_seconds=60)
    # 生成的assistant消息会记录在thread中，第一条是assistant消息（注意：Messages.list 返回的信息是按照创建时间逆序排列的）。
    thread_messages = Messages.list(thread_id=thread_id)
    if thread_messages.data:
        last_msg = thread_messages.data[0]
        return last_msg.content
    return "No reply."

def end_session(thread_id: str):
    """删除thread，级联删除所有消息和run"""
    Threads.delete(thread_id)

# 例子演示
assistant_id = init_assistant()
thread_id = start_session(assistant_id, "你好，请告诉我今天的天气如何？")
reply = get_assistant_reply(assistant_id, thread_id)
print("Assistant reply:", reply)
end_session(thread_id)