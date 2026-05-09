# Lesson 2 学习摘要

## 对应 Notebook
- `L2-RAG_Triad_of_metrics.ipynb`

## 这一节在做什么
这一节专门在讲：
- RAG 到底该怎么评估

不是看“回答看起来不错”就算了，而是把 RAG 拆成三个核心维度来打分，这就是所谓的：
- RAG Triad of Metrics

也就是三元评估框架：
- Answer Relevance
- Context Relevance
- Groundedness

## 这里要分清几个角色

### `sentence_window_engine`
- 这是被评估的 RAG 系统
- 它负责检索上下文并生成答案

### `qwen-max`
- 一方面是业务问答模型
- 另一方面也通过 LiteLLM provider 扮演“评估裁判”

### `TruLens`
- 负责记录 RAG 执行过程
- 负责把问题、上下文、答案送进评估函数

### 三个反馈函数
- `Answer Relevance`
- `Context Relevance`
- `Groundedness`

## 这个 notebook 里的实现工序

### 1. 先准备一个可运行的 RAG 引擎
这节没有从零重建复杂检索，而是复用了：
- Sentence Window Retrieval

通过：
- `build_sentence_window_index(...)`
- `get_sentence_window_query_engine(...)`

得到一个可用的 `sentence_window_engine`。

也就是说：
这一节的重点不是“怎么搭 RAG”，而是“怎么评估它”。

### 2. 配置评估用的 provider
通过：
- `LiteLLM`

把 `qwen-max` 接成 TruLens 的评估提供者。

这表示：
- 模型不仅能回答问题
- 还可以用来判断别的回答是否相关、是否 grounded

### 3. 定义第一个指标：Answer Relevance
这一项看的是：
- 用户问题
- 最终答案

两者之间是否相关。

如果用户问的是“怎样建立 AI 作品集”，结果回答跑去讲别的，就会得分低。

### 4. 定义第二个指标：Context Relevance
这一项看的是：
- 用户问题
- 被检索出来的上下文

之间是否相关。

因为一个 RAG 系统即使最终回答不错，也可能是：
- 检索上下文不够准
- 只是模型自己补全了答案

所以要单独看检索质量。

### 5. 定义第三个指标：Groundedness
这一项看的是：
- 最终回答
- 是否真正被上下文支持

也就是回答有没有“编”。

如果答案说了很多上下文里并没有的事实，那 groundedness 就会低。

### 6. 创建 `TruLlama` recorder
通过：
- `TruLlama(sentence_window_engine, feedbacks=[...])`

把三个反馈函数都挂到同一个 RAG 应用上。

### 7. 准备评估问题集
从 `eval_questions.txt` 读取问题，再补一条自己的问题。

### 8. 批量执行评估
循环对每个问题调用：
- `sentence_window_engine.query(question)`

TruLens 会自动记录并触发三项评估。

### 9. 查看结果
通过：
- `records`
- `feedback`
- `leaderboard`
- `dashboard`

来查看每条样本和整体均值表现。

## 整个工序可以简化成
准备一个可运行 RAG -> 配置 TruLens 和评估模型 -> 定义 Answer Relevance / Context Relevance / Groundedness 三个反馈函数 -> 批量跑问题 -> 汇总和可视化评估结果

## 这一节的关键收获
- RAG 评估不能只盯最终答案。
- 至少要分别看：
  - 答案和问题是否对题
  - 检索上下文是否相关
  - 答案是否被上下文支撑
- 这三项一起看，才比较接近一个完整的 RAG 质量画像。

