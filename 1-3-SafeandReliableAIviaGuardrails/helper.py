import os
import sys
from typing import List, Tuple
from openai import OpenAI,BadRequestError

import ipywidgets as widgets
import numpy as np
from dotenv import find_dotenv, load_dotenv
from guardrails import Guard, settings
from guardrails.errors import ValidationError
from IPython.display import display
from sentence_transformers import SentenceTransformer
from huggingface_hub import HfApi, snapshot_download, list_repo_files
import shutil
import os
# these expect to find a .env file at the directory above the lesson.
# the format for that file is (without the comment)#API_KEYNAME=AStringThatIsTheLongAPIKeyFromSomeService
import litellm
litellm.set_verbose = True 

def load_env():
    _ = load_dotenv(find_dotenv())

def get_qwen_client():
    load_env()
    client = OpenAI(
        api_key=os.getenv("DASHSCOPE_API_KEY"),  # 从环境变量读取
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )
    return client
    
def get_openai_api_key():
    load_env()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    return openai_api_key


def get_guardrails_api_key():
    load_env()
    guardrails_api_key = os.getenv("GUARDRAILS_API_KEY")
    return guardrails_api_key


def download_model(model_name, force_redownload=False):
    """源地址下载模型"""
    if force_redownload:
        cache_path = os.path.join(os.path.expanduser("~"), ".cache", "huggingface", "hub")
        model_cache_dir = os.path.join(cache_path, f"models--{model_name.replace('/', '--')}")
        
        if os.path.exists(model_cache_dir):
            print(f"🗑️ 清理缓存目录: {model_cache_dir}")
            shutil.rmtree(model_cache_dir)

    # 重新下载
    print(f"⬇️ 开始下载模型: {model_name}")
    
    model_path = snapshot_download(
        repo_id=model_name,
        local_dir_use_symlinks=False,
        force_download=force_redownload,  # 强制重新下载
        resume_download=not force_redownload  # 如果不是强制下载，支持断点续传
        # cache_dir 不传，使用默认目录
    )
    print(f"✅ 下载完成: {model_path}")
    return model_path
    
def download_model_with_mirror(model_name, force_redownload=False):
    """使用镜像下载模型,镜像地址不稳定"""
    if force_redownload:
        cache_path = os.path.join(os.path.expanduser("~"), ".cache", "huggingface", "hub")
        model_cache_dir = os.path.join(cache_path, f"models--{model_name.replace('/', '--')}")
        
        if os.path.exists(model_cache_dir):
            print(f"🗑️ 清理缓存目录: {model_cache_dir}")
            shutil.rmtree(model_cache_dir)

    # 重新下载
    print(f"⬇️ 开始下载模型: {model_name}")
    
    model_path = snapshot_download(
        repo_id=model_name,
        endpoint="https://hf-mirror.com",  # 直接在这里指定镜像
        local_dir_use_symlinks=False,
        # force_download=force_redownload,  # 强制重新下载
        resume_download=not force_redownload  # 如果不是强制下载，支持断点续传
        # cache_dir 不传，使用默认目录
    )
    print(f"✅ 下载完成: {model_path}")
    return model_path

def check_model_with_mirror(model_name):
    """使用镜像检查模型是否存在"""
    try:
        # 尝试获取模型信息
        model_info = api.model_info(model_name)
        print("✅ 模型存在！")
        print(f"模型ID: {model_info.modelId}")
        
        # 使用同样的API实例或单独调用list_repo_files
        files = api.list_repo_files(model_name)
        print(f"仓库文件: {list(files)}")
        
    except Exception as e:
        print(f"❌ 错误: {e}")

