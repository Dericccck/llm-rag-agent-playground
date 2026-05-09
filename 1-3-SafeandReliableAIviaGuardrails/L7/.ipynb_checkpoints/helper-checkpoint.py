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
    def __init__(self, client=None, guard=None, system_message=None):
        """
        A widget for handling chat interactions.

        Parameters
        ----------
        client : object
            The OpenAI client object to use for generating responses.
        system_message : str, optional
            An optional system message to initialize the chat with.
        """
        self.chat_logs = []
        self.messages = []
        if system_message:
            self.messages.append({"role": "system", "content": system_message})
        # self.main_output = widgets.Output()

        self.text_input = widgets.Textarea(
            value="",
            placeholder="Type something and press Enter",
            disabled=False,
            continuous_update=False,
            layout=widgets.Layout(width="400px", height="75px"),
            form="chatform",
        )

        self.text_input.observe(self.handle_submit, names="value")
        self.submit_button = widgets.Button(
            form="chatform",
            icon="paper-plane",
            button_style="primary",
            type="submit",
            layout=widgets.Layout(width="40px", margin_y="auto"),
        )

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

        self.chat_box = widgets.VBox(
            [], layout=widgets.Layout(max_height="300px", overflow_y="auto")
        )
        self.main_container = widgets.VBox(
            [self.chat_box, action_bar],
            layout=widgets.Layout(width="505px", justify_content="center"),
        )
        self._client = client
        self._guard = guard

    @property
    def client(self):
        return self._client

    @client.setter
    def client(self, value):
        self._client = value

    def reset(self):
        self.chat_logs = []
        self.messages = []
        self.chat_box.children = self.chat_logs

    def create_msg_widget(self, type, content, is_error=False):
        """Utility function to create a message widget based on the type"""
        common_style = """
            padding: 8px;
            margin: 2px 0;
            border-radius: 5px;
            width: fit-content;
            max-width: 70%;
            word-wrap: break-word;
            white-space: pre-wrap;
            overflow-wrap: break-word;
            line-height: 1.4;
        """

        if type == "user":
            style = (
                common_style
                + "justify-content: flex-end; background-color: #f0f0f0; float: right;"
            )
        elif type == "bot":
            style = common_style + "justify-content: flex-start;"
        else:
            raise ValueError("Type must be either 'user' or 'bot'")

        html_content = f'<div style="{style}">{content}</div>'
        return widgets.HTML(html_content)

    def update_chat_box(self, user_msg, bot_msg, error=False):
        user_widget = self.create_msg_widget("user", user_msg)
        bot_widget = self.create_msg_widget("bot", bot_msg, error)
        self.chat_logs.extend([user_widget, bot_widget])
        self.chat_box.children = self.chat_logs

    def show_loading(self, message):
        user_widget = self.create_msg_widget("user", message)
        loading_widget = self.create_msg_widget("bot", "Thinking...")
        loading_chat_logs = self.chat_logs.copy()
        loading_chat_logs.extend([user_widget, loading_widget])
        self.chat_box.children = loading_chat_logs

    def handle_submit(self, change):
        if (
            change["type"] == "change"
            and change["name"] == "value"
            and change["new"] != ""
        ):
            user_msg = change["new"]
            self.show_loading(user_msg)
            change["owner"].value = ""

            # self.remove_loading()
            query_messages = self.messages.copy()
            query_messages.append({"role": "user", "content": user_msg})

            # get the bot response
            error = False
            try:
                bot_message = self.bot_response_generator(query_messages)

                # write the user msg and bot response back in to message history
                self.messages.append({"role": "user", "content": user_msg})
                self.messages.append({"role": "assistant", "content": bot_message})

            except Exception as e:
                print(e)

                # we don't write here cuz it's errors
                bot_message = str(e)
                error = True

            # Clear the input after submission
            self.update_chat_box(user_msg, bot_message, error)

    def display(self):
        display(self.main_container)

    def bot_response_generator(self, message_history):
        if self.client:
            response = self.client.chat.completions.create(
                model="qwen-max",
                messages=message_history,
                seed=42,
                temperature=0.0,
            )
            bot_msg = response.choices[0].message.content
            return bot_msg
        else:
            settings.use_server = True
            response = self._guard(
                # base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                # model="qwen-plus",
                api_key=os.getenv("DASHSCOPE_API_KEY"),
                api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
                model="dashscope/qwen-max",
                messages=message_history,
                metadata={"sources": sources, "chunk_strategy": "sentence"},
            )

            settings.use_server = False
            return response.validated_output


def chunk_markdown_files(directory):
    chunks = []

    for filename in os.listdir(directory):
        if filename.endswith(".md"):
            file_path = os.path.join(directory, filename)
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()

            # Split content into lines
            lines = content.split("\n")

            title = os.path.splitext(filename)[0]
            current_h1 = ""
            current_h2 = ""
            current_content = []

            for line in lines:
                if line.startswith("# "):
                    # New h1 header
                    if current_content:
                        chunks.append(
                            format_chunk(title, current_h1, current_h2, current_content)
                        )
                    current_h1 = line[2:].strip()
                    current_h2 = ""
                    current_content = []
                elif line.startswith("## "):
                    # New h2 header
                    if current_content:
                        chunks.append(
                            format_chunk(title, current_h1, current_h2, current_content)
                        )
                    current_h2 = line[3:].strip()
                    current_content = []
                else:
                    # Content (including h3 headers and list items)
                    current_content.append(line)

            # Add the last chunk
            if current_content:
                chunks.append(
                    format_chunk(title, current_h1, current_h2, current_content)
                )

    return chunks


def format_chunk(title, h1, h2, content):
    section_info = f"{h1}/{h2}" if h2 else h1
    content_text = "\n".join(content).strip()
    return f"Title: {title}\nSection: {section_info}\n{content_text}"


class SimpleVectorDB:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.embeddings = []
        self.strings = []

    def add_strings(self, strings: List[str]):
        new_embeddings = self.model.encode(strings)
        self.embeddings.extend(new_embeddings)
        self.strings.extend(strings)

    def query(
        self, query_string: str, k: int, threshold: float
    ) -> List[Tuple[str, float]]:
        query_embedding = self.model.encode([query_string])[0]

        if not self.embeddings:
            return []

        embeddings_array = np.array(self.embeddings)

        # Calculate cosine similarities
        similarities = np.dot(embeddings_array, query_embedding) / (
            np.linalg.norm(embeddings_array, axis=1) * np.linalg.norm(query_embedding)
        )

        # Convert similarities to distances (1 - similarity)
        distances = 1 - similarities
        # distances = similarities

        # Sort indices by distance
        sorted_indices = np.argsort(distances)

        results = []
        for idx in sorted_indices:
            if distances[idx] < threshold and len(results) < k:
                results.append((self.strings[idx], float(distances[idx])))
            else:
                break

        results.reverse()

        return results

    @classmethod
    def from_files(cls, directory: str):
        chunks = chunk_markdown_files(directory)
        db = cls()
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
            print(f"query_messages={query_messages}")
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
                    print(f"e={str(e)}")
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

    def retrieve(self, user_msg, k=1, threshold=0.9):
        retrieval = self.vector_db.query(user_msg, k=k, threshold=threshold)
        retrieved_ctx = ""
        for idx, (ctx, _) in enumerate(retrieval):
            retrieved_ctx += f"# Context {idx + 1}:\n{ctx}\n\n"
        # return retrieval
        return retrieved_ctx

    def retrieval_augmentation(self, user_msg, retrieval):
        augmented_user_msg = f"""\n
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
