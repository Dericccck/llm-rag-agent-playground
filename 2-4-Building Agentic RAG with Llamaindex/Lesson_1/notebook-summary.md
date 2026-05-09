# Lesson 1 学习摘要

## 对应 Notebook
- `L1_Router_Engine.ipynb`

## 这一节在做什么
这一节是在讲：
- 同一份文档，不一定只建一种索引
- 也不一定所有问题都该走同一种检索方式

所以它做的是一个 **Router Engine**：
- 用户问问题
- 系统先判断这是“概括型问题”还是“细节型问题”
- 再自动把问题路由到更合适的查询引擎

这个 notebook 用的是一篇 `metagpt.pdf` 论文。

## 这里要分清几个角色

### `qwen-max`
- 负责理解用户问题
- 也参与路由判断
- 不是直接去全文检索，而是先帮系统决定该选哪个工具

### `bge-small-en-v1.5`
- 负责把文本块向量化
- 供向量索引做语义检索

### `SummaryIndex`
- 适合回答全局性、概括性问题
- 比如“这篇论文主要讲了什么”

### `VectorStoreIndex`
- 适合回答具体细节问题
- 比如“某个实验结果是什么”“某个机制怎么实现”

### `RouterQueryEngine`
- 这是这一节真正的核心
- 它负责在多个查询引擎之间做“智能分发”

## 这个 notebook 里的实现工序

### 1. 先加载论文
通过：
- `SimpleDirectoryReader`

把 `metagpt.pdf` 读进来。

### 2. 再切分文档
通过：
- `SentenceSplitter`

把整篇论文切成多个文本块。

这一步是后续建索引的基础。

### 3. 配置模型和 embedding
这里做了两件事：

#### 大模型
- 使用 `qwen-max`
- 通过 DashScope 的 OpenAI 兼容接口接入

#### 向量模型
- 使用本地 `BAAI/bge-small-en-v1.5`

也就是：
- LLM 负责理解和回答
- embedding 模型负责把文本块变成向量

### 4. 基于同一份文档建两种索引

#### `SummaryIndex`
- 更适合做摘要型回答

#### `VectorStoreIndex`
- 更适合做语义相似度检索

这一节最重要的思想就是：
- 同一批 nodes，可以支持多种索引视角

### 5. 把索引变成查询引擎
通过：
- `summary_index.as_query_engine(...)`
- `vector_index.as_query_engine()`

把索引变成真正能答问题的引擎。

### 6. 给查询引擎加上工具描述
用：
- `QueryEngineTool`

把两个查询引擎包装起来，并且写清楚各自用途：
- 一个适合 summary
- 一个适合 retrieval

这一步是为了让路由器知道：
- 每个工具擅长什么

### 7. 创建 Router Engine
通过：
- `RouterQueryEngine`

再配合：
- `LLMSingleSelector`

让系统在用户提问时，先做一次“工具选择”。

### 8. 测试不同问题
例如：
- 问摘要：应该路由到 `SummaryIndex`
- 问具体机制：应该路由到 `VectorStoreIndex`

## 整个工序可以简化成
加载文档 -> 切块 -> 建 `SummaryIndex` 和 `VectorStoreIndex` -> 各自包装成工具 -> `RouterQueryEngine` 根据问题类型自动选工具 -> 返回答案

## 这一节的关键收获
- RAG 不一定只有一个检索入口。
- 同一份文档可以并行构建多种索引。
- Router 的价值在于：
  - 不是让模型直接回答
  - 而是先让模型决定“该怎么查”

