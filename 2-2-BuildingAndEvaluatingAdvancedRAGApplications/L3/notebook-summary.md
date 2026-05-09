# Lesson 3 学习摘要

## 对应 Notebook
- `L3-Sentence_window_retrieval.ipynb`

## 这一节在做什么
这一节是在专门讲一种高级检索策略：
- Sentence Window Retrieval

它要解决的问题是：
- 检索块切太小，容易丢上下文
- 检索块切太大，又容易降低检索精度

它的做法是：
- 检索时只拿“核心句子”做向量匹配
- 交给 LLM 时再把这个句子周围的窗口上下文补回来

## 这里要分清几个角色

### `SentenceWindowNodeParser`
- 负责把文档切成“句子节点”
- 同时为每个句子保存周围窗口上下文

### `bge-small-en-v1.5`
- 负责把句子级节点向量化
- 检索阶段主要匹配的是这些短句

### `MetadataReplacementPostProcessor`
- 负责把被检索到的短句，替换成它对应的窗口文本

### `SentenceTransformerRerank`
- 负责对召回结果再做一次重排序
- 提高最终送给模型的上下文质量

### `qwen-max`
- 负责基于最终上下文生成回答

## 这个 notebook 里的实现工序

### 1. 加载 PDF 并合并成一个 Document
先把整本书读进来，再拼成一个整体文档。

### 2. 定义 `SentenceWindowNodeParser`
这里的关键参数有：
- `window_size`
- `window_metadata_key="window"`
- `original_text_metadata_key="original_text"`

意思是：
- 每个节点本体只是一个句子
- 但它的 metadata 里还存了前后若干句组成的窗口

### 3. 理解“为什么 window 内容会重复”
因为每个句子都会带着自己的邻居句子。

当文档很短时，不同句子的窗口可能几乎覆盖全文。

这一步 notebook 里专门做了小例子来帮助理解：
- 句子本身是检索单位
- 但窗口是生成时使用的上下文单位

### 4. 配置模型和 embedding
设置：
- `qwen-max`
- 本地 `bge-small-en-v1.5`

同时把全局 `Settings.node_parser` 指向 `SentenceWindowNodeParser`。

### 5. 建立句窗索引
通过：
- `VectorStoreIndex.from_documents([document])`

但这里因为 node parser 已切成句子，所以真正进向量索引的是“句子级节点”。

### 6. 持久化索引
把索引保存到本地，避免每次重建。

### 7. 定义后处理器

#### `MetadataReplacementPostProcessor`
它会在检索完成后：
- 读取节点 metadata 里的 `"window"`
- 用窗口文本替换原本短句文本

这一步非常关键，因为它把“精准检索”和“完整上下文”桥接起来了。

### 8. 加入 reranker
通过：
- `SentenceTransformerRerank`

对已召回的窗口做第二轮排序。

也就是：
- 第一轮：向量检索找候选
- 第二轮：reranker 更精细判断哪些最相关

### 9. 组装查询引擎
最终查询引擎流程大致是：
- 先按句子检索 top-k
- 再把句子替换成窗口上下文
- 再 rerank
- 最后把结果喂给 LLM 回答

### 10. 抽成可复用函数
Notebook 后面把这套流程封装成：
- `build_sentence_window_index(...)`
- `get_sentence_window_query_engine(...)`

便于后续实验复用。

### 11. 做 TruLens 评估
最后又比较了不同窗口大小：
- 比如 window size = 1
- 和更大的窗口大小

看哪种设定在评估指标上更好。

## 整个工序可以简化成
加载文档 -> 切成句子节点并给每句挂窗口元数据 -> 建向量索引 -> 查询时先按短句检索 -> 用后处理器替换成完整窗口 -> 用 reranker 重排 -> 交给 LLM 回答 -> 用 TruLens 比较不同窗口大小

## 这一节的关键收获
- Sentence Window Retrieval 的核心不是“多检索一点”，而是“检索粒度和生成粒度分离”。
- 它兼顾了：
  - 精准检索
  - 完整上下文
- 对很多长文档问答场景，这是一种非常实用的高级 RAG 手法。

