# 步骤 1：发出请求

import os
import json
import dashscope

# 预定义示例响应（用于few-shot提示）
# 语法纠错
example1_response = json.dumps(
    {
        "currect": "You are cool.",
        "score": 70,
        "currect_msgs": [
            "将 'is' 改为 'are'，以匹配主语 'You' 的复数形式。",
        ],
        "suggest": [
            "You look cool."
            "You’re really cool."
        ]
    },
    ensure_ascii=False
)

def check_score(content, ws=None):
    messages=[
        {
            "role": "user",
            "content": f"""
                请对以下句子进行语法纠错, 纠错后的句子存储在 currect 中,
                纠错信息使用中文在 currect_msgs 中一条一条说明, 
                然后给纠错后的句子进行地道分打分存储在 score 中,
                如果地道分小于80, 请在suggest中列出1到2个更地道的表达, 
                最后以JSON格式输出结果。
                示例：
                Q: "How is you?"
                A: {example1_response}
            """
        },
        {
            "role": "user",
            # "content": "You is cool.", 
            # "content": "How is you?", 
            "content": content,
        },
    ]

    responses = dashscope.Generation.call(
        # 若没有配置环境变量，请用阿里云百炼API Key将下行替换为：api_key="sk-xxx",
        api_key=os.getenv('DASHSCOPE_API_KEY'),
        model="qwen-plus", 
        messages=messages,
        result_format='message',
        response_format={'type': 'json_object'},
        # stream=True, # 流式输出
        # incremental_output=True, # 增量式流式输出
    )
    
    full_content = responses.output.choices[0].message.content

    if ws is not None:
        ws.send(full_content)

    return json.loads(full_content)

    # print("流式输出内容为：")
    # for response in responses:
    #     text = response.output.choices[0].message.content
    #     if ws is not None:
    #         ws.send(text)
    #         # ws.send(json.dumps(return_data))
    # print("====", text)
    # return json.loads(text)

if __name__=="__main__":
    content = "You is cool."
    # content = "How are you?"
    json_data = check_score(content)
    print(json_data['grammar_correction'])