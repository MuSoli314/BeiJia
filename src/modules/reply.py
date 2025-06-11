
from dashscope.threads import Threads, Messages, Runs

from dashscope.audio.tts import SpeechSynthesizer

def reply_msg(ws, db_pool, assistant_id, thread_id, content):
    msg = Messages.create(
        thread_id=thread_id,
        content=content,
        role="user",
    )

    # 新建
    run = Runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id,
        stream=True,
        # incremental_output=True, # 增量式流式输出
    )

    # 存数据库数据
    # db_data = [thread_id, msg.id, content, None, None, None, None]
    reply_text = ''

    for event, data in run:
        if event == 'thread.run.step.delta':
            tool_call = getattr(data.delta.step_details, 'tool_calls', [None])[0]

            if tool_call and getattr(tool_call, 'type', '') == 'code_interpreter':
                output = getattr(tool_call.code_interpreter, 'output', '')
                reply_text += output
        elif event == 'thread.message.delta':
            content = data.delta.content
            reply_text += content['text']['value']
        # db_data.extend[None, reply_text]
    print(f"----reply_text--{reply_text}")

    ws.send({"ai_reply": reply_text})

    return reply_text, msg.id