import json  # 导入 JSON 处理库，用于解析 API 返回的数据
import requests  # 导入 HTTP 请求库，用于发送网络请求
import os  # 导入操作系统接口，用于读取环境变量
import re  # 导入正则库（虽然此代码段未直接使用，但常用于文本处理）
from typing import List, Dict, Any, Union  # 导入类型提示，增强代码可维护性
from together import Together  # 导入 Together.ai 官方 Python 客户端



from dotenv import load_dotenv
from openai import OpenAI

# 1. 基础配置
def get_qwen_client():
    """
    根据你截图中的逻辑，初始化并返回阿里云 Qwen 客户端
    """
    load_dotenv()# 这一行会自动寻找并加载同目录下的 .env 文件
    # 确保你已经安装了 openai 库: pip install openai

    client = OpenAI(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )
    return client

def generate_params_dict(
    prompt: str,
    temperature: float = None,
    role = 'user',
    top_p: float = None,
    max_tokens: int = 500,
    model: str = "Qwen/Qwen3.5-9B"
):
    """
    构建一个包含采样参数的字典，用于观察不同参数对 LLM 生成效果的影响。

    参数说明：
        temperature: 控制随机性（越低越确定，越高越有创意）。
        top_p: 核采样参数（通过概率阈值控制词汇多样性）。
    """
    # 将所有传入的参数打包成一个字典并返回
    kwargs = {
        "prompt": prompt, 
        'role': role, 
        "temperature": temperature, 
        "top_p": top_p, 
        "max_tokens": max_tokens, 
        'model': model
    }
    return kwargs

def generate_with_single_input(prompt: str,
                               role: str = 'user',
                               top_p: float = None,
                               temperature: float = None,
                               max_tokens: int = 512,
                               model: str = "qwen-plus",
                               **kwargs):
    """
    使用阿里云 Qwen 封装单次输入请求
    """
    client = get_qwen_client()
    
    # 构造消息体
    messages = [{'role': role, 'content': prompt}]
    
    # 构建请求参数，过滤掉 None 值
    params = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        **kwargs
    }
    if temperature is not None: params["temperature"] = temperature
    if top_p is not None: params["top_p"] = top_p

    try:
        # 调用 DashScope 兼容接口
        response = client.chat.completions.create(**params)
        
        # 提取结果并转换为字典格式
        message = response.choices[0].message
        return {
            'role': message.role, 
            'content': message.content
        }
    except Exception as e:
        raise Exception(f"调用 Qwen (单轮) 失败: {e}")

def generate_with_multiple_input(messages: List[Dict],
                                 top_p: float = None,
                                 temperature: float = None,
                                 max_tokens: int = 512,
                                 model: str = "qwen-plus",
                                 **kwargs):
    """
    使用阿里云 Qwen 封装多轮对话请求
    """
    client = get_qwen_client()
    
    params = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        **kwargs
    }
    if temperature is not None: params["temperature"] = temperature
    if top_p is not None: params["top_p"] = top_p

    try:
        response = client.chat.completions.create(**params)
        message = response.choices[0].message
        return {
            'role': message.role, 
            'content': message.content
        }
    except Exception as e:
        raise Exception(f"调用 Qwen (多轮) 失败: {e}")

# 这个函数逻辑保持不变，它依赖于上面的 generate_with_multiple_input
def call_llm_with_context(prompt: str, context: list,  role: str = 'user', **kwargs):
    """
    核心业务逻辑：通过维护 context 列表来实现有记忆的对话（多轮对话）。

    参数：
        prompt: 用户当前输入。
        context: 存储对话历史的列表，函数会自动更新它。
    """

    # 步骤 1：将用户当前的问题打包成字典，并追加到对话历史中
    context.append({'role': role, 'content': prompt})

    # 步骤 2：调用多轮对话函数，获取模型的回答
    response = generate_with_multiple_input(context, **kwargs)

    # 步骤 3：将模型生成的回答也追加到对话历史中，以便下一次调用时包含此上下文
    context.append(response)

    return response



















# def get_proxy_url():
#     """
#     从环境变量中获取代理 URL，如果未设置，则默认使用 Together.ai 的官方端点。
#     主要用于 Docker 容器化部署或特定网络环境。
#     """
#     return os.environ.get('TOGETHER_BASE_URL', 'https://api.together.xyz/')

# def get_proxy_headers():
#     """
#     获取 API 调用所需的认证请求头，包含 Together API Key。
#     """
#     return {"Authorization": os.environ.get("TOGETHER_API_KEY", "")}

# def get_together_key():
#     """
#     直接从环境变量中提取 Together API 密钥。
#     """
#     return os.environ.get("TOGETHER_API_KEY", "")




# def generate_with_single_input(prompt: str,
#                                role: str = 'user',
#                                top_p: float = None,
#                                temperature: float = None,
#                                max_tokens: int = 500,
#                                model: str ="Qwen/Qwen3.5-9B",
#                                together_api_key = None,
#                               **kwargs):
#     """封装单次输入请求，支持自动选择调用路径（代理服务器 vs. 官方 SDK）。"""

