from flask import Flask, render_template
from flask_sock import Sock
import json
import base64
import os
import threading
import time

app = Flask(__name__)
sock = Sock(app)

# 创建音频文件保存目录
AUDIO_DIR = 'received_audio'
if not os.path.exists(AUDIO_DIR):
    os.makedirs(AUDIO_DIR)

# 存储活跃的WebSocket连接
active_connections = set()

@app.route('/')
def index():
    return render_template('index.html')

@sock.route('/api/ws')
def websocket_handler(ws):
    # 添加连接到活跃连接集合
    active_connections.add(ws)
    print('客户端已连接')
    
    # 发送连接成功消息
    try:
        ws.send(json.dumps({
            'type': 'status',
            'data': {'message': '连接成功'}
        }))
    except Exception as e:
        print(f'发送连接消息失败: {str(e)}')
    
    try:
        while True:
            # 接收客户端消息
            message = ws.receive()
            
            if message:
                try:
                    data = json.loads(message)
                    message_type = data.get('type')
                    payload = data.get('data', {})
                    
                    if message_type == 'audio_data':
                        handle_audio_data(ws, payload)
                    elif message_type == 'start_recording':
                        handle_start_recording(ws)
                    elif message_type == 'stop_recording':
                        handle_stop_recording(ws)
                    else:
                        print(f'未知消息类型: {message_type}')
                        
                except json.JSONDecodeError as e:
                    print(f'JSON解析错误: {str(e)}')
                    send_error(ws, f'JSON解析错误: {str(e)}')
                except Exception as e:
                    print(f'处理消息时出错: {str(e)}')
                    send_error(ws, f'处理消息失败: {str(e)}')
            
    except Exception as e:
        print(f'WebSocket连接错误: {str(e)}')
    finally:
        # 从活跃连接中移除
        active_connections.discard(ws)
        print('客户端已断开连接')

def handle_audio_data(ws, data):
    """处理音频数据"""
    try:
        audio_data = data.get('audio', '')
        timestamp = data.get('timestamp', '')
        
        print(f'接收到音频数据，时间戳: {timestamp}')
        
        if audio_data:
            # 解码base64音频数据
            try:
                # 移除data URL前缀（如果存在）
                if audio_data.startswith('data:audio'):
                    audio_data = audio_data.split(',')[1]
                
                # 解码base64数据
                audio_bytes = base64.b64decode(audio_data)
                
                # 保存音频文件（可选）
                filename = f'audio_{timestamp}.webm'
                filepath = os.path.join(AUDIO_DIR, filename)
                with open(filepath, 'wb') as f:
                    f.write(audio_bytes)
                
                print(f'音频文件已保存: {filepath}，大小: {len(audio_bytes)} bytes')
                
                # 向客户端发送确认
                response = {
                    'type': 'audio_received',
                    'data': {
                        'status': 'success',
                        'message': f'音频数据已接收，大小: {len(audio_bytes)} bytes',
                        'timestamp': timestamp,
                        'filename': filename
                    }
                }
                ws.send(json.dumps(response))
                
                # 这里可以添加音频处理逻辑
                # 例如：语音识别、音频分析等
                # process_audio_file(filepath)
                
            except Exception as decode_error:
                print(f'音频解码错误: {str(decode_error)}')
                send_error(ws, f'音频解码失败: {str(decode_error)}')
        else:
            send_error(ws, '音频数据为空')
            
    except Exception as e:
        print(f'处理音频数据时出错: {str(e)}')
        send_error(ws, f'处理音频数据失败: {str(e)}')

def handle_start_recording(ws):
    """处理开始录音"""
    print('开始录音')
    response = {
        'type': 'recording_status',
        'data': {'status': 'started', 'message': '录音已开始'}
    }
    ws.send(json.dumps(response))

def handle_stop_recording(ws):
    """处理停止录音"""
    print('停止录音')
    response = {
        'type': 'recording_status',
        'data': {'status': 'stopped', 'message': '录音已停止'}
    }
    ws.send(json.dumps(response))

def send_error(ws, error_message):
    """发送错误消息"""
    try:
        response = {
            'type': 'error',
            'data': {
                'status': 'error',
                'message': error_message
            }
        }
        ws.send(json.dumps(response))
    except Exception as e:
        print(f'发送错误消息失败: {str(e)}')

def broadcast_message(message):
    """向所有活跃连接广播消息"""
    disconnected = set()
    for ws in active_connections:
        try:
            ws.send(json.dumps(message))
        except Exception as e:
            print(f'广播消息失败: {str(e)}')
            disconnected.add(ws)
    
    # 移除断开的连接
    for ws in disconnected:
        active_connections.discard(ws)

# 可选：定期向客户端发送心跳
def heartbeat():
    """定期发送心跳消息"""
    while True:
        time.sleep(30)  # 每30秒发送一次心跳
        if active_connections:
            heartbeat_message = {
                'type': 'heartbeat',
                'data': {'timestamp': int(time.time())}
            }
            broadcast_message(heartbeat_message)

# 启动心跳线程
heartbeat_thread = threading.Thread(target=heartbeat, daemon=True)
heartbeat_thread.start()

if __name__ == '__main__':
    print("Flask-Sock WebSocket服务器启动中...")
    print("访问 http://localhost:5000 来测试音频传输")
    app.run(debug=True, host='0.0.0.0', port=5001)