class ChatWidget:
    """
    基础聊天部件类，用于处理 IPywidgets 界面元素和 LLM 交互的基础逻辑。
    它维护对话历史，处理用户输入，并调用 LLM API 获取回复。
    """
    # 构造函数
    def __init__(self, client=None, guard=None, system_message=None):
        """
        初始化聊天部件。

        参数:
        ----------
        client : object
            用于生成 LLM 回复的客户端对象（如 Together/OpenAI 客户端）。
        guard : object
            Guard (卫兵) 对象或函数，用于处理服务器端/安全增强的 LLM 调用。
        system_message : str, optional
            一个可选的系统消息，用于初始化聊天上下文，设定 LLM 的角色或指令。
        """
        import ipywidgets as widgets # 假设 ipywidgets 已导入
        from IPython.display import display # 假设 display 已导入
        import os # 用于 bot_response_generator 中访问环境变量
        
        self.chat_logs = []  # 存储用于显示的聊天消息部件 (widgets) 列表
        self.messages = []   # 存储用于 LLM API 调用的消息历史列表（字典格式：role/content）
        
        # 如果存在系统消息，则将其作为助手（Assistant）的身份加入到 LLM 消息历史中
        if system_message:
            self.messages.append({"role": "assistant", "content": system_message})
            
        # ------------------- 界面元素初始化：输入框 -------------------
        self.text_input = widgets.Textarea(
            value="",
            placeholder="Type something and press Enter", # 提示文本
            disabled=False,
            continuous_update=False, # 仅在提交或失去焦点时更新值，提高性能
            layout=widgets.Layout(width="400px", height="75px"),
            form="chatform", # 与提交按钮关联的表单名称
        )

        # 绑定事件：当输入框的值 ('value') 改变时，调用 self.handle_submit 方法
        self.text_input.observe(self.handle_submit, names="value")
        
        # ------------------- 界面元素初始化：提交按钮 -------------------
        self.submit_button = widgets.Button(
            form="chatform",
            icon="paper-plane", # 使用纸飞机图标
            button_style="primary", # 设置为主要按钮样式（通常是蓝色）
            type="submit", # 提交类型，与输入框的 form 属性配合工作
            layout=widgets.Layout(width="40px", margin_y="auto"),
        )

        # ------------------- 界面元素初始化：操作栏 (输入框 + 按钮) -------------------
        action_bar = widgets.HBox(
            [
                self.text_input,
                widgets.VBox(
                    [self.submit_button],
                    layout=widgets.Layout(justify_content="center", margin_y="auto"),
                ),
            ],
            layout=widgets.Layout(
                justify_content="center", width="480px", padding_y="10px"
            ),
        )

        # ------------------- 界面元素初始化：聊天记录显示区 -------------------
        self.chat_box = widgets.VBox(
            [], # 初始聊天记录为空
            layout=widgets.Layout(max_height="300px", overflow_y="auto") # 设置最大高度并启用垂直滚动条
        )
        
        # ------------------- 界面元素初始化：主容器 -------------------
        self.main_container = widgets.VBox(
            [self.chat_box, action_bar], # 垂直堆叠聊天记录和操作栏
            layout=widgets.Layout(width="505px", justify_content="center"),
        )
        
        # 存储 LLM 客户端和 Guard 实例（使用下划线前缀表示内部变量）
        self._client = client
        self._guard = guard

    # ------------------- 属性 (Property)：client -------------------
    @property
    def client(self):
        """获取 LLM 客户端对象。"""
        return self._client

    @client.setter
    def client(self, value):
        """设置 LLM 客户端对象。"""
        self._client = value

    # ------------------- 方法：重置 -------------------
    def reset(self):
        """清空聊天日志、消息历史，并更新聊天界面的显示。"""
        self.chat_logs = []
        self.messages = []
        self.chat_box.children = self.chat_logs

    # ------------------- 方法：创建消息部件 -------------------
    def create_msg_widget(self, type, content, is_error=False):
        """
        根据类型 ('user' 或 'bot') 创建带有基本 CSS 样式的 HTML 消息部件。
        """
        # ... (CSS 样式代码省略，但其目的是定义消息气泡的样式) ...
        # (略去具体样式定义)
        common_style = "..."

        if type == "user":
            # 用户消息：右对齐，灰色背景
            style = common_style + "justify-content: flex-end; background-color: #f0f0f0; float: right;"
        elif type == "bot":
            # 助手消息：左对齐
            style = common_style + "justify-content: flex-start;"
            # 注意：is_error 参数未被使用，但可用于未来添加错误高亮样式
        else:
            raise ValueError("Type must be either 'user' or 'bot'")

        html_content = f'<div style="{style}">{content}</div>'
        return widgets.HTML(html_content)

    # ------------------- 方法：更新聊天框 -------------------
    def update_chat_box(self, user_msg, bot_msg, error=False):
        """将用户消息和助手回复添加到 chat_logs 并更新 chat_box 的显示。"""
        user_widget = self.create_msg_widget("user", user_msg)
        bot_widget = self.create_msg_widget("bot", bot_msg, error)
        self.chat_logs.extend([user_widget, bot_widget])
        self.chat_box.children = self.chat_logs # 替换显示内容，触发界面更新

    # ------------------- 方法：显示加载状态 -------------------
    def show_loading(self, message):
        """在等待 LLM 响应时，显示用户消息和 'Thinking...' 状态。"""
        user_widget = self.create_msg_widget("user", message)
        loading_widget = self.create_msg_widget("bot", "Thinking...")
        loading_chat_logs = self.chat_logs.copy() # 复制现有消息
        loading_chat_logs.extend([user_widget, loading_widget]) # 添加新消息和加载提示
        self.chat_box.children = loading_chat_logs # 显示加载状态

    # ------------------- 方法：处理提交 (核心逻辑) -------------------
    def handle_submit(self, change):
        """
        处理用户在文本输入框中提交消息时的回调函数。
        """
        # 检查是否为有效的 'value' 变化事件且新值不为空
        if (
            change["type"] == "change"
            and change["name"] == "value"
            and change["new"] != ""

# ----------------------------------------------------------------------
# 辅助函数：将 Markdown 文件按标题分块 (Chunking)
# ----------------------------------------------------------------------
def chunk_markdown_files(directory):
    """
    遍历指定目录下的所有 Markdown (.md) 文件，并根据一级标题 (#) 和二级标题 (##)
    将文件内容分割成结构化的文本块 (chunks)。
    
    参数:
        directory (str): 包含 Markdown 文件的目录路径。
        
    返回:
        list: 包含所有格式化文本块的列表。
    """
    import os
    
    chunks = []  # 用于存储所有生成的文本块

    # 遍历目录中的所有文件
    for filename in os.listdir(directory):
        # 仅处理以 .md 结尾的文件
        if filename.endswith(".md"):
            file_path = os.path.join(directory, filename)
            # 以 UTF-8 编码读取文件内容
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()

            # 将文件内容按行分割
            lines = content.split("\n")

            # 提取文件名作为主标题 (Title)
            title = os.path.splitext(filename)[0]
            current_h1 = ""       # 当前一级标题内容
            current_h2 = ""       # 当前二级标题内容
            current_content = []  # 当前分块的内容行

            # 逐行遍历文件内容
            for line in lines:
                if line.startswith("# "):
                    # 遇到新的一级标题 (# )
                    if current_content:
                        # 如果当前内容不为空，则将前一个分块保存到 chunks 列表中
                        chunks.append(
                            format_chunk(title, current_h1, current_h2, current_content)
                        )
                    # 更新一级标题，并重置二级标题和内容
                    current_h1 = line[2:].strip()
                    current_h2 = ""
                    current_content = []
                elif line.startswith("## "):
                    # 遇到新的二级标题 (## )
                    if current_content:
                        # 如果当前内容不为空，则将前一个分块保存到 chunks 列表中
                        chunks.append(
                            format_chunk(title, current_h1, current_h2, current_content)
                        )
                    # 更新二级标题，并重置内容
                    current_h2 = line[3:].strip()
                    current_content = []
                else:
                    # 普通内容行 (包括三级标题和列表项等)
                    current_content.append(line)

            # 文件遍历结束后，添加最后一个分块（避免遗漏文件末尾的内容）
            if current_content:
                chunks.append(
                    format_chunk(title, current_h1, current_h2, current_content)
                )

    return chunks


def format_chunk(title, h1, h2, content):
    """
    将分块信息和内容组合成一个统一的、结构化的字符串格式。
    
    参数:
        title (str): 文件标题。
        h1 (str): 当前一级标题。
        h2 (str): 当前二级标题。
        content (list): 包含分块内容的行列表。
        
    返回:
        str: 格式化的文本块字符串。
    """
    # 组合章节信息：如果存在 h2 则为 "h1/h2"，否则只用 h1
    section_info = f"{h1}/{h2}" if h2 else h1
    # 将内容行用换行符连接起来，并移除首尾空白
    content_text = "\n".join(content).strip()
    # 返回最终的格式化字符串，便于 LLM 理解其来源和结构
    return f"Title: {title}\nSection: {section_info}\n{content_text}"

# ----------------------------------------------------------------------
# 核心类：简易向量数据库 (SimpleVectorDB)
# ----------------------------------------------------------------------
class SimpleVectorDB:
    """
    一个简单的基于内存的向量数据库，使用 SentenceTransformer 进行嵌入和余弦相似度查询。
    """
    # 构造函数
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        初始化向量数据库，加载 SentenceTransformer 模型并初始化嵌入和字符串列表。
        """
        # 导入必需的库
        from sentence_transformers import SentenceTransformer
        
        self.model = SentenceTransformer(model_name) # 加载嵌入模型
        self.embeddings = []                        # 存储嵌入向量的列表
        self.strings = []                           # 存储原始文本块的列表

    def add_strings(self, strings: List[str]):
        """
        将一批文本字符串添加到数据库中，并计算它们的嵌入向量。
        
        参数:
            strings (List[str]): 要添加的文本块列表。
        """
        new_embeddings = self.model.encode(strings) # 计算新文本块的嵌入向量
        self.embeddings.extend(new_embeddings)      # 将新嵌入向量添加到总列表
        self.strings.extend(strings)                # 将新文本块添加到总列表

    def query(
        self, query_string: str, k: int, threshold: float
    ) -> List[Tuple[str, float]]:
        """
        对数据库执行相似度查询，返回 k 个最相似且距离小于阈值的文本块。
        
        参数:
            query_string (str): 用户的查询字符串。
            k (int): 返回的最相似结果的最大数量。
            threshold (float): 距离阈值（小于此值才被视为相关）。
            
        返回:
            List[Tuple[str, float]]: 包含 (文本块, 距离) 元组的列表。
        """
        import numpy as np
        from typing import List, Tuple
        
        # 计算查询字符串的嵌入向量
        query_embedding = self.model.encode([query_string])[0]

        # 如果数据库中没有嵌入向量，则直接返回空列表
        if not self.embeddings:
            return []

        embeddings_array = np.array(self.embeddings) # 将嵌入列表转换为 NumPy 数组

        # --- 计算余弦相似度 ---
        # 计算所有嵌入向量与查询向量的点积
        # 接着除以各自的范数（L2 模长）的乘积，得到余弦相似度
        similarities = np.dot(embeddings_array, query_embedding) / (
            np.linalg.norm(embeddings_array, axis=1) * np.linalg.norm(query_embedding)
        )

        # 将相似度转换为距离 (1 - similarity)，以便使用 np.argsort 进行从小到大排序
        distances = 1 - similarities
        # distances = similarities # 如果直接使用相似度，则需要 np.argsort(distances)[::-1] 来降序排序

        # 按距离从小到大排序，获取索引
        sorted_indices = np.argsort(distances)

        results = []
        # 遍历排序后的索引
        for idx in sorted_indices:
            # 筛选：距离必须小于阈值 (threshold) 且结果数量未达到 k
            if distances[idx] < threshold and len(results) < k:
                # 添加结果：(原始文本块, 距离)
                results.append((self.strings[idx], float(distances[idx])))
            else:
                # 一旦距离超过阈值或达到 k，停止搜索（因为后续的距离只会更大）
                break
        
        # 将结果列表反转，使其按相似度（距离）从高到低排列
        results.reverse()

        return results

    @classmethod
    def from_files(cls, directory: str):
        """
        类方法：从指定目录下的 Markdown 文件创建并初始化 SimpleVectorDB 实例。
        
        参数:
            directory (str): 包含 Markdown 文件的目录路径。
            
        返回:
            SimpleVectorDB: 初始化完成的向量数据库实例。
        """
        # 1. 调用 chunk_markdown_files 函数获取所有文本块
        chunks = chunk_markdown_files(directory)
        # 2. 创建 SimpleVectorDB 实例
        db = cls()
        # 3. 将所有文本块添加到数据库中（计算嵌入向量）
        db.add_strings(chunks)
        return db


class RAGChatWidget(ChatWidget):
    def __init__(
        self,
        client=None,
        guard=None,
        system_message=None,
        vector_db=None,
        # data_directory="shared_data/",
    ):
        super().__init__(
            client=client, guard=guard, system_message=system_message
        )
        self.vector_db = vector_db
        # self.data_directory = data_directory

        # self.hydrate_vector_db()

    def hydrate_vector_db(self):
        chunks = chunk_markdown_files(self.data_directory)
        self.vector_db.add_strings(chunks)

    # --- 识别客户端的函数 ---
    @staticmethod
    def is_guarded_client(client: OpenAI) -> bool:
        """
        检查客户端的 base_url 是否指向本地的 Guardrails Server。
        """
        # client._base_url 是 httpx.URL 对象。我们检查它的字符串表示
        base_url_str = str(client._base_url) 
        
        # 检查 URL 是否包含 Guardrails Server 的特征字符串
        # 示例: "http://localhost:8000/guards/hallucination_guard/openai/v1/"
        return "/guards/" in base_url_str or "localhost:8000" in base_url_str

    def bot_response_generator(self, message_history, context=None):
        if self.client is not None:
            print(f"client: {self.client}")
        else:
            print("client: (None)")
        
        if self.client:
            is_guarded = RAGChatWidget.is_guarded_client(self.client)
            
            if is_guarded:
                # 模式 A: 连接到 Guardrails Server
                # 构造 extra_args（无论是否 Guarded Client，RAG 上下文的提取逻辑都是一样的）
                if context:
                    sources = [c[0] for c in context]
                    extra_args = {
                        "extra_body": {
                            "metadata": {
                                "sources": sources,
                                "chunk_strategy": "sentence"
                            }
                        }
                    }
                else:
                    extra_args = {}
                
                settings.use_server = True # 确保设置正确
                response = self.client.chat.completions.create(
                    model="dashscope/qwen-max",
                    messages=message_history,
                    seed=42,
                    temperature=0.0,
                    **extra_args # 传递 RAG 上下文给 Guardrails Server
                )
                bot_msg = response.choices[0].message.content
                return bot_msg
                
            else:
                # 模式 B: 标准 LLM 客户端 (无 Guardrails 或仅做生成)
                response = self.client.chat.completions.create(
                    model="qwen-max", 
                    messages=message_history,
                    seed=42,
                    temperature=0.0,
                )
                bot_msg = response.choices[0].message.content
                return bot_msg
            
        # --- 2. 客户端不存在（假设是本地 Guardrails 模式）---
        else:
            # Context is a list of touples, we want to map down to the first value in the tuples
            sources = [c[0] for c in context]
            settings.use_server = False

            # 改成千问模型
            response = self._guard(
                # base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                # model="qwen-plus",
                api_key=os.getenv("DASHSCOPE_API_KEY"),
                api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
                model="dashscope/qwen-max",
                messages=message_history,
                metadata={"sources": sources, "chunk_strategy": "sentence"},
            )

            return response.validated_output

    def handle_submit(self, change):
        if (
            change["type"] == "change"
            and change["name"] == "value"
            and change["new"] != ""
        ):
            # extract message user sent
            user_msg = change["new"]
            self.show_loading(user_msg)
            # Clear the input after submission
            change["owner"].value = ""

            context = self.retrieve(user_msg, k=3)

            # do retrieval, add to message history
            augmented_user_msg = self.retrieval_augmentation(user_msg, context)
            error = False
            query_messages = self.messages.copy()
            query_messages.append({"role": "user", "content": augmented_user_msg})
            # get the bot response
            try:
                bot_message = self.bot_response_generator(
                    query_messages, context=context
                )

                # write the user msg and bot response back in to message history
                self.messages.append({"role": "user", "content": augmented_user_msg})
                self.messages.append({"role": "assistant", "content": bot_message})

            except ValidationError as e:
                # 捕获 ValidatorError，这表明验证失败
                print("Validation failed. Returning fix_value directly.")
                # 从异常对象中提取 fail_result 的详细信息
                # 这里的 e.args[0] 通常包含 fail_result 对象
                bot_message = str(e)
            except BadRequestError as e: 
                print("Guardrails Validation Failed via API.")
                # 尝试从异常体中提取详细信息。如果直接访问 'detail' 失败，
                # 打印完整的错误体或使用异常消息本身。
                try:
                    # 完整的错误信息在 Traceback 的最底部，通常是 str(e) 或 e.message
                    print(str(e))
                    bot_message = "I can't answer this question" 
                except Exception:
                    bot_message = "I can't answer this question"
                
                error = True
            except Exception as e:
                # 打印原始错误信息到控制台，以便调试
                print(f"An error occurred: {type(e).__name__}: {e}")
                
                # 尝试安全地提取错误消息
                try:
                    # 尝试提取 BadRequestError 的详细信息
                    bot_message = e.body['detail']
                except (AttributeError, KeyError):
                    # 如果不是 BadRequestError (比如现在的 TypeError)，则使用标准的错误字符串
                    bot_message = f"An unexpected error occurred: {str(e)}"
                
                error = True
    

            # We show user_msg here instead of the augmented_user_msg to hide the retrieval
            self.update_chat_box(user_msg, bot_message, error)

  # ----------------------------------------------------------------------
    # 辅助方法：检索
    # ----------------------------------------------------------------------
    def retrieve(self, user_msg, k=1, threshold=0.9):
        """
        使用向量数据库查询用户消息，并返回格式化的检索结果。
        
        参数:
            user_msg (str): 用户的查询。
            k (int): 要检索的最佳结果数量。
            threshold (float): 相似度距离阈值。
            
        返回:
            str: 格式化后的检索上下文字符串。
        """
        # 调用 SimpleVectorDB 的 query 方法获取检索结果
        retrieval = self.vector_db.query(user_msg, k=k, threshold=threshold)
        retrieved_ctx = ""
        # 遍历检索结果 (ctx: 文本块, _: 距离/相似度)
        for idx, (ctx, _) in enumerate(retrieval):
            # 将每个检索到的文本块格式化，添加 Context 编号
            retrieved_ctx += f"# Context {idx + 1}:\n{ctx}\n\n"
        # 返回所有格式化上下文的组合字符串
        return retrieved_ctx

    # ----------------------------------------------------------------------
    # 辅助方法：提示词增强
    # ----------------------------------------------------------------------
    def retrieval_augmentation(self, user_msg, retrieval):
        """
        将检索到的上下文和用户消息结合起来，创建一个增强的提示词。
        
        参数:
            user_msg (str): 用户的原始查询。
            retrieval (str): 格式化后的检索上下文。
            
        返回:
            str: 用于发送给 LLM 的增强提示词。
        """
        # 使用 f-string 模板将上下文和用户消息合并
        augmented_user_msg = f"""\n
Use this context to help answer the question:

{retrieval}

User message:
{user_msg}
"""
        return augmented_user_msger_msg = f"""\n
        Use this context to help answer the question:
        
        {retrieval}
        
        User message:
        {user_msg}
        """

        return augmented_user_msg


# Example usage
if __name__ == "__main__":
    directory = "shared_data/"
    chunks = chunk_markdown_files(directory)
    for chunk in chunks:
        print(chunk)
        print("-" * 50)
