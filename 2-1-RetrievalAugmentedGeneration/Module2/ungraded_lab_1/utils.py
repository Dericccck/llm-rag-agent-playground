import requests  # 导入请求库，用于发送 HTTP 请求
import json      # 导入 JSON 库，用于解析和生成 JSON 数据
import os        # 导入操作系统接口库，用于读取环境变量
from typing import List, Dict  # 导入类型提示，用于标注列表和字典类型
import matplotlib.pyplot as plt  # 导入绘图库，用于生成图表
import numpy as np  # 导入数值计算库，用于向量运算
from sklearn.decomposition import PCA  # 导入 PCA 算法，用于将高维向量降维到 2D
from ipywidgets import Text, Button, VBox, Output, Layout, HTML  # 导入 Jupyter 交互组件
from IPython.display import display, clear_output, HTML  # 导入 Jupyter 显示控制功能
import matplotlib.cm as cm  # 导入颜色映射库
from matplotlib.colors import ListedColormap  # 导入用于创建自定义颜色表的工具
from adjustText import adjust_text  # 导入自动调整文字位置的库（防止绘图标签重叠）
from io import BytesIO  # 导入内存 IO 流工具
import base64  # 导入 Base64 编码工具
from together import Together  # 导入 Together AI 的官方 Python SDK

def get_proxy_url():
    """
    获取代理 URL，优先从环境变量获取，否则默认为 Together.ai 的官方端点
    """
    return os.environ.get('TOGETHER_BASE_URL', 'https://api.together.xyz/')

def get_proxy_headers():
    """
    获取 API 请求头，包含从环境变量中读取的 API 密钥
    """
    return {"Authorization": os.environ.get("TOGETHER_API_KEY", "")}

def get_together_key():
    """
    直接从环境变量中获取 Together API Key
    """
    return os.environ.get("TOGETHER_API_KEY", "")

def plot_vectors():
    """
    绘制向量图示，并计算展示余弦相似度与欧氏距离
    """
    # 定义两个基础向量 v1 和 v2
    v1 = np.array([1, 2])
    v2 = np.array([1, 1])
    # 定义一组对比向量
    array_v = np.array([[3, 2], [5, 6]])

    # 定义计算余弦相似度的内部函数
    def cosine_similarity(vec1, vec2):
        dot_product = np.dot(vec1, vec2)  # 计算点积
        norm_vec1 = np.linalg.norm(vec1)  # 计算 vec1 的模长
        norm_vec2 = np.linalg.norm(vec2)  # 计算 vec2 的模长
        return dot_product / (norm_vec1 * norm_vec2)  # 返回余弦值

    # 定义计算欧氏距离的内部函数
    def euclidean_distance(vec1, vec2):
        return np.linalg.norm(vec1 - vec2)  # 计算两点间的直线距离

    # 计算 v1、v2 与 array_v 中每个向量的相似度和距离
    cos_sim_v1_array_v = [cosine_similarity(v1, av) for av in array_v]
    cos_sim_v2_array_v = [cosine_similarity(v2, av) for av in array_v]
    euc_dist_v1_array_v = [euclidean_distance(v1, av) for av in array_v]
    euc_dist_v2_array_v = [euclidean_distance(v2, av) for av in array_v]

    # 创建一个 8x8 英寸的画布
    plt.figure(figsize=(8, 8))

    # 使用 quiver 绘制向量 v1 的箭头（红色）
    plt.quiver(0, 0, v1[0], v1[1], angles='xy', scale_units='xy', scale=1, color='#fb5c6b')
    plt.text(v1[0] + 0.1, v1[1], f'v1: {tuple(int(x) for x in v1)}', fontsize=9, color='#191c24')

    # 绘制向量 v2 的箭头（红色）
    plt.quiver(0, 0, v2[0], v2[1], angles='xy', scale_units='xy', scale=1, color='#fb5c6b')
    plt.text(v2[0] + 0.1, v2[1], f'v2: {tuple(int(x) for x in v2)}', fontsize=9, color='#191c24')

    # 循环绘制对比向量组 array_v（青蓝色）
    for i, av in enumerate(array_v):
        plt.quiver(0, 0, av[0], av[1], angles='xy', scale_units='xy', scale=1, color='#08b4cc')
        plt.text(av[0] + 0.1, av[1], f' av[{i}]: {tuple(int(x) for x in av)}', fontsize=9, color='#191c24')

    # 在图表上动态打印计算出的相似度和距离数值
    y_start = 6.5  # 文字起始 y 坐标
    step = 0.3     # 行间距
    for i in range(len(array_v)):
        plt.text(0.5, y_start - (2 * i * step), f'Cos(v1, av[{i}]) = {cos_sim_v1_array_v[i]:.4f}', color='#191c24')
        plt.text(0.5, y_start - ((2 * i + 1) * step), f'Dist(v1, av[{i}]) = {euc_dist_v1_array_v[i]:.4f}', color='#191c24')
        plt.text(3.5, y_start - (2 * i * step), f'Cos(v2, av[{i}]) = {cos_sim_v2_array_v[i]:.4f}', color='#191c24')
        plt.text(3.5, y_start - ((2 * i + 1) * step), f'Dist(v2, av[{i}]) = {euc_dist_v2_array_v[i]:.4f}', color='#191c24')

    # 绘制向量终点的散点
    plt.scatter(array_v[:, 0], array_v[:, 1], color='#191c24', s=10)
    plt.scatter([v1[0], v2[0]], [v1[1], v2[1]], color='#191c24', s=10)

    # 设置坐标轴范围、标签、标题和网格
    plt.xlim(0, 6)
    plt.ylim(0, 7)
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.title("Cosine Similarity & Euclidean Distance", color="#191c24")
    plt.grid(True)
    plt.tight_layout() # 自动调整布局防止重叠
    plt.show() # 显示图表

