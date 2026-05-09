from flask import Flask, request, jsonify  # 导入 Flask 核心组件：用于构建 Web 服务器、处理请求和返回 JSON
import threading  # 导入多线程库，用于在不阻塞主线程的情况下运行服务器
import json  # 导入 JSON 解析库，用于处理 API 的数据交互
import numpy as np  # 导入数值计算库（向量处理的常用依赖）
import logging  # 导入日志模块，用于控制控制台的输出流
from utils import generate_embedding  # 从自定义工具包导入核心函数：将文本转化为高维向量
import os  # 导入操作系统接口，用于读取路径或环境变量

app = Flask(__name__)  # 初始化 Flask 应用程序对象

# 健康检查接口：用于自动化部署工具（如 Kubernetes）检测服务是否已经“准备就绪”
@app.route('/.well-known/ready', methods=['GET'])
def readiness_check():
    return "Ready", 200  # 返回字符串和 HTTP 200 状态码

# 元数据状态接口：返回 JSON 格式的服务运行状态
@app.route('/meta', methods=['GET'])
def readiness_check_2():
    return jsonify({'status': 'Ready'}), 200

# 核心功能接口：接收文本并返回其对应的向量（Embedding）
@app.route('/vectors', methods=['POST']) 
def vectorize():
    try:
        try:
            # 尝试从请求的 JSON 体中提取键名为 'text' 的数据
            data = request.json.get('text')
        except Exception as e:
            try:
                # 如果 JSON 解析失败，尝试手动解码原始请求二进制数据为字符串
                data = request.data.decode("utf-8")
            except Exception as e:
                print(e)  # 打印可能的解码错误
        
        # 将获取到的字符串数据解析为 Python 对象
        text = json.loads(data)
        
        # 统一输入格式：如果是单条字符串则转为列表；如果是字典则取出其中的 'text' 列表
        if isinstance(text, str):
            text = [text]
        else:
            text = text['text']
            
        # 调用核心算法函数，将文本列表批量转化为向量
        embeddings = generate_embedding(text)

        # 以 JSON 格式返回计算出的向量数据
        return jsonify({'vector': embeddings})

    except Exception as e:
        # 如果处理过程中出现任何意外，返回错误信息和 500 服务器错误码
        return jsonify({'error': str(e)}), 500
    
# 禁用 Flask 默认的日志记录，避免控制台被频繁的访问记录刷屏
app.logger.disabled = True
# 获取 Flask 底层 Web 服务器 (Werkzeug) 的日志记录器
log = logging.getLogger('werkzeug')
# 设置日志等级为 ERROR（这意味着普通的 GET/POST 访问日志将不再显示）
log.setLevel(logging.ERROR)

# 定义一个运行 Flask 应用的包装函数
def run_app():
    # 启动服务器：监听所有 IP (0.0.0.0)，端口 5000，关闭调试模式
    app.run(host='0.0.0.0', port=5000, debug = False)

# 创建并配置一个新线程来运行 Web 服务器
# 这样你就可以在运行服务器的同时，在主程序里执行其他任务（如数据分析）
flask_thread = threading.Thread(target=run_app)
# 正式启动后台线程
flask_thread.start()