import json  # 导入 JSON 处理库
import requests  # 导入 HTTP 请求库
from typing import Union, List, Dict, Any  # 导入类型提示，增强代码可读性
import os  # 导入操作系统接口，用于读取环境变量
from contextlib import redirect_stdout, redirect_stderr, contextmanager  # 导入上下文管理器，用于控制输出流
import logging  # 导入日志记录模块
import httpx  # 导入高性能 HTTP 客户端
import subprocess  # 导入子进程控制模块，用于执行系统命令
from openai import OpenAI, DefaultHttpxClient  # 导入 OpenAI SDK 组件
from together import Together  # 导入 Together.ai 官方客户端
from sentence_transformers import SentenceTransformer  # 导入本地向量模型加载工具

# 把双引号里面的 xxxxx 换成你刚才申请到的真实 API Key。
# os.environ["TOGETHER_API_KEY"] = "tgp_v1_n6-OMe0CDJCW2LjmReS4WXGnT88VyNjT6kG0Nl-Bg3U"
os.environ["TOGETHER_API_KEY"] = "sk-272ee942c239406681329c73361c2e3e"

custom_path = os.path.expanduser("~/Desktop/AIAgent/models")
# 指定要使用的预训练模型名称
model_name = "BAAI/bge-base-en-v1.5"
# 加载句子转换器（Sentence Transformer）模型
model = SentenceTransformer(model_name, cache_folder=custom_path)

# 创建自定义的 HTTP 传输层：设置监听地址并关闭 SSL 证书验证（在特定的教学或代理环境下很有用）
transport = httpx.HTTPTransport(local_address="0.0.0.0", verify=False)

def get_proxy_url():
    """获取 API 代理地址，默认回退到 Together.ai 的官方端点"""
    return os.environ.get('TOGETHER_BASE_URL', 'https://api.together.xyz/')

def get_proxy_headers():
    """获取 API 调用所需的认证头信息"""
    return {"Authorization": os.environ.get("TOGETHER_API_KEY", "")}

def get_together_key():
    """从环境变量获取 Together API 密钥"""
    return os.environ.get("TOGETHER_API_KEY", "")

# 使用上面定义的自定义传输层创建 HTTP 客户端实例，供 OpenAI SDK 使用
http_client = DefaultHttpxClient(transport=transport)

def kill_processes_on_ports(
    ports: List[int],  # 要清理的端口列表
    *,
    only_listening: bool = True,  # 是否只终止处于“监听”状态的进程
    include_udp: bool = True,  # 是否包含 UDP 端口
    force: bool = True,  # 如果常规终止无效，是否强制杀掉进程 (SIGKILL)
    timeout: float = 5.0  # 发送终止信号后的等待时间
) -> Dict[str, Any]:
    """系统工具：根据端口号杀掉绑定的进程，用于释放被占用的 Web 服务端口"""
    import socket
    import psutil  # 系统进程监控库

    target_ports = {int(p) for p in ports}  # 将端口列表转为集合，方便快速查找
    results = {  # 初始化执行结果记录
        'pids_targeted': [], 'terminated': [], 'killed': [], 'errors': [], 'ports_with_no_match': []
    }

    try:
        conns = psutil.net_connections(kind='inet')  # 一次性获取所有网络连接
    except Exception as e:
        raise RuntimeError(f"无法枚举网络连接: {e}")

    pids = set()
    matched_ports = set()
    for c in conns:
        if not c.laddr: continue
        port = c.laddr.port
        if port not in target_ports: continue

        if c.type == socket.SOCK_STREAM:  # TCP 协议处理
            if only_listening and c.status != psutil.CONN_LISTEN: continue
        elif c.type == socket.SOCK_DGRAM:  # UDP 协议处理
            if not include_udp: continue

        if c.pid is not None:
            pids.add(c.pid)
            matched_ports.add(port)

    results['pids_targeted'] = sorted(pids)
    results['ports_with_no_match'] = sorted(target_ports - matched_ports)

    procs = []
    for pid in list(pids):
        try:
            p = psutil.Process(pid)
            if not p.is_running(): continue
            p.terminate()  # 尝试友好终止进程
            procs.append(p)
        except (psutil.NoSuchProcess, psutil.ZombieProcess): continue
        except psutil.AccessDenied as e:
            results['errors'].append({'pid': pid, 'error': f'权限不足: {e}'})
        except Exception as e:
            results['errors'].append({'pid': pid, 'error': str(e)})

    gone, alive = psutil.wait_procs(procs, timeout=timeout)  # 等待进程退出
    for p in gone:
        results['terminated'].append({'pid': p.pid, 'name': p.name()})

    if alive and force:  # 如果进程依然存在且开启了强制模式
        for p in alive:
            try:
                p.kill()  # 暴力结束进程
            except Exception as e:
                results['errors'].append({'pid': p.pid, 'error': str(e)})
        gone2, alive2 = psutil.wait_procs(alive, timeout=timeout)
        for p in gone2:
            results['killed'].append({'pid': p.pid, 'name': p.name()})
        for p in alive2:
            results['errors'].append({'pid': p.pid, 'error': '强制终止后仍然存活'})

    return results

