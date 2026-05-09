import os                                          # 导入 os 模块，用于访问环境变量
import requests                                    # 导入 requests 模块，用于发送 HTTP 请求
import json                                        # 导入 json 模块，用于处理 JSON 数据
from together import Together                      # 导入 Together 客户端库.  AI 模型调用库
from typing import List, Dict

def generate_with_single_input(prompt: str,                          # LLM的输入提示词 (str)
                             role: str = 'user',                      # 消息的角色，默认为'user' (用户)
                             top_p: float = None,                     # 采样参数 top_p (float)，控制随机性
                             temperature: float = None,               # 采样温度 (float)，控制创造性
                             max_tokens: int = 500,                   # 响应生成的最大词元数 (int)
                             model: str ="meta-llama/Llama-3.2-3B-Instruct-Turbo", # 使用的模型名称 (str)
                             together_api_key = None,                # 可选的 Together.ai API 密钥 (str)
                             **kwargs):                              # 接受其他可选参数
    """
    负责向 LLM (通过 Together.ai 或代理) 发送单个输入提示词并获取响应。
    此函数处理 Coursera 环境下的代理调用和本地环境下的 Together.ai 直# 导入 Together 客户端库
    """
    # 如果 top_p 未指定，则设置为 'none' (字符串，表示不使用该参数或使用默认值)
    if top_p is None:
        top_p = 'none'
    # 如果 temperature 未指定，则设置为 'none' (字符串，表示不使用该参数或使用默认值)
    if temperature is None:
        temperature = 'none'

    # 构建发送给 API 的请求负载 (Payload) 字典
    payload = {
                "model": model,
                "messages": [{'role': role, 'content': prompt}], # 将单个提示词格式化为消息列表
                "top_p": top_p,
                "temperature": temperature,
                "max_tokens": max_tokens,
                **kwargs                                         # 包含所有额外的参数
                        }
    
    # 判断是使用 Coursera 代理还是 Together.ai 直接调用
    # 逻辑：如果未提供 together_api_key 且环境变量中不存在 'TOGETHER_API_KEY'
    if (not together_api_key) and ('TOGETHER_API_KEY' not in os.environ):
        # --- 使用 Coursera 代理服务器进行调用 ---
        # 构造代理服务器的 URL
        url = os.path.join('https://proxy.dlai.link/coursera_proxy/together', 'v1/chat/completions')    
        # 发送 POST 请求到代理服务器，携带 JSON 负载
        response = requests.post(url, json = payload, verify=False)
        
        # 检查响应状态码，如果不成功则抛出异常
        if not response.ok:
            raise Exception(f"Error while calling LLM: f{response.text}")
        
        # 尝试解析 JSON 响应
        try:
            json_dict = json.loads(response.text)
        except Exception as e:
            # 解析失败则抛出异常
            raise Exception(f"Failed to get correct output from LLM call.\nException: {e}\nResponse: {response.text}")
    else:
        # --- 使用 Together.ai 客户端直接调用 ---
        # 如果 together_api_key 为 None (但环境变量中存在)，则从环境变量获取
        if together_api_key is None:
            together_api_key = os.environ['TOGETHER_API_KEY']
            
        # 使用 API 密钥初始化 Together 客户端
        client = Together(api_key =  together_api_key)
        
        # 使用客户端调用 chat completions API，并将结果转换为字典
        json_dict = client.chat.completions.create(**payload).model_dump()
        
        # LlamaIndex 客户端返回的角色可能是枚举类型，需要将其转换为小写字符串，以保持与代理返回格式一致
        json_dict['choices'][-1]['message']['role'] = json_dict['choices'][-1]['message']['role'].name.lower()
        
    # 从最终的 JSON 响应字典中提取所需的结果
    try:
        # 提取最后一个 'choice' 中的 'role' 和 'content'
        output_dict = {'role': json_dict['choices'][-1]['message']['role'], 'content': json_dict['choices'][-1]['message']['content']}
    except Exception as e:
        # 提取失败则抛出异常
        raise Exception(f"Failed to get correct output dict. Please")

