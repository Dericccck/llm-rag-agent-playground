from flask import Flask, request, jsonify  # 导入 Flask 框架核心组件：应用类、请求对象、JSON 序列化工具
import threading  # 导入多线程库，用于在后台运行 Web 服务器
import json  # 导入 JSON 解析库
import numpy as np  # 导入数值计算库（虽然此处未直接调用，但通常是向量操作的依赖）
import torch  # 导入深度学习框架（通常用于加载后端模型）
import logging  # 导入日志模块，用于控制控制台输出信息
from utils import generate_embedding  # 从自定义的工具包中导入核心函数：将文本转为向量

# 全局初始化模型（注释提示：此处应加载模型，确保只加载一次以节省内存和时间）

app = Flask(__name__)  # 初始化 Flask 应用程序实例

# 定义健康检查接口：常用于容器（如 Docker/K8s）检测服务是否启动成功
@app.route('/.well-known/ready', methods=['GET'])
def readiness_check():
    return "Ready", 200  # 返回字符串和状态码 200

# 定义元数据接口：返回 JSON 格式的服务就绪状态
@app.route('/meta', methods=['GET'])
def readiness_check_2():
    return jsonify({'status': 'Ready'}), 200

# 核心接口：接受文本并返回对应的向量
@app.route('/vectors', methods=['POST']) 
def vectorize():
    try:
        try:
            # 尝试从标准的 JSON 请求体中获取 'text' 字段的内容
            data = request.json.get('text')
        except Exception as e:
            try:
                # 如果 JSON 获取失败，尝试手动解码原始请求数据并转为字符串
                data = request.data.decode("utf-8")
            except Exception as e:
                print(e)  # 打印解码错误

        # 将获取到的字符串数据解析为 Python 对象（如字典或列表）
        text = json.loads(data)
        
        # 统一数据格式：如果是单条字符串，转为列表；如果是字典，取其 'text' 键的值
        if isinstance(text, str):
            text = [text]
        else:
            text = text['text']
            
        # 调用核心算法函数，将文本列表转化为高维向量列表
        embeddings = generate_embedding(text)

        # 返回 JSON 响应，包含计算出的向量数据
        return jsonify({'vector': embeddings})

    except Exception as e:
        # 如果过程中发生任何错误，返回错误信息和 500 状态码
        return jsonify({'error': str(e)}), 500
    
# 禁用 Flask 自带的默认日志记录器
app.logger.disabled = True
# 获取 Web 服务器（Werkzeug）的日志记录器
log = logging.getLogger('werkzeug')
# 设置日志等级为 ERROR（这意味着普通的请求访问日志将不再打印，控制台会更干净）
log.setLevel(logging.ERROR)

# 定义一个运行应用的包装函数
def run_app():
    # 启动 Flask 服务：监听所有网络接口（0.0.0.0），端口 5000，关闭调试模式
    app.run(host='0.0.0.0', port=5000, debug = False)

# 创建一个新线程来运行 Flask 应用
# 这样做的目的是为了不阻塞当前的主线程（比如在 Jupyter Notebook 中可以继续操作）
flask_thread = threading.Thread(target=run_app)
# 启动线程
flask_thread.start()