def print_object_properties(obj: Union[dict, list]) -> None:
    """美化打印 RAG 检索回来的对象属性（如文章内容、向量等），并自动截断长文本"""
    t = ''
    if isinstance(obj, dict):
        keys = sorted(list(obj.keys()))  # 按字母顺序排序键名
        for x in keys:
            y = obj[x]
            # 对超长文本字段进行截断显示，防止控制台被刷屏
            if x in ['article_content', 'chunk']:
                t += f'{x}: {y[:100]}...(已截断)\n'
            elif x == 'main_vector':
                t += f'{x}: {y[:30]}...(已截断)\n'
            else:
                t += f'{x}: {y}\n'
    else:  # 如果输入是列表，则递归处理
        for l in obj:
            print_object_properties(l)
    print(t)

def generate_embedding(prompt: str):
    """核心函数：利用本地加载的 BGE 模型将输入的文本转换为向量列表"""
    return model.encode(prompt).tolist()

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








def generate_with_single_input(prompt: str, role: str = 'user', top_p: float = None, 
                               temperature: float = None, max_tokens: int = 500,
                               # 修改默认模型为你本地安装的 Gemma 4
                               model_name: str = "gemma4:26b-a4b-it-q4_K_M", 
                               **kwargs):
    """
    封装单轮 LLM 调用逻辑，优先连接本地 Ollama 运行的 Gemma 4。
    """
    # 1. 设置 Ollama 的本地 API 地址 (默认端口 11434)
    # /v1/chat/completions 是 OpenAI 兼容接口
    ollama_url = "http://localhost:11434/v1/chat/completions"

    # 2. 构造请求载体
    payload = {
        "model": model_name,
        "messages": [{'role': role, 'content': prompt}],
        "max_tokens": max_tokens,
        "stream": False, # 设置为 False 直接获取完整回复
        **kwargs
    }
    
    # 只有在设置了参数时才添加，避免覆盖模型默认配置
    if temperature is not None: payload["temperature"] = temperature
    if top_p is not None: payload["top_p"] = top_p

    try:
        # 3. 发送本地请求
        response = requests.post(
            ollama_url, 
            json=payload, 
            headers={"Content-Type": "application/json"},
            timeout=60 # 给 26b 模型预留足够的推理时间
        )
        
        if response.status_code != 200:
            raise Exception(f"本地 Ollama 调用报错: {response.text}")
            
        json_dict = response.json()
        
        # 4. 提取回复内容
        return {
            'role': json_dict['choices'][0]['message']['role'], 
            'content': json_dict['choices'][0]['message']['content']
        }
        
    except requests.exceptions.ConnectionError:
        raise Exception("无法连接到 Ollama，请确保 Ollama App 正在运行且模型已加载。")
    except Exception as e:
        raise Exception(f"生成输出失败: {e}")






# def generate_with_single_input(prompt: str, role: str = 'user', top_p: float = None, 
#                                temperature: float = None, max_tokens: int = 500,
#                                model: str ="Qwen/Qwen3.5-9B", together_api_key = None, **kwargs):
#     """封装单轮 LLM 调用逻辑，支持通过代理或官方 Together API。"""
    
#     # 构造请求载体，仅在参数非空时添加，以符合 API 规范
#     payload = {
#         "model": model, "messages": [{'role': role, 'content': prompt}],
#         "max_tokens": max_tokens, "reasoning": {"enabled": False}, **kwargs
#     }
#     if temperature is not None: payload["temperature"] = temperature
#     if top_p is not None: payload["top_p"] = top_p

