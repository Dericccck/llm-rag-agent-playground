#!pip install python-dotenv


import os
from dotenv import load_dotenv, find_dotenv

import numpy as np
# from trulens_eval import (
#     Feedback,
#     TruLlama
# )
# from trulens.providers.litellm import LiteLLM
from trulens.core import Feedback             # Feedback 移到了 core 模块
from trulens.apps.llamaindex import TruLlama  # TruLlama 移到了 apps 模块
from trulens.providers.litellm import LiteLLM # 这个不用动，保持原样

import nest_asyncio

# os.environ["DASHSCOPE_API_KEY"] = "sk-272ee942c239406681329c73361c2e3e"
# ----------------------------------------------------------------------
# 异步环境配置
# ----------------------------------------------------------------------
# nest_asyncio.apply()：用于解决在Jupyter/Colab环境中运行异步代码时，
#                       事件循环可能已经运行的问题。确保TruLens的异步评估能正常工作。
nest_asyncio.apply()


def get_dashscope_api_key():
    _ = load_dotenv(find_dotenv())
    # os.environ["DASHSCOPE_API_KEY"] = "sk-272ee942c239406681329c73361c2e3e"
    return os.getenv("DASHSCOPE_API_KEY")

def get_hf_api_key():
    _ = load_dotenv(find_dotenv())

    return os.getenv("HUGGINGFACE_API_KEY")

# ----------------------------------------------------------------------
# LLM Provider 配置
# ----------------------------------------------------------------------
# liteLLM_provider：使用 LiteLLM 封装的提供者，将大模型服务（如 DashScope/Qwen-Max）
#                 接入 TruLens，用于执行评估任务（如相关性判断、事实一致性检查）。
load_dotenv(find_dotenv())
dashscope_key = os.environ.get("DASHSCOPE_API_KEY")
# ----------------------------------------------------------------------
# 核心补丁：使用阿里云的 OpenAI 兼容模式，绕过 LiteLLM 的原生 Bug
# ----------------------------------------------------------------------
# 将通义千问的 Key 赋值给 OPENAI_API_KEY
os.environ["OPENAI_API_KEY"] = dashscope_key
# 将请求地址强行指向阿里云的兼容网关
os.environ["OPENAI_API_BASE"] = "https://dashscope.aliyuncs.com/compatible-mode/v1"

# 2. 实例化 Provider
# 注意这里的前缀改成了 openai/，这会骗过 LiteLLM，让它用最稳的通道发请求
liteLLM_provider = LiteLLM(model_engine="openai/qwen-max")


# liteLLM_provider = LiteLLM(model_engine="dashscope/qwen-max")

# ----------------------------------------------------------------------
# TruLens 评估指标定义 (Feedback Functions)
# ----------------------------------------------------------------------
# 回答相关性：衡量的是 Input (问题) 和 Output (回答) 之间的相关性
qa_relevance = (
    Feedback(
        liteLLM_provider.relevance_with_cot_reasons, name="Answer Relevance"
    )
    .on_input()  # 评估的第一个输入是用户问题 (Input)
    .on_output() # 评估的第二个输入是 LLM 的答案 (Output)
    # 目的：评估答案与问题的匹配程度。
)

# 上下文相关性：RAG 系统检索到的上下文与用户原始问题的相关程度
qs_relevance = (
    Feedback(
        liteLLM_provider.relevance_with_cot_reasons,
        name="Context Relevance"
    )
    .on_input()                # 评估的第一个输入是用户问题 (Input)
    .on_context(collect_list=False) # 评估的第二个输入是检索到的上下文 (Context)。
                                   # collect_list=False 表示对每个上下文块单独评估相关性。
    .aggregate(np.mean)       # 聚合函数：对所有上下文块的相关性得分求平均值。
    # 目的：评估检索器工作质量，即检索到的信息是否真正有助于回答问题。
)

# 事实一致性：评估 LLM 生成的答案是否基于检索到的上下文
groundedness = (
    Feedback(
        liteLLM_provider.groundedness_measure_with_cot_reasons,
        name="Groundedness"
    )
    .on_context(collect_list=True) # 评估的第一个输入是检索到的所有上下文 (作为 Source/证据)。
                                   # collect_list=True 表示将所有上下文合并。
    .on_output()                   # 评估的第二个输入是 LLM 的答案 (作为 Statement/陈述)。
    .aggregate(np.mean)            # 聚合函数：对答案中所有陈述的事实一致性得分求平均值。
    # 目的：检测 LLM 回答中是否存在“幻觉”（Hallucination），确保答案由上下文支持。
)

feedbacks = [qa_relevance, qs_relevance, groundedness] # 将所有定义的指标集合成列表


