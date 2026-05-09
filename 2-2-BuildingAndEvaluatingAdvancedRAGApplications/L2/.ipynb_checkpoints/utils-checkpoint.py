#!pip install python-dotenv


import os
from dotenv import load_dotenv, find_dotenv

import numpy as np
import nest_asyncio

# ----------------------------------------------------------------------
# 异步环境配置
# ----------------------------------------------------------------------
# nest_asyncio.apply()：用于解决在Jupyter/Colab环境中运行异步代码时，
#                       事件循环可能已经运行的问题。确保TruLens的异步评估能正常工作。
nest_asyncio.apply()


def get_dashscope_api_key():
    _ = load_dotenv(find_dotenv())

    return os.getenv("DASHSCOPE_API_KEY")


def get_hf_api_key():
    _ = load_dotenv(find_dotenv())

    return os.getenv("HUGGINGFACE_API_KEY")


from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.core.node_parser import SentenceWindowNodeParser
from llama_index.core.indices.postprocessor import MetadataReplacementPostProcessor
from llama_index.core.postprocessor import SentenceTransformerRerank
from llama_index.core import load_index_from_storage
from llama_index.core.settings import Settings
import os

def build_sentence_window_index(
    document,
    llm,
    embed_model="local:BAAI/bge-small-en-v1.5",
    save_dir="sentence_index"
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
    # 配置全局设置
    Settings.llm = llm
    Settings.embed_model = embed_model

    # 创建句子窗口节点解析器
    node_parser = SentenceWindowNodeParser.from_defaults(
        window_size=3,
        window_metadata_key="window",
        original_text_metadata_key="original_text",
    )
    Settings.node_parser = node_parser

    # 缓存/持久化逻辑：如果索引不存在则创建，否则加载
    if not os.path.exists(save_dir):
        # 创建新索引：使用全局配置的 node_parser 对文档进行切分、嵌入和索引
        sentence_index = VectorStoreIndex.from_documents(
            [document]
        )
        # 将索引数据持久化保存到磁盘
        sentence_index.storage_context.persist(persist_dir=save_dir)
    else:
        # 加载已保存的索引以节省时间
        sentence_index = load_index_from_storage(
            StorageContext.from_defaults(persist_dir=save_dir)
        )

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
    
    rerank = SentenceTransformerRerank(
        top_n=rerank_top_n, model="BAAI/bge-reranker-base"
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
    embed_model="local:BAAI/bge-small-en-v1.5",
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
    Settings.embed_model = embed_model

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
    rerank = SentenceTransformerRerank(
        top_n=rerank_top_n, model="BAAI/bge-reranker-base"
    )
    # 基于检索器创建最终的查询引擎
    auto_merging_engine = RetrieverQueryEngine.from_args(
        retriever, 
        node_postprocessors=[rerank] # 将重排序器作为后处理器链传入
    )
    # 原理：Retriever 负责叶子节点检索和自动合并，Postprocessor 负责最终优化。
    return auto_merging_engine

