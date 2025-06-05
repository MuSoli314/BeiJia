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
# painting_assistant = dashscope.Assistants.create(
#     model='qwen-max',   # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
#     name='Art Maestro',
#     description='用于绘画和艺术知识的AI助手',
#     instructions='''提供绘画技巧、艺术史和创意指导的信息。
#     使用工具进行研究和生成图像。''',
#     tools=[
#         {'type': 'quark_search', 'description': '用于研究艺术主题'},
#         {'type': 'text_to_image', 'description': '用于创建视觉示例'}
#     ]
# )

# if not check_status(painting_assistant, "助手创建"):
#     exit()

# 2. 创建一个新线程
# thread = dashscope.Threads.create()

# if not check_status(thread, "线程创建"):
#     exit()

# 3. 向线程发送消息
thread_id = "thread_16344e95-e442-4403-8c8d-e6a63de944ec"
message = dashscope.Messages.create(thread_id, content='Could you help me to learn english?')

if not check_status(message, "消息创建"):
    exit()

# 4. 在线程上运行助手
# run = dashscope.Runs.create(thread.id, assistant_id=painting_assistant.id)
run = dashscope.Runs.create(
    thread_id, 
    assistant_id="asst_f362b86b-d930-4005-8861-2cae2b8d87b2"
)

if not check_status(run, "运行创建"):
    exit()
# 5. 等待运行完成
print("等待助手处理请求...")
run = dashscope.Runs.wait(run.id, thread_id=thread_id)

if check_status(run, "运行完成"):
    print(f"运行完成，状态：{run.status}")
else:
    print("运行未完成。")
    exit()

# 6. 检索并显示助手的响应
messages = dashscope.Messages.list(thread_id)

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

# echo "export DASHSCOPE_API_KEY='sk-a8f7756ab8e84626867e2688a3092263'" >> ~/.zshrc