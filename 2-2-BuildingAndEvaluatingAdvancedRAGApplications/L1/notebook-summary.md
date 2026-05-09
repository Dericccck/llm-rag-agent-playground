# Lesson 1 学习摘要

## 对应 Notebook
- `L1-Advanced_RAG_Pipeline.ipynb`

## 这一节在做什么
这一节是在讲一个完整的高级 RAG 思路：
- 先搭一个基础 RAG
- 再用评估工具看它表现如何
- 然后引入两种更高级的检索策略来改进效果

也就是说，这一节不是只教“怎么查”，而是在讲：
- 基础版 RAG 怎么做
- 高级版 RAG 为什么更强
- 怎么用指标验证优化是不是有效

## 这里要分清几个角色

### `qwen-max`
- 负责最后根据检索到的上下文生成答案
- 它是回答层，不负责存储

### `bge-small-en-v1.5`
- 负责把文本块向量化
- 支撑向量检索

### `VectorStoreIndex`
- 这是基础 RAG 的索引层
- 负责把文档块变成可检索向量

### `TruLens`
- 负责评估 RAG
- 记录输入、检索上下文、输出答案，并计算反馈分数

### 两种高级检索策略
- Sentence Window Retrieval
- Auto-merging Retrieval

## 这个 notebook 里的实现工序

### 第一部分：先搭基础 RAG

#### 1. 加载 PDF 文档
把整本电子书读进来，然后合并成一个大的 `Document`。

这一步是因为 PDF 往往会按页拆开，先合并有助于统一处理。

#### 2. 配置模型和 embedding
这里设置了：
- LLM：`qwen-max`
- embedding：本地 `bge-small-en-v1.5`

### 3. 建立向量索引
通过：
- `VectorStoreIndex.from_documents([document])`

把整本书切块并向量化。

### 4. 创建基础查询引擎
通过：
- `index.as_query_engine()`

得到一个标准的基础 RAG 问答入口。

### 5. 测试基础查询
用户提问后，流程就是：
- 问题向量化
- 从向量库中召回相关文本块
- 把上下文和问题一起交给 LLM
- 生成答案

## 第二部分：接入 TruLens 做评估

### 6. 准备评估问题集
从 `eval_questions.txt` 读入一批问题，再加入你自己的测试问题。

### 7. 初始化 TruLens
通过：
- `Tru()`
- `tru.reset_database()`

建立评估数据库。

### 8. 为基础查询引擎创建 recorder
通过：
- `get_prebuilt_trulens_recorder(query_engine, app_id=...)`

让基础 RAG 每次回答时都被记录。

### 9. 批量跑评估
用所有问题循环调用 `query_engine.query(question)`。

TruLens 会记录：
- 输入问题
- 检索到的上下文
- 最终回答
- 各种反馈指标

### 10. 查看 leaderboard 和 dashboard
通过：
- `tru.get_records_and_feedback(...)`
- `tru.run_dashboard()`

对比不同 RAG 方案的表现。

## 第三部分：升级成高级 RAG

### A. Sentence Window Retrieval
这一招的核心是：
- 检索时按更小粒度句子做匹配
- 回答时给 LLM 提供更大窗口上下文

也就是：
- 小粒度检索保证精度
- 大窗口上下文保证语义完整

这个 notebook 通过工具函数：
- `build_sentence_window_index(...)`
- `get_sentence_window_query_engine(...)`

来完成这套管线。

### B. Auto-merging Retrieval
这一招的核心是：
- 先检索细粒度小块
- 再把相关小块沿着层级结构往上合并
- 最后把更完整、更有语义连贯性的上下文交给 LLM

这个 notebook 通过：
- `build_automerging_index(...)`
- `get_automerging_query_engine(...)`

来构建自动合并检索引擎。

### 11. 分别评估两种高级方案
对 Sentence Window 和 Auto-merging 各自都跑一遍 TruLens 评估。

这样你就能看到：
- 基础 RAG
- 句窗检索
- 自动合并检索

三者在同一问题集上的差异。

## 整个工序可以简化成
加载文档 -> 建基础向量索引 -> 做基础 RAG -> 接入 TruLens 评估 -> 换成 Sentence Window Retrieval -> 再评估 -> 换成 Auto-merging Retrieval -> 再评估 -> 比较不同高级 RAG 策略效果

## 这一节的关键收获
- RAG 不只是“能不能答”，还要“答得是否更 grounded、更相关”。
- 高级 RAG 的改进重点通常在检索层，而不是只换更强的模型。
- TruLens 的价值在于把“感觉更好”变成“可量化比较”。

