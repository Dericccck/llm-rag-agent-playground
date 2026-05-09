# Lesson 4 学习摘要

## 对应 Notebook
- `L4-Auto-merging_Retrieval.ipynb`

## 这一节在做什么
这一节是在讲另一种高级检索策略：
- Auto-merging Retrieval

它要解决的问题是：
- 直接检索很小的文本块，虽然精确，但上下文太碎
- 直接检索大文本块，虽然上下文足，但不够准

它的解决办法是：
- 先在最细粒度的小块上检索
- 再把命中的小块沿着层级结构自动往上合并
- 最终给 LLM 更大、更连贯的语义片段

## 这里要分清几个角色

### `HierarchicalNodeParser`
- 负责把文档切成多层级节点
- 并建立父子关系

### `leaf_nodes`
- 这是最细粒度的叶子节点
- 用来做最初的向量检索

### `docstore`
- 存储所有层级节点
- 让系统知道“这个叶节点的父节点是谁”

### `AutoMergingRetriever`
- 负责把检索命中的小块自动合并成更高层的父块

### `SentenceTransformerRerank`
- 负责对合并后的候选上下文再重排

### `qwen-max`
- 负责基于最后得到的上下文生成回答

## 这个 notebook 里的实现工序

### 1. 加载文档并合并
先把书读进来，再整成一个统一 `Document`。

### 2. 定义层级切分器
通过：
- `HierarchicalNodeParser.from_defaults(chunk_sizes=[2048, 512, 128])`

把文档切成多层：
- 大块：2048
- 中块：512
- 小块：128

这里最重要的不是切多少层，而是：
- 节点之间保留父子关系

### 3. 提取叶子节点
通过：
- `get_leaf_nodes(nodes)`

拿到最细粒度的小块。

这些叶节点才是真正被向量化和检索的单位。

### 4. 配置模型和 embedding
设置：
- `qwen-max`
- 本地 `bge-small-en-v1.5`

### 5. 构建索引时做两件事

#### 第一件事：把所有层级节点放进 docstore
因为之后要做自动合并，系统必须知道：
- 某个叶节点属于哪个父节点

#### 第二件事：只拿叶节点建向量索引
因为检索要在最细粒度上做，才够精准。

所以这里的设计是：
- 全部节点进 docstore
- 只有叶节点进 vector index

### 6. 定义自动合并检索器
流程是先创建一个基础 retriever：
- `automerging_index.as_retriever(similarity_top_k=...)`

然后再包上一层：
- `AutoMergingRetriever(...)`

这一层才是真正的核心，它会：
- 看看命中的叶节点是否属于同一个上层语义块
- 如果是，就往上合并

### 7. 加上 reranker
和前一节类似，再通过：
- `SentenceTransformerRerank`

对检索/合并结果做二次排序。

### 8. 组装最终查询引擎
通过：
- `RetrieverQueryEngine.from_args(...)`

把：
- 检索器
- 合并逻辑
- reranker

都装进一个完整的查询入口。

### 9. 查询时真正发生了什么
用户问问题后，大致流程是：
- 问题向量化
- 先匹配最相关的叶子节点
- 再看这些叶子节点能否自动向上合并成更大块
- 对合并结果 rerank
- 把更完整上下文交给 LLM 生成回答

### 10. 抽成复用函数
Notebook 后面把流程封成：
- `build_automerging_index(...)`
- `get_automerging_query_engine(...)`

方便重复实验。

### 11. 评估不同层级方案
最后还比较了：
- 两层切分
- 三层切分

通过 TruLens 看不同层级结构对 RAG 表现的影响。

## 整个工序可以简化成
加载文档 -> 用 `HierarchicalNodeParser` 切成多层节点 -> 所有节点进 docstore、叶节点进向量索引 -> 查询时先检索叶节点 -> `AutoMergingRetriever` 自动向上合并上下文 -> rerank -> LLM 回答 -> 用 TruLens 对比不同层级配置

## 这一节的关键收获
- Auto-merging Retrieval 的核心是“先精检，再扩上下文”。
- 它和 Sentence Window Retrieval 的区别在于：
  - Sentence Window 是基于固定句子窗口补上下文
  - Auto-merging 是基于文档层级结构动态合并上下文
- 这类方法特别适合长文档、章节结构明显的资料型 RAG。

