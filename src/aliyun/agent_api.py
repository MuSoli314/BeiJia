import dashscope
from http import HTTPStatus
import json


def check_status(component, operation):
    if component.status_code == HTTPStatus.OK:
        print(f"{operation} 成功。")
        return True
    else:
        print(f"{operation} 失败。状态码：{component.status_code}，错误码：{component.code}，错误信息：{component.message}")
        return False


# 1. 创建绘画助手
painting_assistant = dashscope.Assistants.create(
    api_key = "sk-8448e25c726e45b2ac57fbc1b801aa7d",
    model='qwen-max',   # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
    name='解答',
    description='正常回答用户问题',
    instructions='''正常回答用户问题''',
    # tools=[
    #     {'type': 'quark_search', 'description': '用于研究艺术主题'},
    #     {'type': 'text_to_image', 'description': '用于创建视觉示例'}
    # ]
)

if not check_status(painting_assistant, "助手创建"):
    exit()
print(f"painting_assistant id: {painting_assistant.id}")

# 2. 创建一个新线程
thread = dashscope.Threads.create()

if not check_status(thread, "线程创建"):
    exit()
print(f"thread id: {thread.id}")

# 3. 向线程发送消息
message = dashscope.Messages.create(thread.id, content='今天是几号')

if not check_status(message, "消息创建"):
    exit()
print(f"message id: {message.id}")

# 4. 在线程上运行助手
run = dashscope.Runs.create(thread.id, assistant_id=painting_assistant.id)

if not check_status(run, "运行创建"):
    exit()
print(f"run id: {run.id}")

# 5. 等待运行完成
print("等待助手处理请求...")
run = dashscope.Runs.wait(run.id, thread_id=thread.id)

if check_status(run, "运行完成"):
    print(f"运行完成，状态：{run.status}")
else:
    print("运行未完成。")
    exit()

# 6. 检索并显示助手的响应
messages = dashscope.Messages.list(thread.id)

if check_status(messages, "消息检索"):
    if messages.data:
        # 显示最后一条消息的内容（助手的响应）
        last_message = messages.data[0]
        print("\n助手的回应：")
        print(json.dumps(last_message, ensure_ascii=False, default=lambda o: o.__dict__, sort_keys=True, indent=4))
    else:
        print("在线程中未找到消息。")
else:
    print("未能检索到助手的响应。")

# 提示: 这段代码创建了一个绘画助手，开始了一段关于如何绘制布偶猫的对话，
# 并展示了助手的回答。
# 提示: 这段代码创建了一个绘画助手，开始了一段关于如何绘制布偶猫的对话，
# 并展示了助手的回答。
# 助手创建 成功。
# assistant id: asst_e35b3116-2886-4558-acc2-41e01daf03bd
# 线程创建 成功。
# thread id: thread_46204706-93d8-4194-81d5-ad3607b3c0c3
# 消息创建 成功。
# message id: message_66615473-e7f3-4974-b572-685b174d3f96