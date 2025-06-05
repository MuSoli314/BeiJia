from logging import info
import requests

class AgentOp:
    def __init__(self, api_key):
        # 目标URL
        self.url = "https://dashscope.aliyuncs.com/api/v1/assistants"  # 替换为你的接口地址

        # 定义请求头
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
    
    def creat(self, json_data):
        response = requests.post(self.url, json=json_data, headers=self.headers)
        return response
    
    def list(self, limit=10, order="desc"):
        response = requests.get(f"{self.url}?limit={limit}&order={order}", headers=self.headers)
        print(f"{self.url}?limit={limit}&order={order}")
        return response

    def search(self, id):
        response = requests.get(f"{self.url}/{id}", headers=self.headers)
        return response

    def update(self, id, json_data):
        response = requests.post(f"{self.url}/{id}", json=json_data, headers=self.headers)
        return response

    def delete(self, id):
        response = requests.delete(f"{self.url}/{id}", headers=self.headers)
        return response

if __name__=="__main__":
    api_key = "sk-8448e25c726e45b2ac57fbc1b801aa7d"
    agent_op = AgentOp(api_key)
    response = agent_op.search("asst_c9426ec9-fb80-4830-88bf-df43434244eb")
    print(response.json())