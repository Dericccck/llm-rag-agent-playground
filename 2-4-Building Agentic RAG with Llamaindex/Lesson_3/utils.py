# TODO: abstract all of this into a function that takes in a PDF file name 

# 导入必要的库
# 这些是LlamaIndex框架的核心组件，用于构建RAG（检索增强生成）系统
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, SummaryIndex
from llama_index.core.node_parser import SentenceSplitter  # 用于将文档分割成小块
from llama_index.core.tools import FunctionTool, QueryEngineTool  # 用于创建可调用的工具
from llama_index.core.vector_stores import MetadataFilters, FilterCondition  # 用于元数据过滤
from typing import List, Optional  # 用于类型注解
import os

def get_doc_tools(
    file_path: str,  # PDF文件的路径，例如"metagpt.pdf"
    name: str,       # 工具的名称标识，用于区分不同文档的工具
) -> str:
    """Get vector query and summary query tools from a document.
    从PDF文档创建查询工具
    这个函数会：
    1. 加载PDF文档
    2. 将文档分割成小块
    3. 创建向量索引（用于语义搜索）
    4. 创建摘要索引（用于整体概览）
    5. 返回两个查询工具：
       - vector_query_tool：用于按页码查询具体内容
       - summary_tool：用于获取文档整体摘要
    
    参数：
    file_path (str): PDF文件的路径
    name (str): 工具的名称标识（例如"metagpt"）
    
    返回：
    tuple: (vector_query_tool, summary_tool)
    """

    # load documents
    documents = SimpleDirectoryReader(input_files=[file_path]).load_data()
    splitter = SentenceSplitter(chunk_size=1024)
    nodes = splitter.get_nodes_from_documents(documents)
    vector_index = VectorStoreIndex(nodes)
    
    def vector_query(
        query: str, 
        page_numbers: Optional[List[str]] = None
    ) -> str:
        """Use to answer questions over the MetaGPT paper.
    
        Useful if you have specific questions over the MetaGPT paper.
        Always leave page_numbers as None UNLESS there is a specific page you want to search for.
    
        Args:
            query (str): the string query to be embedded.
            page_numbers (Optional[List[str]]): Filter by set of pages. Leave as NONE 
                if we want to perform a vector search
                over all pages. Otherwise, filter by the set of specified pages.
        
                执行向量搜索，从文档中查找与查询相关的内容
        
        参数：
        query (str): 用户的查询字符串，会被转换为向量进行语义搜索
        page_numbers (Optional[List[str]]): 要过滤的页码列表
            - None或空列表：搜索所有页面
            - 例如["1", "2", "3"]：只搜索第1、2、3页
        
        返回：
        str: 搜索结果的文本内容
        
        工作原理（根据元数据管理规范）：
        1. 先应用元数据过滤（按页码）→ 缩小搜索范围
        2. 再进行向量检索 → 在过滤后的结果中找最相关的内容
        这种顺序大大提高了搜索效率和精确度
        """
    
        page_numbers = page_numbers or []
        metadata_dicts = [
            {"key": "page_label", "value": p} for p in page_numbers
        ]
        
        query_engine = vector_index.as_query_engine(
            similarity_top_k=2,
            filters=MetadataFilters.from_dicts(
                metadata_dicts,
                condition=FilterCondition.OR
            )
        )
        response = query_engine.query(query)
        return response
        
    
    vector_query_tool = FunctionTool.from_defaults(
        name=f"vector_tool_{name}",
        fn=vector_query
    )
    
    summary_index = SummaryIndex(nodes)
    summary_query_engine = summary_index.as_query_engine(
        response_mode="tree_summarize",
        use_async=True,
    )
    summary_tool = QueryEngineTool.from_defaults(
        name=f"summary_tool_{name}",
        query_engine=summary_query_engine,
        description=(
            "Use ONLY IF you want to get a holistic summary of MetaGPT. "  # 只有在你想获得MetaGPT的整体摘要时才使用。
            "Do NOT use if you have specific questions over MetaGPT."  # 如果你对MetaGPT有具体问题，请不要使用。
        ),
    )

    return vector_query_tool, summary_tool