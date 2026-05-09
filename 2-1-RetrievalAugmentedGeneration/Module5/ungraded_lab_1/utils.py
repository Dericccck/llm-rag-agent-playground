# 导入必要的模块和库
from flask import Flask, request, jsonify  # Web 框架组件
import json  # JSON 处理
import os  # 操作系统接口，处理环境变量和路径
import requests  # HTTP 请求库
from contextlib import contextmanager  # 用于创建上下文管理器
import subprocess  # 执行系统子进程命令
import joblib  # 序列化工具，用于加载 .joblib 数据文件
import time  # 时间处理
from together import Together  # Together.ai API 客户端
import weaviate  # Weaviate 向量数据库客户端
from typing import List, Dict, Any  # 类型提示

from sentence_transformers import SentenceTransformer
# 从 Hugging Face 加载预训练的向量模型 (BGE 1.5)，并缓存到本地目录
# model = SentenceTransformer("BAAI/bge-base-en-v1.5", cache_folder = ".models")

custom_path = os.path.expanduser("~/Desktop/AIAgent/models")
# 指定要使用的预训练模型名称
model_name = "BAAI/bge-base-en-v1.5"
# 加载句子转换器（Sentence Transformer）模型
model = SentenceTransformer(model_name, cache_folder=custom_path)


def kill_processes_on_ports(
    ports: List[int],  # 需要检查并清理的端口列表
    *,
    only_listening: bool = True,  # 是否仅针对“监听”状态的进程（推荐）
    include_udp: bool = True,  # 是否包含 UDP 套接字
    force: bool = True,  # 如果进程未正常退出，是否强制杀掉 (SIGKILL)
    timeout: float = 5.0  # 发送终止信号后的等待秒数
) -> Dict[str, Any]:
    """
    清理占用指定端口的进程，常用于防止 Web 服务启动时端口冲突。
    """
    import socket
    import psutil  # 跨平台的进程和系统工具

    target_ports = {int(p) for p in ports}
    results = {
        'pids_targeted': [], 'terminated': [], 'killed': [], 'errors': [], 'ports_with_no_match': []
    }

    # 一次性获取所有网络连接，比遍历进程扫描更快
    try:
        conns = psutil.net_connections(kind='inet') 
    except Exception as e:
        raise RuntimeError(f"无法枚举网络连接: {e}")

    # 映射端口到对应的进程 ID (PID)
    pids = set()
    matched_ports = set()
    for c in conns:
        if not c.laddr: continue
        port = c.laddr.port
        if port not in target_ports: continue

        # 协议过滤逻辑
        if c.type == socket.SOCK_STREAM:  # TCP
            if only_listening and c.status != psutil.CONN_LISTEN: continue
        elif c.type == socket.SOCK_DGRAM:  # UDP
            if not include_udp: continue

        if c.pid is not None:
            pids.add(c.pid)
            matched_ports.add(port)

    results['pids_targeted'] = sorted(pids)
    results['ports_with_no_match'] = sorted(target_ports - matched_ports)

    # 尝试终止进程，必要时进行强制杀除
    procs = []
    for pid in list(pids):
        try:
            p = psutil.Process(pid)
            if not p.is_running(): continue
            p.terminate()  # 发送 SIGTERM（友好终止）
            procs.append(p)
        except (psutil.NoSuchProcess, psutil.ZombieProcess): continue
        except psutil.AccessDenied as e:
            results['errors'].append({'pid': pid, 'error': f'拒绝访问: {e}'})
        except Exception as e:
            results['errors'].append({'pid': pid, 'error': str(e)})

    gone, alive = psutil.wait_procs(procs, timeout=timeout)
    for p in gone:
        results['terminated'].append({'pid': p.pid, 'name': p.name()})

    if alive and force:  # 如果进程仍存活且开启了强制模式
        for p in alive:
            try:
                p.kill()  # 发送 SIGKILL（强制杀除）
            except Exception as e:
                results['errors'].append({'pid': p.pid, 'error': str(e)})
        gone2, alive2 = psutil.wait_procs(alive, timeout=timeout)
        for p in gone2:
            results['killed'].append({'pid': p.pid, 'name': p.name()})
        for p in alive2:
            results['errors'].append({'pid': p.pid, 'error': '强制杀除后依然存活'})

    return results

def get_proxy_url():
    """获取 API 代理 URL，默认为 Together.ai 的官方接口"""
    return os.environ.get('TOGETHER_BASE_URL', 'https://api.together.xyz/')

def get_proxy_headers():
    """获取 API 请求头（包含授权密钥）"""
    return {"Authorization": os.environ.get("TOGETHER_API_KEY", "")}

def get_together_key():
    """获取 Together API 密钥"""
    return os.environ.get("TOGETHER_API_KEY", "")