#     # 判断是否使用 DLAI 代理（通常用于在线实验环境）
#     if (not together_api_key) and ('TOGETHER_API_KEY' not in os.environ):
#         url = os.path.join(get_proxy_url(), 'v1/chat/completions')
#         response = requests.post(url, json = payload, verify=False)
#         if not response.ok: raise Exception(f"调用 LLM 报错: {response.text}")
#         json_dict = json.loads(response.text)
#     else:
#         # 使用官方 SDK 调用
#         if together_api_key is None: together_api_key = os.environ['TOGETHER_API_KEY']
#         client = Together(api_key =  together_api_key)
#         json_dict = client.chat.completions.create(**payload).model_dump()
#         # 兼容角色名的大小写处理
#         json_dict['choices'][-1]['message']['role'] = json_dict['choices'][-1]['message']['role'].name.lower()
    
#     try:
#         return {'role': json_dict['choices'][-1]['message']['role'], 'content': json_dict['choices'][-1]['message']['content']}
#     except Exception as e:
#         raise Exception(f"生成输出字典失败: {e}")

# (此处省略逻辑相似的 generate_with_multiple_input)

def display_widget(llm_call_func, semantic_search_retrieve, bm25_retrieve, hybrid_retrieve, semantic_search_with_reranking):
    """构建 Jupyter 交互界面，允许用户一键对比：语义搜索、关键词(BM25)、混合搜索、重排序以及纯生成的结果"""
    
    def on_button_click(b):
        """点击按钮后的执行逻辑：同时触发 5 种不同的检索/生成流程"""
        query = query_input.value
        top_k = slider.value
        rerank_property = rerank_property_dropdown.value
        for output in [output1, output2, output3, output4, output5]:
            output.clear_output()  # 清空之前的内容
        status_output.clear_output()
        status_output.append_stdout("正在生成结果...\n")
        
        # 定义任务配置列表：输出位置、调用函数、检索器等信息
        retrievals = [
            (output1, llm_call_func, query, semantic_search_retrieve, True),
            (output4, llm_call_func, query, semantic_search_with_reranking, True, True, rerank_property),
            (output2, llm_call_func, query, bm25_retrieve, True),
            (output3, llm_call_func, query, hybrid_retrieve, True),
            (output5, llm_call_func, query, None, False)  # 无 RAG 纯生成对比
        ]
        
        for output, func, query, retriever, use_rag, *extra_info in retrievals:
            use_rerank = extra_info[0] if len(extra_info) > 0 else False
            rr_property = extra_info[1] if use_rerank else None
            # 调用 LLM 并结合检索逻辑
            response = func(query=query, top_k=top_k, use_rag=use_rag, retrieve_function=retriever, use_rerank=use_rerank, rerank_property=rr_property)
            with output:
                display(Markdown(response))  # 将 Markdown 格式的回答渲染到界面上
        status_output.clear_output()

    # --- UI 组件定义 ---
    query_input = widgets.Text(description='', value="简述 2024 年美巴关系...", layout=widgets.Layout(width='70%'))
    query_label = widgets.Label(value="查询内容:", layout=widgets.Layout(width='10%'))
    query_box = widgets.HBox([query_label, query_input])

    slider = widgets.IntSlider(value=5, min=1, max=20, step=1, description='Top K(检索篇数):')
    rerank_property_dropdown = widgets.Dropdown(options=['title', 'chunk'], value='title', description='重排属性:')
    
    # 定义 5 个输出容器及对应的标签
    output_style = {'border': '1px solid #ccc', 'width': '100%', 'height': '300px', 'padding': '10px', 'overflow': 'auto'}
    output1, output2, output3, output4, output5 = [widgets.Output(layout=output_style) for _ in range(5)]
    status_output = widgets.Output()
    
    submit_button = widgets.Button(description="获取所有对比回答", button_style='info')
    submit_button.on_click(on_button_click)
    
    # 布局组织：将 5 种模式分两行排列
    hbox_outputs1 = widgets.HBox([
        widgets.VBox([widgets.Label(value="语义搜索 (Semantic)"), output1], layout={'width': '33%'}),
        widgets.VBox([widgets.Label(value="带重排的语义搜索"), output4], layout={'width': '33%'}),
        widgets.VBox([widgets.Label(value="关键词搜索 (BM25)"), output2], layout={'width': '33%'})
    ])
    hbox_outputs2 = widgets.HBox([
        widgets.VBox([widgets.Label(value="混合搜索 (Hybrid)"), output3], layout={'width': '50%'}),
        widgets.VBox([widgets.Label(value="纯大模型生成 (No RAG)"), output5], layout={'width': '50%'})
    ])
    
    display(query_box, slider, rerank_property_dropdown, submit_button, status_output)
    display(hbox_outputs1, hbox_outputs2)