# ----------------------------------------------------------------------
# TruLens 记录器创建函数
# ----------------------------------------------------------------------

def get_trulens_recorder(query_engine, feedbacks, app_id):
    """
    创建 TruLlama 记录器实例，用于追踪和评估 RAG 流程。

    参数说明：
    - query_engine: LlamaIndex 的查询引擎实例。
    - feedbacks: 要应用于评估的 Feedback Function 列表。
    - app_id: 应用的唯一标识符，用于在 TruLens 看板中分组记录。
    """
    tru_recorder = TruLlama(
        query_engine,
        app_name="LlamaIndex_App",
        app_version="base",
        feedbacks=feedbacks, # 将定义的评估指标传入记录器
    )
    # 原理：TruLlama 会对 query_engine 及其组件进行动态代码注入（Instrumentation），
    #      自动捕获查询、检索、生成等步骤的输入和输出。
    return tru_recorder


def get_prebuilt_trulens_recorder(query_engine, app_id):
    """
    预构建的 TruLlama 记录器，使用全局定义的 feedbacks 列表。
    """
    # TruLlama 是 TruLens 专门为 LlamaIndex 深度定制的记录器类
    tru_recorder = TruLlama(
        query_engine,            # 传入你要监控的 LlamaIndex 查询引擎
        app_name="LlamaIndex_App", # 在 TruLens Dashboard 中显示的应用主分类名称
        app_version="base",       # 应用的版本号（方便你在调整参数后进行版本对比，如 "v1", "v2"）
        feedbacks=feedbacks,     # 核心：传入一个评估函数列表（如：诚实度评分、相关性评分等）
    )
    return tru_recorder  # 返回这个记录器对象，后续通过它来启动查询


from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.core.node_parser import SentenceWindowNodeParser
from llama_index.core.indices.postprocessor import MetadataReplacementPostProcessor
from llama_index.core.postprocessor import SentenceTransformerRerank
from llama_index.core import load_index_from_storage
from llama_index.core.node_parser import HierarchicalNodeParser
from llama_index.core.retrievers import AutoMergingRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.settings import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.node_parser import get_leaf_nodes
import os


def build_sentence_window_index(
    document,       # 输入参数：待索引的 LlamaIndex 文档对象列表
    llm,            # 输入参数：配置好的大语言模型实例（如 Qwen 或 GPT）
    embed_model,    # 输入参数：可以是本地路径字符串，也可以是已初始化的 Embedding 对象
    save_dir="sentence_index"  # 输入参数：索引在磁盘上的持久化存储目录，默认为 "sentence_index"
):
    """
    负责数据准备和索引构建，构建或加载一个 Sentence Window Index（句子窗口索引）。
    这是 LlamaIndex 中一种先进的 RAG 策略，用于提高检索的精度和上下文的完整性。
    侧重于精确性。检索小块（句子），但提供大块（句子窗口）给 LLM。
    将文档分割成重叠的句子窗口，为后续的精确检索做准备。
    （注：代码配置 window_size=3，意味着每个窗口包含当前句+前后各3句，共7句。）

    参数说明：
    - document: 原始文档对象。
    - llm: 要使用的 LLM 实例。
    - embed_model: 用于向量化的嵌入模型。
    - save_dir: 索引持久化的目录。
    """


    # --- 1. 智能处理嵌入模型 (Embedding Model) ---
    # 检查传进来的 embed_model 是否为字符串类型（即文件路径）
    if isinstance(embed_model, str):
        # 如果字符串是以 "local:" 开头的（常见于某些教程格式），则提取后面的实际路径
        if embed_model.startswith("local:"):
            model_name = embed_model.split("local:")[1] # 截取 "local:" 之后的部分作为模型路径
        else:
            model_name = embed_model # 直接将该字符串视为模型路径
            
        # 使用 HuggingFaceEmbedding 初始化本地向量模型
        Settings.embed_model = HuggingFaceEmbedding(
            model_name=model_name,      # 指定本地模型所在的绝对路径
            device="mps",               # 针对 Mac M1/M2/M3 芯片使用 Metal Performance Shaders 加速
            local_files_only=True       # 强制只从本地读取，禁止连接 HuggingFace 远程服务器
        )
    else:
        # 如果传进来的是已经初始化好的对象，直接将其赋值给全局设置
        Settings.embed_model = embed_model

    # 将传入的 LLM 实例配置到全局设置中，供后续索引构建使用
    Settings.llm = llm

    # --- 2. 节点解析器 (Sentence Window Node Parser) ---
    # 这是关键：创建一个特殊的解析器，它会把文档拆分成单个句子
    node_parser = SentenceWindowNodeParser.from_defaults(
        window_size=3,                           # 设置窗口大小：检索到某句时，额外附带前后各 3 句话作为背景
        window_metadata_key="window",            # 在元数据中存储上下文窗口的键名
        original_text_metadata_key="original_text", # 在元数据中存储原始单句文本的键名
    )
    # 将此解析器设为全局默认解析器
    Settings.node_parser = node_parser

    # --- 3. 持久化与加载逻辑 ---
    # 检查存储目录是否已经存在
    if not os.path.exists(save_dir):
        # 如果目录不存在：说明是第一次运行，需要根据文档创建新索引
        # 使用 from_documents 会自动触发 node_parser 进行切分和向量化
        sentence_index = VectorStoreIndex.from_documents([document])
        # 将生成的索引数据（向量和元数据）保存到指定的硬盘目录中
        sentence_index.storage_context.persist(persist_dir=save_dir)
    else:
        # 如果目录已存在：直接从硬盘加载现有索引，避免重复消耗 Token 或算力进行向量化
        # 加载时必须显式传入 embed_model，否则 LlamaIndex 可能会回退到默认的 OpenAI API
        sentence_index = load_index_from_storage(
            StorageContext.from_defaults(persist_dir=save_dir), # 定位存储上下文
            embed_model=Settings.embed_model # 确保加载时使用的向量空间与构建时一致
        )

    # 返回构建好或加载好的索引对象
    return sentence_index


