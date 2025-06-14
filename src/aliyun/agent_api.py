# 步骤 1：发出请求

import os
import json
import dashscope

# 预定义示例响应（用于few-shot提示）
example1_response = json.dumps(
    {
        "info": {"name": "张三", "age": "25岁", "email": "zhangsan@example.com"},
        "hobby": ["唱歌"]
    },
    ensure_ascii=False
)
example2_response = json.dumps(
    {
        "info": {"name": "李四", "age": "30岁", "email": "lisi@example.com"},
        "hobby": ["跳舞", "游泳"]
    },
    ensure_ascii=False
)
example3_response = json.dumps(
    {
        "info": {"name": "王五", "age": "40岁", "email": "wangwu@example.com"},
        "hobby": ["Rap", "篮球"]
    },
    ensure_ascii=False
)

messages=[
        {
            "role": "system",
            "content": f"""提取name、age、email和hobby（数组类型），输出包含info层和hobby数组的JSON。
            示例：
            Q：我叫张三，今年25岁，邮箱是zhangsan@example.com，爱好是唱歌
            A：{example1_response}
            
            Q：我叫李四，今年30岁，邮箱是lisi@example.com，平时喜欢跳舞和游泳
            A：{example2_response}
            
            Q：我的邮箱是wangwu@example.com，今年40岁，名字是王五，会Rap和打篮球
            A：{example3_response}"""
        },
        {
            "role": "user",
            "content": "大家好，我叫刘五，今年34岁，邮箱是liuwu@example.com，平时喜欢打篮球和旅游", 
        },
    ]
response = dashscope.Generation.call(
    # 若没有配置环境变量，请用阿里云百炼API Key将下行替换为：api_key="sk-xxx",
    api_key=os.getenv('DASHSCOPE_API_KEY'),
    model="qwen-plus", 
    messages=messages,
    result_format='message',
    response_format={'type': 'json_object'}
    )
    
json_string = response.output.choices[0].message.content
print(json_string)