def make_url():
    """
    根据运行环境自动生成 Phoenix (AI 观测工具) UI 的访问 URL。
    支持 Coursera 实验环境、自定义学习平台以及本地机器。
    """
    BOLD = "\033[1m"  # 终端加粗样式
    RESET = "\033[0m" # 重置样式

    if 'WORKSPACE_ID' in os.environ:
        # 在 Coursera 环境下运行：构建特定的 labs.coursera.org 链接
        lab_id = os.environ['WORKSPACE_ID']
        url = f"http://{lab_id}.labs.coursera.org"
    elif 'HOSTNAME' in os.environ and 'REV_PROXY_BASE_DOMAIN' in os.environ:
        # 在特定的在线学习平台运行：使用反向代理域名
        ip = os.environ['HOSTNAME'].split('.')[0][3:]
        port = 6006  # Phoenix 服务默认端口
        url = os.environ['REV_PROXY_BASE_DOMAIN'].format(ip=ip, port=port)
    else:
        # 在本地机器运行
        url = "http://localhost:6006"
        print(f"{BOLD}在本地机器运行 - 使用 localhost{RESET}")

    print(f"{BOLD}请点击此链接打开 UI 界面: {url}{RESET}")

def restart_kernel():
    """通过直接退出 Python 进程来强制重启 Jupyter 内核"""
    import os
    os._exit(00)

def generate_with_single_input(prompt: str, role: str = 'user', top_p: float = None, 
                               temperature: float = None, max_tokens: int = 500,
                               model: str = "Qwen/Qwen3.5-9B", together_api_key=None, **kwargs):
    """
    LLM 对话生成函数。支持处理采样参数，并根据环境选择直连 API 或通过代理请求。
    """
    payload_top_p = top_p if top_p is not None else None
    payload_temperature = temperature if temperature is not None else None

    payload = {
        "model": model, "messages": [{'role': role, 'content': prompt}],
        "max_tokens": max_tokens, "reasoning": {"enabled": False}, **kwargs
    }
    if payload_temperature is not None: payload["temperature"] = payload_temperature
    if payload_top_p is not None: payload["top_p"] = payload_top_p

    # 判断是使用 DLAI 代理还是 Together SDK
    if (not together_api_key) and ('TOGETHER_API_KEY' not in os.environ):
        url = os.path.join(get_proxy_url(), 'v1/chat/completions')
        response = requests.post(url, json=payload, verify=False)
        if not response.ok: raise Exception(f"调用 LLM 报错: {response.text}")
        json_dict = json.loads(response.text)
    else:
        if together_api_key is None: together_api_key = os.environ['TOGETHER_API_KEY']
        client = Together(api_key=together_api_key)
        json_dict = client.chat.completions.create(**payload).model_dump()
        json_dict['choices'][-1]['message']['role'] = json_dict['choices'][-1]['message']['role'].name.lower()
    
    try:
        # 返回结果中额外包含了 total_tokens 以便进行成本或性能分析
        output_dict = {
            'role': json_dict['choices'][-1]['message']['role'],
            'content': json_dict['choices'][-1]['message']['content'],
            'total_tokens': json_dict['usage']['total_tokens']
        }
    except Exception as e:
        raise Exception(f"解析输出失败: {e}")
    return output_dict

def generate_embedding(prompt: str): 
    """将文本转化为向量。优先使用加载好的本地 BGE 模型。"""
    return model.encode(prompt).tolist()

def cleanup_phoenix_projects():
    """
    清理 Phoenix 观测工具的会话。用于解决项目 ID 冲突或重置监控看板。
    """
    try:
        import phoenix as px
        px.close_app()  # 关闭当前 Phoenix 应用
        time.sleep(2)   # 等待资源释放
        print("Phoenix 清理完成")
    except Exception as e:
        print(f"Phoenix 清理警告: {e}")

def setup_faq_collection():
    """
    在本地 Weaviate 数据库中创建 FAQ（常见问题）集合并导入数据。
    """
    try:
        # 连接到本地 Weaviate 实例（指定 API 端口和 gRPC 端口）
        client = weaviate.connect_to_local(port=8079, grpc_port=50050)
        
        # 如果集合已存在则跳过创建
        if client.collections.exists("Faq"):
            print("FAQ 集合已存在")
            client.close()
            return
        
        # 定义 Schema 并创建集合
        collection = client.collections.create(
            name="Faq",
            properties=[
                weaviate.classes.config.Property(
                    name="question", data_type=weaviate.classes.config.DataType.TEXT,
                ),
                weaviate.classes.config.Property(
                    name="answer", data_type=weaviate.classes.config.DataType.TEXT,
                ),
                weaviate.classes.config.Property(
                    name="type", data_type=weaviate.classes.config.DataType.TEXT,
                ),
            ],
            # 配置向量生成器，使用 Transformers 插件（Weaviate 会自动处理文本到向量的转换）
            vectorizer_config=weaviate.classes.config.Configure.Vectorizer.text2vec_transformers()
        )
        
        # 从本地加载预存的 FAQ 数据文件
        import os
        faq_file_path = os.path.join(os.path.dirname(__file__), "faq.joblib")
        faq_data = joblib.load(faq_file_path)
        
        # 批量执行数据插入
        collection.data.insert_many(faq_data)
        
        print(f"成功创建 FAQ 集合并导入了 {len(faq_data)} 条数据")
        client.close()
        
    except Exception as e:
        print(f"设置 FAQ 集合时出错: {e}")
        if 'client' in locals(): client.close()
        raise