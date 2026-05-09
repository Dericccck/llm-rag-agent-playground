from flask import Flask, request, jsonify  # 导入 Flask 用于创建 Web 服务
import threading  # 导入多线程支持，用于并发执行任务
from sentence_transformers import SentenceTransformer  # 导入本地向量模型加载工具
import json  # 导入 JSON 处理库
import requests  # 导入 HTTP 请求库，用于调用外部 API
from typing import Union, List, Dict, Any  # 导入类型提示，增强代码可读性
import os  # 导入操作系统接口，用于读取环境变量和路径
from contextlib import redirect_stdout, redirect_stderr, contextmanager  # 导入上下文管理器，用于重定向输出或抑制日志
import logging  # 导入日志记录模块
import together  # 导入 Together.ai 的官方 Python 客户端库
import torch  # 导入 PyTorch 深度学习框架
import subprocess  # 导入子进程控制模块，用于执行系统命令
import signal  # 导入信号处理模块，用于终止进程
import sys  # 导入系统参数模块
import httpx  # 导入高性能 HTTP 客户端，支持异步
from openai import OpenAI, DefaultHttpxClient  # 导入 OpenAI SDK 和默认 HTTP 客户端工具

# 把双引号里面的 xxxxx 换成你刚才申请到的真实 API Key
os.environ["TOGETHER_API_KEY"] = "tgp_v1_n6-OMe0CDJCW2LjmReS4WXGnT88VyNjT6kG0Nl-Bg3U"

# 加载预训练的向量模型 (BGE 1.5)，并将模型缓存到本地 .models 文件夹中
# model = SentenceTransformer("BAAI/bge-base-en-v1.5", cache_folder = ".models")

custom_path = os.path.expanduser("~/Desktop/AIAgent/models")
# 指定要使用的预训练模型名称
model_name = "BAAI/bge-base-en-v1.5"
# 加载句子转换器（Sentence Transformer）模型
model = SentenceTransformer(model_name, cache_folder=custom_path)

# 创建自定义的 HTTP 传输层，设置监听地址为 0.0.0.0，并关闭 SSL 证书验证（在代理环境下常用）
transport = httpx.HTTPTransport(local_address="0.0.0.0", verify=False)

# 使用自定义的传输层创建一个默认的 HTTP 客户端实例
http_client = DefaultHttpxClient(transport=transport)

def kill_processes_on_ports(
    ports: List[int],  # 要检查的端口列表
    *,
    only_listening: bool = True,  # 是否只终止处于“监听”状态的进程
    include_udp: bool = True,  # 是否包含 UDP 协议的连接
    force: bool = True,  # 如果进程未响应，是否强制终止 (SIGKILL)
    timeout: float = 5.0  # 发送终止信号后的等待超时时间
) -> Dict[str, Any]:
    """根据端口号清理进程的实用工具函数，常用于释放被占用的 Web 端口。"""
    import socket
    import psutil  # 导入进程和系统监控工具

    target_ports = {int(p) for p in ports}  # 将端口转为集合以便快速查找
    results = {  # 初始化返回结果字典
        'pids_targeted': [], 'terminated': [], 'killed': [], 'errors': [], 'ports_with_no_match': []
    }

    try:
        conns = psutil.net_connections(kind='inet')  # 一次性获取系统中所有的网络连接
    except Exception as e:
        raise RuntimeError(f"无法枚举网络连接: {e}")

    pids = set()
    matched_ports = set()
    for c in conns:
        if not c.laddr: continue  # 跳过没有本地地址的连接
        port = c.laddr.port
        if port not in target_ports: continue  # 跳过不在目标列表中的端口

        if c.type == socket.SOCK_STREAM:  # 如果是 TCP 协议
            if only_listening and c.status != psutil.CONN_LISTEN: continue  # 若指定只处理监听，则跳过已建立的连接
        elif c.type == socket.SOCK_DGRAM:  # 如果是 UDP 协议
            if not include_udp: continue

        if c.pid is not None:
            pids.add(c.pid)  # 记录该端口对应的进程 ID (PID)
            matched_ports.add(port)

    results['pids_targeted'] = sorted(pids)
    results['ports_with_no_match'] = sorted(target_ports - matched_ports)

    procs = []
    for pid in list(pids):
        try:
            p = psutil.Process(pid)
            if not p.is_running(): continue  # 跳过已经停止的进程
            p.terminate()  # 发送常规终止信号 (SIGTERM)
            procs.append(p)
        except (psutil.NoSuchProcess, psutil.ZombieProcess): continue
        except psutil.AccessDenied as e:
            results['errors'].append({'pid': pid, 'error': f'权限不足: {e}'})
        except Exception as e:
            results['errors'].append({'pid': pid, 'error': str(e)})

    gone, alive = psutil.wait_procs(procs, timeout=timeout)  # 等待进程结束
    for p in gone:
        results['terminated'].append({'pid': p.pid, 'name': p.name()})

    if alive and force:  # 如果仍有进程存活且开启了强制模式
        for p in alive:
            try:
                p.kill()  # 强行杀掉进程 (SIGKILL)
            except (psutil.NoSuchProcess, psutil.ZombieProcess): continue
            except Exception as e:
                results['errors'].append({'pid': p.pid, 'error': str(e)})
        gone2, alive2 = psutil.wait_procs(alive, timeout=timeout)
        for p in gone2:
            results['killed'].append({'pid': p.pid, 'name': p.name()})
        for p in alive2:
            results['errors'].append({'pid': p.pid, 'error': '强制终止后依然存活'})

    return results