def generate_with_multiple_input(messages: List[Dict],              # 包含对话历史的**消息列表** (List[Dict])
                               top_p: float = None,                 # 采样参数 top_p (float)，控制随机性
                               temperature: float = None,           # 采样温度 (float)，控制创造性
                               max_tokens: int = 500,               # 响应生成的最大词元数 (int)
                               model: str ="meta-llama/Llama-3.2-3B-Instruct-Turbo", # 使用的模型名称 (str)
                               together_api_key = None,            # 可选的 Together.ai API 密钥 (str)
                               **kwargs):                          # 接受其他可选参数
    """
    负责向 LLM (通过 Together.ai 或代理) 发送包含**多轮对话历史**的消息列表并获取响应。
    此函数处理 Coursera 环境下的代理调用和本地环境下的 Together.ai 直接调用Together 客户端库
    """
    # 注意：在这个函数中，top_p 和 temperature 的 None 值**没有**被转换为 'none' 字符串。
    #      如果调用需要这些参数，应确保它们符合 API 要求或在调用前被处理。
    
    # 构建发送给 API 的请求负载 (Payload) 字典
    payload = {
        "model": model,
        "messages": messages,                      # 直接使用传入的消息列表 (messages)，用于维护对话历史
        "top_p": top_p,
        "temperature": temperature,
        "max_tokens": max_tokens,
        **kwargs                                   # 包含所有额外的参数
                }
    
    # 判断是使用 Coursera 代理服务器还是 Together.ai 客户端进行直接调用
    # 逻辑：如果未提供 together_api_key 且环境变量中不存在 'TOGETHER_API_KEY'
    if (not together_api_key) and ('TOGETHER_API_KEY' not in os.environ):
        # --- 使用 Coursera 代理服务器进行调用 ---
        # 构造代理服务器的 URL
        url = os.path.join('https://proxy.dlai.link/coursera_proxy/together', 'v1/chat/completions')    
        # 发送 POST 请求到代理服务器，携带 JSON 负载
        response = requests.post(url, json = payload, verify=False)
        
        # 检查响应状态码，如果不成功则抛出异常
        if not response.ok:
            raise Exception(f"Error while calling LLM: f{response.text}")
            
        # 尝试解析 JSON 响应
        try:
            json_dict = json.loads(response.text)
        except Exception as e:
            # 解析失败则抛出异常
            raise Exception(f"Failed to get correct output from LLM call.\nException: {e}\nResponse: {response.text}")
    else:
        # --- 使用 Together.ai 客户端直接调用 ---
        # 如果 together_api_key 为 None (但环境变量中存在)，则从环境变量获取
        if together_api_key is None:
            together_api_key = os.environ['TOGETHER_API_KEY']
            
        # 使用 API 密钥初始化 Together 客户端
        client = Together(api_key = together_api_key)
        
        # 使用客户端调用 chat completions API，并将结果转换为字典
        json_dict = client.chat.completions.create(**payload).model_dump()
        
        # LlamaIndex 客户端返回的角色可能是枚举类型，需要将其转换为小写字符串，以保持与代理返回格式一致
        json_dict['choices'][-1]['message']['role'] = json_dict['choices'][-1]['message']['role'].name.lower()
        
    # 从最终的 JSON 响应字典中提取所需的结果
    try:
        # 提取最后一个 'choice' 中的 'role' 和 'content'
        output_dict = {'role': json_dict['choices'][-1]['message']['role'], 'content': json_dict['choices'][-1]['message']['content']}
    except Exception as e:
        # 提取失败则抛出异常
        raise Exception(f"Failed to get correct output dict. Please try again. Error'content'")
    except Exception as e:
        raise Exception(f"Failed to get correct output dict. Please try again. Error: {e}")
    return output_dict