#     # 处理采样参数：如果为 None，则保持为 None，不要设置成字符串 'none'
#     payload_top_p = top_p if top_p is not None else None
#     payload_temperature = temperature if temperature is not None else None

#     # 构建请求负载（Payload）
#     payload = {
#         "model": model,
#         "messages": [{'role': role, 'content': prompt}],
#         "max_tokens": max_tokens,
#         "reasoning": {"enabled": False},  # 关闭部分模型的推理过程展示（如果适用）
#         **kwargs
#     }
    
#     # 仅在参数不为空时加入负载，避免覆盖 API 的默认行为
#     if payload_temperature is not None:
#         payload["temperature"] = payload_temperature
#     if payload_top_p is not None:
#         payload["top_p"] = payload_top_p

#     # 逻辑判断：如果没有提供 API Key，则尝试通过代理服务器（如 Coursera/DLAI 代理）调用
#     if (not together_api_key) and ('TOGETHER_API_KEY' not in os.environ):
#         url = os.path.join(get_proxy_url(), 'v1/chat/completions')
#         # 使用 requests 发送 POST 请求，verify=False 用于跳过某些环境下的 SSL 验证
#         response = requests.post(url, json = payload, verify=False)
#         if not response.ok:
#             raise Exception(f"调用 LLM 时出错: {response.text}")
#         try:
#             json_dict = json.loads(response.text)
#         except Exception as e:
#             raise Exception(f"无法解析 API 返回值。异常: {e}")
#     else:
#         # 如果存在 API Key，则使用 Together 官方 SDK 调用
#         if together_api_key is None:
#             together_api_key = os.environ['TOGETHER_API_KEY']
#         client = Together(api_key =  together_api_key)
#         # 调用 SDK 并将结果转为字典格式
#         json_dict = client.chat.completions.create(**payload).model_dump()
#         # 统一处理返回结果中角色名称的大小写
#         json_dict['choices'][-1]['message']['role'] = json_dict['choices'][-1]['message']['role'].name.lower()
    
#     try:
#         # 提取模型生成的角色和具体内容
#         output_dict = {
#             'role': json_dict['choices'][-1]['message']['role'], 
#             'content': json_dict['choices'][-1]['message']['content']
#         }
#     except Exception as e:
#         raise Exception(f"提取输出内容失败，请重试。错误: {e}")
#     return output_dict

# def generate_with_multiple_input(messages: List[Dict],
#                                top_p: float = None,
#                                temperature: float = None,
#                                max_tokens: int = 500,
#                                model: str ="Qwen/Qwen3.5-9B",
#                                 together_api_key = None,
#                                 **kwargs):
#     """封装多轮对话输入请求（传入整个消息历史列表）。逻辑与单次输入类似。"""
    
#     payload_top_p = top_p if top_p is not None else None
#     payload_temperature = temperature if temperature is not None else None

#     payload = {
#         "model": model,
#         "messages": messages, # 这里传入的是完整的对话历史列表
#         "max_tokens": max_tokens,
#         "reasoning": {"enabled": False},
#         **kwargs
#     }
#     if payload_temperature is not None:
#         payload["temperature"] = payload_temperature
#     if payload_top_p is not None:
#         payload["top_p"] = payload_top_p

#     # 代理与 SDK 的选择逻辑与上述函数一致
#     if (not together_api_key) and ('TOGETHER_API_KEY' not in os.environ):
#         url = os.path.join(get_proxy_url(), 'v1/chat/completions')
#         response = requests.post(url, json = payload, verify=False)
#         if not response.ok:
#             raise Exception(f"调用 LLM 时出错: {response.text}")
#         try:
#             json_dict = json.loads(response.text)
#         except Exception as e:
#             raise Exception(f"解析失败。异常: {e}\n响应内容: {response.text}")
#     else:
#         if together_api_key is None:
#             together_api_key = os.environ['TOGETHER_API_KEY']
#         client = Together(api_key =  together_api_key)
#         json_dict = client.chat.completions.create(**payload).model_dump()
#         json_dict['choices'][-1]['message']['role'] = json_dict['choices'][-1]['message']['role'].name.lower()
    
#     try:
#         output_dict = {
#             'role': json_dict['choices'][-1]['message']['role'], 
#             'content': json_dict['choices'][-1]['message']['content']
#         }
#     except Exception as e:
#         raise Exception(f"提取输出内容失败。错误: {e}")
#     return output_dict

# def call_llm_with_context(prompt: str, context: list,  role: str = 'user', **kwargs):
#     """
#     核心业务逻辑：通过维护 context 列表来实现有记忆的对话（多轮对话）。

#     参数：
#         prompt: 用户当前输入。
#         context: 存储对话历史的列表，函数会自动更新它。
#     """

#     # 步骤 1：将用户当前的问题打包成字典，并追加到对话历史中
#     context.append({'role': role, 'content': prompt})

#     # 步骤 2：调用多轮对话函数，获取模型的回答
#     response = generate_with_multiple_input(context, **kwargs)

#     # 步骤 3：将模型生成的回答也追加到对话历史中，以便下一次调用时包含此上下文
#     context.append(response)

#     return response