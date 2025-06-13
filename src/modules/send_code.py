import requests
import json
from typing import Dict, Any, Optional

def send_ver_code(
    mobile: str,
    content: str,
    apikey: str = "N134046ecab",
    secret: str = "1340464f4eb1542c3",
    sign_id: str = "234327",
    template_id: str = "276044",
    api_url: str = "https://api.4321.sh/sms/template"
) -> Dict[str, Any]:
    """
    发送短信验证码
    
    Args:
        apikey (str): API密钥
        secret (str): API密钥对应的secret
        mobile (str): 手机号码
        sign_id (str): 签名ID
        template_id (str): 模板ID
        content (str): 短信内容（验证码）
        api_url (str): API接口地址，默认为 https://api.4321.sh/sms/template
    
    Returns:
        Dict[str, Any]: API响应结果
        
    Raises:
        requests.RequestException: 网络请求异常
        ValueError: 参数验证失败
    """
    
    # 参数验证
    if not all([apikey, secret, mobile, sign_id, template_id, content]):
        raise ValueError("所有参数都不能为空")
    
    # 构建请求数据
    payload = {
        "apikey": apikey,
        "secret": secret,
        "mobile": mobile,
        "sign_id": sign_id,
        "template_id": template_id,
        "content": content
    }
    
    # 设置请求头
    headers = {
        'Content-Type': 'application/json'
    }
    
    try:
        # 发送POST请求
        response = requests.post(
            url=api_url,
            headers=headers,
            data=json.dumps(payload),
            timeout=10
        )
        
        return response
        # 检查HTTP状态码
        # response.raise_for_status()
        
        # # 返回JSON响应
        # return response.json()
    except requests.exceptions.Timeout:
        raise requests.RequestException("请求超时")
    except requests.exceptions.ConnectionError:
        raise requests.RequestException("网络连接错误")
    except requests.exceptions.HTTPError as e:
        raise requests.RequestException(f"HTTP错误: {e}")
    except json.JSONDecodeError:
        raise requests.RequestException("响应格式错误，无法解析JSON")

# 使用示例
if __name__ == "__main__":
    try:
        # 发送验证码示例
        result = send_ver_code(
            mobile="17608476160",
            content="123456"
        )
        print(result.json())
    except Exception as e:
        print("短信发送失败:", str(e))