def get_sentence_window_query_engine(
    sentence_index,
    similarity_top_k=6,
    rerank_top_n=2,
):
    """
    负责查询执行和结果优化。
    配置和创建一个具有句子窗口 (Sentence Window) 机制、智能后处理和重排序 (Rerank) 功能的查询引擎。

    参数说明：
    - sentence_index: 必需参数，一个已构建好的 Sentence Window Index 对象，是数据检索的来源。
    - similarity_top_k: 可选参数，默认为 6。定义了初始**向量检索**阶段需要获取的相似节点的数量。
    - rerank_top_n: 可选参数，默认为 2。定义了**重排序**后，最终保留并传递给 LLM 的最优节点的数量。
    """

    # ----------------------------------------------------------------------
    # 1. 定义后处理器 (Postprocessor)
    # ----------------------------------------------------------------------
    # 后处理器是指在 RAG 流程中的检索阶段结束之后、但 LLM 生成阶段开始之前执行的一系列操作。
    
    postproc = MetadataReplacementPostProcessor(target_metadata_key="window")
    
    # 作用：MetadataReplacementPostProcessor 是**上下文还原处理器**。
    # 原理：它查找检索到的节点的元数据中键名为 "window" 的内容（即完整的句子窗口上下文），
    #      并用这个**大块**内容替换节点原本的**小块**内容（即单个句子）。
    # 目的：实现“小块（句子）高精度检索”和“大块（窗口）高质量生成”的结合。

    # ----------------------------------------------------------------------
    # 2. 定义重排序器 (Reranker)
    # ----------------------------------------------------------------------
    reranker_base_path = os.path.expanduser("~/Desktop/AIAgent/models/models--BAAI--bge-reranker-base/snapshots/2cfc18c9415c912f9d8155881c133215df768a70")
    rerank = SentenceTransformerRerank(
        top_n=rerank_top_n, model=reranker_base_path
    )
    
    # SentenceTransformerRerank 是一个基于交叉编码器的重排序器。
    # top_n=rerank_top_n：指定重排序后只保留最相关的 rerank_top_n 个结果。
    # model="BAAI/bge-reranker-base"：使用的是 BAAI/bge-reranker-base 这个高性能模型进行二次打分。
    # 目的：在上下文还原后，对所有候选的句子窗口进行二次精确筛选，进一步提高最终上下文的相关性。

    # ----------------------------------------------------------------------
    # 3. 创建查询引擎 (Query Engine)
    # ----------------------------------------------------------------------
    sentence_window_engine = sentence_index.as_query_engine(
        similarity_top_k=similarity_top_k,
        node_postprocessors=[postproc, rerank]
    )

    # sentence_index.as_query_engine(...)：调用索引的方法创建查询引擎。
    # similarity_top_k：指定 Retriever（检索器）的 k 值，检索器从索引中获取 top_k 个最相似的**句子**。
    # node_postprocessors=[postproc, rerank]：指定后处理链。
    # 顺序：检索器检索 6 个句子 -> postproc 将 6 个句子替换为 6 个句子窗口 -> rerank 对 6 个窗口重排序并选出最终的 2 个。
    

    # ----------------------------------------------------------------------
    # 4. 返回结果
    # ----------------------------------------------------------------------
    return sentence_window_engine