def display_widget(model):
    """
    在 Jupyter 中创建一个交互式微件，支持实时添加词汇并显示其 Embedding 的 PCA 降维图
    """
    # 初始词汇列表
    sentences = [
        'apple', 'king', 'queen', 'cellphone', 'car', 'automobile', 'fruit', 'man', 'woman',
        "He spoke softly in class", "He whispered quietly during class", "Her daughter brightened the gloomy day"
    ]
    # 使用传入的模型将文本转换为高维向量
    embeddings = model.encode(sentences)

    # 初始化 PCA 模型，设定降维目标为 2 维
    pca = PCA(n_components=2)
    embeddings_2d = pca.fit_transform(embeddings) # 训练并转换初始数据

    # 创建一个输出微件用于承载 Matplotlib 图像
    output_plot = Output()

    # 定义一套柔和的调色板颜色
    pastel_colors = ['#fa5c69', '#425469', '#00b1cd', '#f44549', '#b3a7d4', '#cccccc', '#8bd3dd', '#c7d3d4', '#738578']

    def plot_embeddings():
        """
        内部绘图函数：负责清空旧图并绘制新的 2D 散点图
        """
        with output_plot:
            clear_output(wait=True) # 清除旧的输出
            plt.figure(figsize=(12, 8))

            # 根据当前句子数量动态生成循环颜色映射
            color_count = len(sentences)
            colormap = ListedColormap((pastel_colors * (color_count // len(pastel_colors) + 1))[:color_count])

            texts = []
            # 遍历数据绘制散点
            for color, (label, (x, y)) in zip(colormap.colors, zip(sentences, embeddings_2d)):
                plt.scatter(x, y, color=color, s=100) # 画点
                texts.append(plt.text(x, y, label, fontsize=9, color='black')) # 添加文本标签

            # 调用 adjust_text 自动移动标签位置以避免遮挡点或彼此重叠
            adjust_text(texts, arrowprops=dict(arrowstyle='-', color='gray'))

            plt.title('PCA of Word Embeddings', fontsize=16)
            plt.xlabel('Principal Component 1')
            plt.ylabel('Principal Component 2')
            plt.grid(True, linestyle='--', alpha=0.7)
            plt.show()

    def on_add_word(change):
        """
        按钮点击事件：获取输入框内容，计算 Embedding 并更新图表
        """
        nonlocal embeddings_2d, sentences # 声明使用外部变量
        new_word = word_input.value.strip() # 获取输入框文本
        if new_word:
            new_embedding = model.encode([new_word]) # 转换新词为向量
            new_embedding_2d = pca.transform(new_embedding) # 沿用旧 PCA 模型降维

            # 更新数据列表和矩阵
            sentences.append(new_word)
            embeddings_2d = np.vstack([embeddings_2d, new_embedding_2d])

            word_input.value = ''  # 清空输入框
            plot_embeddings()      # 触发重绘

    # 使用 HTML 定义自定义按钮样式（粉红色背景）
    display(HTML("""
    <style>
        .custom-button {
            background-color: #fa5c69;
            color: white;
            font-weight: bold;
            border: none;
            border-radius: 4px;
        }
        .custom-button:hover { background-color: #6b252b; }
        .output-plot { display: flex; justify-content: center; }
    </style>
    """))

    # 创建文本输入框和提交按钮
    word_input = Text(description="Word/Sentence:", layout=Layout(width='400px'), style={'description_width': 'initial'})
    add_button = Button(description="Add Word or Sentence!", layout=Layout(width='200px'))
    add_button.add_class("custom-button") # 应用 CSS 样式
    add_button.on_click(on_add_word) # 绑定点击事件

    # 布局显示：垂直排列输入框和按钮，下方显示图像
    display(VBox([word_input, add_button], layout=Layout(margin='10px 0')))
    display(HTML("<div class='output-plot'>"))
    display(VBox([output_plot], layout=Layout(align_items='center', justify_content='center')))
    display(HTML("</div>"))

    # 首次进入页面时展示初始图表
    plot_embeddings()

def generate_with_single_input(prompt: str, role: str = 'user', top_p: float = None, 
                               temperature: float = None, max_tokens: int = 500, 
                               model: str ="Qwen/Qwen3.5-9B", together_api_key = None, **kwargs):
    """
    单条 Prompt 生成函数：封装了对 Together AI 接口的调用
    """
    # 预处理参数：如果为 None 则不传递给 API
    payload_top_p = top_p if top_p is not None else None
    payload_temperature = temperature if temperature is not None else None

    # 构建请求负载
    payload = {
        "model": model,
        "messages": [{'role': role, 'content': prompt}],
        "max_tokens": max_tokens,
        "reasoning": {"enabled": False}, # 禁用某些模型的推理链展示
        **kwargs # 支持传入额外参数
    }
    # 仅在参数不为空时加入 payload
    if payload_temperature is not None: payload["temperature"] = payload_temperature
    if payload_top_p is not None: payload["top_p"] = payload_top_p

    # 判断是使用自定义代理请求还是直接使用 Together SDK
    if (not together_api_key) and ('TOGETHER_API_KEY' not in os.environ):
        # 场景 A: 使用 requests 发送 POST 到预设代理（通常用于 Docker 环境）
        url = os.path.join(get_proxy_url(), 'v1/chat/completions')
        response = requests.post(url, json = payload, verify=False)
        if not response.ok:
            raise Exception(f"Error while calling LLM: {response.text}")
        try:
            json_dict = json.loads(response.text)
        except Exception as e:
            raise Exception(f"Failed to parse LLM response: {e}")
    else:
        # 场景 B: 使用 Together 官方 SDK 调用
        if together_api_key is None:
            together_api_key = os.environ['TOGETHER_API_KEY']
        from together import Together
        client = Together(api_key =  together_api_key)
        # 调用 API 并将结果转为字典格式
        json_dict = client.chat.completions.create(**payload).model_dump()
        # 统一角色字段的格式
        json_dict['choices'][-1]['message']['role'] = json_dict['choices'][-1]['message']['role'].name.lower()
    
    try:
        # 提取模型生成的最终内容
        output_dict = {'role': json_dict['choices'][-1]['message']['role'], 'content': json_dict['choices'][-1]['message']['content']}
    except Exception as e:
        raise Exception(f"Failed to get correct output dict: {e}")
    return output_dict

def generate_with_multiple_input(messages: List[Dict], top_p: float = None, 
                                 temperature: float = None, max_tokens: int = 500, 
                                 model: str ="Qwen/Qwen3.5-9B", together_api_key = None, **kwargs):
    """
    多轮对话生成函数：支持传入完整的消息历史 (messages 列表)
    """
    # 参数预处理（同单输入函数）
    payload_top_p = top_p if top_p is not None else None
    payload_temperature = temperature if temperature is not None else None

    payload = {
        "model": model,
        "messages": messages, # 直接传入对话列表
        "max_tokens": max_tokens,
        "reasoning": {"enabled": False},
        **kwargs
    }
    if payload_temperature is not None: payload["temperature"] = payload_temperature
    if payload_top_p is not None: payload["top_p"] = payload_top_p

    # API 调用逻辑（同单输入函数）
    if (not together_api_key) and ('TOGETHER_API_KEY' not in os.environ):
        url = os.path.join(get_proxy_url(), 'v1/chat/completions')
        response = requests.post(url, json = payload, verify=False)
        if not response.ok:
            raise Exception(f"Error while calling LLM: {response.text}")
        try:
            json_dict = json.loads(response.text)
        except Exception as e:
            raise Exception(f"Failed to parse response: {e}")
    else:
        if together_api_key is None:
            together_api_key = os.environ['TOGETHER_API_KEY']
        from together import Together
        client = Together(api_key =  together_api_key)
        json_dict = client.chat.completions.create(**payload).model_dump()
        json_dict['choices'][-1]['message']['role'] = json_dict['choices'][-1]['message']['role'].name.lower()
    
    try:
        output_dict = {'role': json_dict['choices'][-1]['message']['role'], 'content': json_dict['choices'][-1]['message']['content']}
    except Exception as e:
        raise Exception(f"Failed to get output: {e}")
    return output_dict