def get_proxy_url():
    """从环境变量获取代理 URL，默认为 Together.ai 的官方接口。"""
    return os.environ.get('TOGETHER_BASE_URL', 'https://api.together.xyz/')

def get_proxy_headers():
    """获取 API 调用所需的认证请求头。"""
    return {"Authorization": os.environ.get("TOGETHER_API_KEY", "")}

def get_together_key():
    """获取 Together.ai 的 API 密钥。"""
    return os.environ.get("TOGETHER_API_KEY", "")

def generate_embedding(prompt: str):
    """将文本转换为向量。优先使用本地模型，若本地不可用则调用 API。"""
    return model.encode(prompt).tolist()  # 使用加载好的本地模型进行推理并转为列表

def generate_with_single_input(prompt: str, role: str = 'user', top_p: float = None, 
                               temperature: float = None, max_tokens: int = 500,
                               model: str ="Qwen/Qwen3.5-9B", together_api_key = None, **kwargs):
    """封装单次对话请求，支持通过 DLAI 代理或 Together API 调用大模型。"""
    if top_p is None: top_p = 'none'
    if temperature is None: temperature = 'none'

    payload = {  # 构建请求载体
            "model": model, "messages": [{'role': role, 'content': prompt}],
            "top_p": top_p, "temperature": temperature, "max_tokens": max_tokens,
            "reasoning": {"enabled": False}, **kwargs
    }
    # 判断是否使用 DLAI 代理（通常用于教学环境）
    if (not together_api_key) and ('TOGETHER_API_KEY' not in os.environ):
        url = os.path.join('https://proxy.dlai.link/coursera_proxy/together', 'v1/chat/completions')   
        response = requests.post(url, json = payload, verify=False)
        if not response.ok:
            raise Exception(f"调用 LLM 出错: {response.text}")
        json_dict = json.loads(response.text)
    else:
        # 使用 Together 官方客户端调用
        if together_api_key is None: together_api_key = os.environ['TOGETHER_API_KEY']
        client = Together(api_key =  together_api_key)
        json_dict = client.chat.completions.create(**payload).model_dump()
        json_dict['choices'][-1]['message']['role'] = json_dict['choices'][-1]['message']['role'].name.lower()
    
    try:
        output_dict = {'role': json_dict['choices'][-1]['message']['role'], 'content': json_dict['choices'][-1]['message']['content']}
    except Exception as e:
        raise Exception(f"解析输出失败: {e}")
    return output_dict

def generate_with_multiple_input(messages: List[Dict], top_p: float = 1, temperature: float = 1,
                               max_tokens: int = 500, model: str ="Qwen/Qwen3.5-9B", 
                                together_api_key = None, **kwargs):
    """封装多轮对话请求（传入整个 messages 历史）。"""
    payload = {
        "model": model, "messages": messages, "top_p": top_p,
        "temperature": temperature, "max_tokens": max_tokens,
        "reasoning": {"enabled": False}, **kwargs
    }
    # 逻辑同单次输入函数，适配 DLAI 代理或官方 API
    if (not together_api_key) and ('TOGETHER_API_KEY' not in os.environ):
        url = os.path.join('https://proxy.dlai.link/coursera_proxy/together', 'v1/chat/completions')   
        response = requests.post(url, json = payload, verify=False)
        if not response.ok: raise Exception(f"调用 LLM 出错: {response.text}")
        json_dict = json.loads(response.text)
    else:
        if together_api_key is None: together_api_key = os.environ['TOGETHER_API_KEY']
        client = Together(api_key =  together_api_key)
        json_dict = client.chat.completions.create(**payload).model_dump()
        json_dict['choices'][-1]['message']['role'] = json_dict['choices'][-1]['message']['role'].name.lower()
    
    try:
        output_dict = {'role': json_dict['choices'][-1]['message']['role'], 'content': json_dict['choices'][-1]['message']['content']}
    except Exception as e:
        raise Exception(f"解析输出失败: {e}")
    return output_dict

def print_object_properties(obj: Union[dict, list]) -> None:
    """美化打印字典或列表，主要用于查看 RAG 检索结果，并截断超长字段。"""
    t = ''
    items = obj if isinstance(obj, list) else [obj]
    for l in items:
        for x, y in l.items():
            # 针对特定长字段（文章内容、向量值、分块内容）进行截断展示
            if x in ['article_content', 'main_vector', 'chunk']:
                t += f'{x}: {str(y)[:100 if x != "main_vector" else 30]}...(截断)\n'
            else:
                t += f'{x}: {y}\n'
        t += "\n\n"
    print(t)

def print_properties(item):
    """以 JSON 格式美化打印对象的属性属性。"""
    print(json.dumps(item.properties, indent=2, sort_keys=True, default=str))

@contextmanager
def suppress_subprocess_output():
    """
    上下文管理器：静默子进程输出。
    在进入此上下文时，临时修改 subprocess.Popen，将所有 stdout 和 stderr 重定向到 DEVNULL。
    """
    original_popen = subprocess.Popen  # 保存原始的 Popen 方法

    def patched_popen(*args, **kwargs):
        kwargs['stdout'] = subprocess.DEVNULL  # 强制将输出重定向到空设备
        kwargs['stderr'] = subprocess.DEVNULL  # 强制将错误重定向到空设备
        return original_popen(*args, **kwargs)

    try:
        subprocess.Popen = patched_popen  # 应用补丁
        yield  # 返回控制权给调用者
    finally:
        subprocess.Popen = original_popen  # 无论如何，最后还原原始方法