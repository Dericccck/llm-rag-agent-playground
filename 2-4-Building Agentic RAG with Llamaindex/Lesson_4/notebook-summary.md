# Lesson 4 学习摘要

## 对应 Notebook
- `L4_Building_a_Multi-Document_Agent.ipynb`

## 这一节在做什么
这一节是在讲：
- 当文档不止一篇时，怎么做 Agentic RAG

核心目标是构建一个 **Multi-Document Agent**：
- 能在多篇论文之间自动选择相关工具
- 既能回答单篇论文问题
- 也能做跨论文比较和综合分析

## 这里要分清几个角色

### `qwen-max`
- 负责理解用户问题
- 负责决定调用哪些论文工具
- 负责整合多篇论文的检索结果

### `bge-small-en-v1.5`
- 负责向量化文档块
- 也支撑后面的工具检索

### 每篇论文对应的一组工具
- `vector_tool`
- `summary_tool`

也就是每篇论文其实都被包装成一个“可被 Agent 调用的小知识单元”。

### `FunctionAgent`
- 负责把大量论文工具组织成一个统一 Agent

### `ObjectIndex`
- 这是后半节最重要的新角色
- 它不是索引论文内容，而是索引“工具对象本身”

## 这个 notebook 里的实现工序

### 第一部分：先做 3 篇论文版本

#### 1. 准备论文列表
这里先用 3 篇论文：
- MetaGPT
- LongLoRA
- Self-RAG

#### 2. 配置模型和 embedding
设置：
- `qwen-max`
- `bge-small-en-v1.5`

#### 3. 为每篇论文创建专用工具
通过：
- `get_doc_tools(paper, Path(paper).stem)`

为每篇论文各生成两类工具：
- 向量检索工具
- 摘要工具

所以 3 篇论文最后会变成一组工具集合。

#### 4. 合并所有工具
把所有论文的工具拉平成一个列表：
- `initial_tools`

#### 5. 创建多文档 Agent
通过：
- `FunctionAgent(tools=initial_tools, llm=llm, verbose=True)`

让一个 Agent 拥有跨 3 篇论文的工具能力。

#### 6. 测试单篇和跨篇问题
例如：
- 问 LongLoRA 的评估数据集
- 同时总结 Self-RAG 和 LongLoRA

Agent 会自己决定该调哪篇论文的工具。

### 第二部分：扩展到 11 篇论文
这一部分开始暴露一个现实问题：
- 论文越来越多时，不能把所有工具无脑全塞给 Agent
- 工具太多时，模型选工具的难度会变大

所以 notebook 引入了“工具检索”。

#### 1. 扩展到 11 篇论文
先为 11 篇论文继续生成各自的：
- `vector_tool`
- `summary_tool`

于是总工具数会明显增加。

#### 2. 建立工具对象索引
这里的关键代码是：
- `ObjectIndex.from_objects(all_tools, index_cls=VectorStoreIndex)`

注意这一步非常重要：
- 不是给论文内容建索引
- 而是给“工具”建索引

也就是：
- 每个工具也变成一个可检索对象
- 用户问题先用来检索“最可能相关的工具”

#### 3. 创建工具检索器
通过：
- `obj_index.as_retriever(similarity_top_k=5)`

把用户问题映射到“最相关的几个工具”。

#### 4. 创建支持 `tool_retriever` 的 Agent
这次创建 `FunctionAgent` 时，不再传一大坨固定工具列表，而是传：
- `tool_retriever=obj_retriever`

这表示：
- 先做工具检索
- 再在命中的工具上做调用

#### 5. 处理跨论文复杂问题
例如：
- 比较 MetaGPT 和 SWE-Bench 的评估数据集
- 比较 LongLoRA 和 LoftQ 的方法

这时 Agent 的流程会变成：
- 先检索相关论文工具
- 再调用这些工具
- 最后整合多篇论文结果

### 6. 观察不同模型的工具调用效果
这个 notebook 还特别记录了一个现实现象：
- 不同模型在“工具选择”上的稳定性不同
- `qwen-max` 和 `gpt-4o-mini` 在跨论文工具调用时表现可能不同

这点对真正做 Agentic RAG 很重要，因为问题不只在索引，也在模型的 tool-use 能力。

## 整个工序可以简化成
为每篇论文生成专属工具 -> 把多篇论文工具交给 Agent -> 先实现小规模多文档问答 -> 文档数量增大后，引入 `ObjectIndex` 做工具检索 -> Agent 先选相关工具再回答跨论文问题

## 这一节的关键收获
- 多文档 RAG 的难点不只是“文档多”，而是“工具也多”。
- `ObjectIndex` 很关键，因为它把“工具选择”也变成了一个检索问题。
- 这节非常像真正的 Agentic RAG 形态：
  - 文档内容有索引
  - 工具本身也可检索
  - Agent 在多篇资料之间动态规划查询路径