def build_automerging_index(
    documents,
    llm,
    embed_model,
    save_dir="merging_index",
    chunk_sizes=None,
):
    """
    负责数据准备和索引构建，创建文档的层次化结构（Auto-Merging Index）。
    侧重于上下文的完整性和灵活合并。
    建立多层级的文档结构，检索最小块，但允许在检索时根据需求动态合并到更大的父块。

    参数说明：
    - documents: 原始文档对象列表。
    - llm: 要使用的 LLM 实例。
    - embed_model: 用于向量化的嵌入模型。
    - save_dir: 索引持久化的目录。
    - chunk_sizes: 可选参数，定义文档分层切分的大小。
    """
    # 配置全局设置
    Settings.llm = llm
    Settings.embed_model = HuggingFaceEmbedding(
        # model_name=LOCAL_BGE_PATH,
        model_name=embed_model,
        # 如果您的机器有 GPU，建议设置 device="cuda"
        device="cpu", 
        # 连不了外网记得这个标志要设置为True，不然虽然本地有了还会掉huggingface获取包信息检验
        local_files_only=True,
    )

    # 设置默认块大小：大块2048字符，中块512字符，小块128字符
    chunk_sizes = chunk_sizes or [2048, 512, 128]
    # 创建分层解析器，按指定大小切割文档
    node_parser = HierarchicalNodeParser.from_defaults(chunk_sizes=chunk_sizes)
    # 将文档解析成层次化的节点树（包含大块、中块、小块）
    nodes = node_parser.get_nodes_from_documents(documents)
    # 只获取最底层的叶子节点（最小的块）用于向量检索
    leaf_nodes = get_leaf_nodes(nodes)

    # 创建存储上下文
    storage_context = StorageContext.from_defaults()
    # 关键：将所有节点（包括父节点和子节点）存入文档存储
    storage_context.docstore.add_documents(nodes)
    # 现在 docstore 包含了完整的层次结构：
    # - 叶子节点：用于向量检索（向量存储）
    # - 父节点：用于后续的自动合并（文档存储）

    # 检查是否已存在保存的索引
    if not os.path.exists(save_dir):
        # 创建新索引：只用叶子节点构建向量索引，确保检索的最小粒度
        automerging_index = VectorStoreIndex(
            leaf_nodes,
            storage_context=storage_context
        )
        # 持久化保存整个索引结构到磁盘
        automerging_index.storage_context.persist(persist_dir=save_dir)
    else:
        # 加载已保存的索引
        automerging_index = load_index_from_storage(
            StorageContext.from_defaults(persist_dir=save_dir)
        )
    return automerging_index


# ----------------------------------------------------------------------
# Auto-Merging Query Engine 构建方法
# ----------------------------------------------------------------------
def get_automerging_query_engine(
    automerging_index,       # 参数1：已构建的自动合并索引
    similarity_top_k=12,     # 参数2：向量检索返回12个候选节点
    rerank_top_n=2,          # 参数3：重排序后保留2个最终节点
):
    """
    负责查询执行和结果优化，实现层次化检索和智能合并。
    工作流程：
        1、检索叶子节点：找到最相关的细节小块
        2、自动合并：如果多个相关的小块属于同一个父块，则返回完整的父块
        3、重排序：对合并后的结果进行重新排序
    
    参数说明：
    - automerging_index: 已构建好的 Auto-Merging Index 对象。
    - similarity_top_k: 初始检索（针对最小块）获取的节点数量。
    - rerank_top_n: 重排序后最终保留的节点数量。
    """
    # 从自动合并索引创建基础检索器
    base_retriever = automerging_index.as_retriever(similarity_top_k=similarity_top_k)
    # 在基础检索器上包装 AutoMerging 逻辑，实现智能合并
    retriever = AutoMergingRetriever(
        base_retriever, automerging_index.storage_context, verbose=True
    )
    # 创建句子转换器重排序器
    reranker_base_path = os.path.expanduser("~/Desktop/AIAgent/models/models--BAAI--bge-reranker-base/snapshots/2cfc18c9415c912f9d8155881c133215df768a70")
    rerank = SentenceTransformerRerank(
        top_n=rerank_top_n, model=reranker_base_path
    )
    # 基于检索器创建最终的查询引擎
    auto_merging_engine = RetrieverQueryEngine.from_args(
        retriever, 
        node_postprocessors=[rerank] # 将重排序器作为后处理器链传入
    )
    # 原理：Retriever 负责叶子节点检索和自动合并，Postprocessor 负责最终优化。
    return auto_merging_engine
