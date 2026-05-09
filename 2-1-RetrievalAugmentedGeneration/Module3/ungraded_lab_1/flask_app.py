from flask import Flask, request, jsonify  # 导入 Flask 用于构建 Web 接口
import threading  # 导入多线程，用于在后台运行服务
import json  # 导入 JSON 处理
from FlagEmbedding import FlagReranker  # 导入 BGE 重排序模型工具
import numpy as np  # 导入数值计算库
import torch  # 导入深度学习框架 PyTorch
import logging  # 导入日志管理
import os  # 导入系统接口
from utils import generate_embedding  # 从你之前的 utils 文件中导入向量生成函数

# 全局初始化模型：确保模型只加载一次，避免重复占用显存/内存
# 使用 BGE-Reranker-Base 模型，并指定缓存目录
reranker = FlagReranker('BAAI/bge-reranker-base', cache_dir=os.environ["MODEL_M3"], use_fp16=False)

app = Flask(__name__)  # 初始化 Flask 应用

# 健康检查接口：用于容器或集群判断服务是否已经启动
@app.route('/.well-known/ready', methods=['GET'])
def readiness_check():
    return "Ready", 200

# 另一个元数据接口：返回 JSON 格式的服务状态
@app.route('/meta', methods=['GET'])
def readiness_check_2():
    return jsonify({'status': 'Ready'}), 200

# 重排序接口：这是 RAG 系统中提升精度的关键步骤
@app.route('/rerank', methods=['POST'])
def rerank():
    try:
        data = None
        try:
            # 尝试解析 JSON 数据
            data = request.json
            if data is None:
                # 如果请求头不是 JSON，尝试直接读取原始数据并解码
                text_str = request.data.decode("utf-8")
                data = json.loads(text_str)
            text = data
        except Exception as e:
            # 备选解析逻辑，处理不规范的请求体
            try:
                text_str = request.data.decode("utf-8")
                text = json.loads(text_str)
            except Exception as e_inner:
                print(f"解析请求数据出错: {e_inner}")
                return jsonify({'error': f"无法解析请求体: {e_inner}"}), 400

        # 验证输入格式是否符合 Weaviate 等工具的预期（必须包含查询和文档列表）
        if not isinstance(text, dict) or 'query' not in text or 'documents' not in text:
            print(f"输入格式无效。预期包含 'query' 和 'documents' 的字典。实际得到: {text}")
            return jsonify({'error': "输入格式无效。"}), 400

        query = text['query']  # 用户的搜索关键词
        documents = text['documents']  # 初步检索回来的候选文档列表

        if not documents:
            # 如果没有文档需要重排，直接返回空分数列表，防止程序崩溃
            return jsonify({'scores': []})

        # 准备模型输入：将查询与每一个文档配对，形成 [(query, doc1), (query, doc2)...]
        compares = [(query, doc) for doc in documents]
        
        # 使用重排序模型计算得分：模型会深度对比每一对的相关性
        scores = reranker.compute_score(compares)

        # 将 NumPy 数组或张量结果转换为标准的 Python 列表，方便 JSON 序列化
        scores_list = scores.tolist() if hasattr(scores, 'tolist') else scores

        # 构造响应：Weaviate 的 reranker-transformers 模块要求返回包含文档和分数的列表
        reranked_results = []
        for i, doc_text in enumerate(documents):
            score = scores_list[i]
            reranked_results.append({
                "document": doc_text,  # 原始文档文本
                "score": float(score)  # 计算出的相关度分数（分数越高越相关）
            })

        return jsonify({'scores': reranked_results}) # 返回结果给调用方

    except Exception as e:
        print(f"重排序接口发生未处理错误: {e}")
        return jsonify({'error': str(e)}), 500

# 文本向量化接口：将文字转化为数字向量
@app.route('/vectors', methods=['POST']) 
def vectorize():
    try:
        try:
            data = request.json.get('text')
        except Exception as e:
            try:
                data = request.data.decode("utf-8")
            except Exception as e:
                print(e)
        
        text = json.loads(data)
        # 如果传入的是单个字符串，转为列表统一处理
        if isinstance(text, str):
            text = [text]
        else:
            text = text['text']
            
        # 调用 utils 中的函数生成向量（Embedding）
        embeddings = generate_embedding(text)

        return jsonify({'vector': embeddings})

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# 禁用 Flask 默认的日志打印，让控制台保持干净
app.logger.disabled = True
log = logging.getLogger('werkzeug')
# 将日志级别设为 ERROR，这样就不会在控制台看到每一条 HTTP 请求的滚动信息
log.setLevel(logging.ERROR)

# 定义启动 Flask 的函数
def run_app():
    # 监听所有 IP (0.0.0.0)，端口 5000
    app.run(host='0.0.0.0', port=5000, debug=False)

# 在独立的线程中启动 Flask 服务，防止阻塞主程序的其他逻辑
flask_thread = threading.Thread(target=run_app)
flask_thread.start()