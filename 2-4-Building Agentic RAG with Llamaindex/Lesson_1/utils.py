# --- 导入必要的 LlamaIndex 模块 ---
# LlamaIndex 是一个用于连接 LLM 和外部数据的框架。

# 从核心模块导入 SimpleDirectoryReader，用于加载本地文件（如 PDF、TXT 等）。
from llama_index.core import SimpleDirectoryReader
# 导入 SentenceSplitter，用于将长文档分割成适合 LLM 处理的小块（Node）。
from llama_index.core.node_parser import SentenceSplitter
# 导入 Settings，用于全局配置，虽然在这个函数中没有直接使用，但通常用于设置全局的 LLM/Embedding 模型。
from llama_index.core import Settings
# 导入 OpenAI 的 LLM 封装。
from llama_index.llms.openai import OpenAI
# 导入 OpenAI 的 Embedding 封装，用于将文本转换为向量。
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai_like import OpenAILike
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
# 导入 SummaryIndex (摘要索引) 和 VectorStoreIndex (向量存储索引)，这是两种不同的数据结构。
from llama_index.core import SummaryIndex, VectorStoreIndex
# 导入 QueryEngineTool，用于将查询引擎包装成可供路由引擎选择的“工具”。
from llama_index.core.tools import QueryEngineTool
# 导入 RouterQueryEngine，这是本代码的核心，用于智能选择要使用的工具。
from llama_index.core.query_engine.router_query_engine import RouterQueryEngine
# 导入 LLMSingleSelector，这是一个选择器，它会使用 LLM 来决定在多个工具中选择哪一个。
from llama_index.core.selectors import LLMSingleSelector
from helper import get_openai_api_key, get_dashscope_api_key
import os


def get_router_query_engine(file_path: str, llm = None, embed_model = None):
    """
    创建一个路由查询引擎。
    它会根据用户问题，智能地在“摘要总结”和“精确检索”两种模式中选择一种。
    
    Args:
        file_path (str): 要加载的文档文件路径。
        llm (Optional): 可选的 LLM 实例。
        embed_model (Optional): 可选的 Embedding 模型实例。
        
    Returns:
        RouterQueryEngine: 路由查询引擎实例。
    """
    # --- 1. 初始化模型 ---
    # 如果没有传入 LLM 实例，则创建一个默认的 OpenAI LLM。
    # 它是 Agent 做出决策（路由选择）和生成答案的核心。
    # llm = llm or OpenAILike(
    #     api_key=get_openai_api_key(),
    #     api_base="https://models.inference.ai.azure.com/",
    #     model="gpt-4o-mini",
    #     temperature=0.1,
    #     context_window=128000,
    #     is_chat_model=True,
    #     is_function_calling_model=False,
    # )
    llm = OpenAILike(
    api_key=get_dashscope_api_key(),
    api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
    model="qwen-max",
    temperature=0.1,
    context_window=128000,
    is_chat_model=True,
    is_function_calling_model=True,
)
    # 如果没有传入 Embedding 模型，则创建一个默认的 OpenAI Embedding 模型。
    # Embedding 模型用于将文本转化为数字向量，是 VectorStoreIndex 的核心。
    # embed_model = embed_model or OpenAIEmbedding(model="text-embedding-ada-002")
    model_real_path = os.path.expanduser(
        "~/Desktop/AIAgent/models/models--BAAI--bge-small-en-v1.5/snapshots/5c38ec7c405ec4b44b94cc5a9bb96e735b38267a"
    )
    embed_model = embed_model or HuggingFaceEmbedding(
        model_name=model_real_path,
        # 默认情况下，LlamaIndex 会尝试自动下载和加载模型
        device="cpu",  # 如果您没有GPU，可以使用"cpu"
        # 连不了外网下载模型到本地的记得这个标志要设置为True，不然虽然本地有了还会掉huggingface获取包信息检验
        local_files_only=True,
    )
    # --- 2. 加载文档 ---
    # 使用 SimpleDirectoryReader 从指定文件路径加载数据。
    # 结果是一个包含原始文档内容的列表。
    documents = SimpleDirectoryReader(input_files=[file_path]).load_data()
    
    # --- 3. 分割文档（分块） ---
    # 初始化句子分割器，设置块大小为 1024 个 token/字符。
    # 将文档分割成小块（Node），便于 LLM 在处理时保持上下文，这是 RAG 的关键步骤。
    splitter = SentenceSplitter(chunk_size=1024)
    nodes = splitter.get_nodes_from_documents(documents)
    
    # --- 4. 创建两种不同用途的索引 ---
    
    # 摘要索引 (SummaryIndex):
    # 简单地将所有节点（文档块）按顺序连接起来。
    # 适合用来生成整个文档的全局摘要。
    summary_index = SummaryIndex(nodes)
    
    # 向量存储索引 (VectorStoreIndex):
    # 将所有节点（文档块）转换为向量，并存储起来。
    # 适合用来进行语义搜索，快速找到与查询最相关的特定片段。
    vector_index = VectorStoreIndex(nodes, embed_model=embed_model)
    
    # --- 5. 为每种索引创建查询引擎 ---
    
    # 摘要查询引擎:
    # 设置 response_mode="tree_summarize"，意味着它会递归地总结所有文档块，生成一份完整的摘要。
    summary_query_engine = summary_index.as_query_engine(
        response_mode="tree_summarize",
        use_async=True, # 启用异步处理，提高性能。
        llm=llm
    )
    
    # 向量查询引擎:
    # 默认模式下，它会搜索最相似的向量（文档片段），并将这些片段提供给 LLM 来生成答案。
    vector_query_engine = vector_index.as_query_engine(llm=llm)
    
    # --- 6. 将查询引擎包装成工具 ---
    
    # 摘要工具 (summary_tool):
    # 将摘要查询引擎包装起来，并给它一个清晰的描述。
    # 描述是关键！LLM 将根据这个描述来判断何时使用这个工具。
    summary_tool = QueryEngineTool.from_defaults(
        query_engine=summary_query_engine,
        description=(
            "Useful for summarization questions related to MetaGPT" # 翻译：适用于与 MetaGPT 相关的总结性问题。
        ),
    )
    
    # 向量工具 (vector_tool):
    # 将向量查询引擎包装起来。
    vector_tool = QueryEngineTool.from_defaults(
        query_engine=vector_query_engine,
        description=(
            "Useful for retrieving specific context from the MetaGPT paper."  # 翻译：适用于从 MetaGPT 论文中检索具体内容。
        ),
    )
    
    # --- 7. 构建路由查询引擎 ---
    
    # RouterQueryEngine (路由查询引擎) 是一个“决策者”。
    query_engine = RouterQueryEngine(
        # selector (选择器): 决定使用哪个工具。
        # LLMSingleSelector.from_defaults() 表示 LLM 会基于工具的描述来做选择（一选一）。
        selector=LLMSingleSelector.from_defaults(),
        # query_engine_tools (工具列表): 传入所有可供选择的工具。
        query_engine_tools=[
            summary_tool,
            vector_tool,
        ],
        # verbose (详细模式): 设置为 True，会在运行时打印出 LLM 做出选择的过程，便于调试。
        verbose=True
    )
    
    # 返回最终的路由查询引擎。
    return query_engine