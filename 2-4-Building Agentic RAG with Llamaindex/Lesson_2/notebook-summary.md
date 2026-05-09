# Lesson 2 学习摘要

## 对应 Notebook
- `L2_Tool_Calling.ipynb`

## 这一节在做什么
这一节是在讲：
- LlamaIndex 里的 LLM 不只是回答问题
- 还可以根据问题决定要不要调用工具

这里演示了两类工具：
- 普通 Python 函数工具
- 文档检索工具

也就是把“计算能力”和“RAG 检索能力”都变成 LLM 可调用工具。

## 这里要分清几个角色

### `qwen-max`
- 负责理解用户问题
- 负责判断该调用哪个工具
- 负责把工具结果整理成最终回答

### `FunctionTool`
- 负责把普通 Python 函数包装成 LLM 可调用工具

### `QueryEngineTool`
- 负责把文档查询引擎包装成工具

### `bge-small-en-v1.5`
- 负责把文档块向量化
- 支撑向量检索

### 文档索引层
- `VectorStoreIndex`：查细节
- `SummaryIndex`：查概括

## 这个 notebook 里的实现工序

### 1. 先定义普通函数工具
代码里先写了两个简单函数：
- `add(x, y)`
- `mystery(x, y)`

然后用：
- `FunctionTool.from_defaults`

把它们变成 LLM 能调用的工具。

这一步是在说明：
只要是 Python 函数，也能纳入 Agent 工具体系。

### 2. 配置支持 function calling 的模型
这里的 `qwen-max` 被配置成：
- `is_function_calling_model=True`

这很关键，因为模型必须支持“先选工具再回答”的模式。

### 3. 先做一个简单工具调用实验
通过：
- `llm.predict_and_call(...)`

让模型自己决定是否调用 `add_tool` 或 `mystery_tool`。

### 4. 加载论文并做向量索引
接着把 `metagpt.pdf` 加载进来，并切成文本块，再建立：
- `VectorStoreIndex`

然后得到一个适合语义检索的查询引擎。

### 5. 加入元数据过滤
这里做了一个很重要的增强：
- 不只是向量检索
- 还可以按页码做 metadata filter

比如：
- 只搜第 2 页

这说明工具不仅能“查”，还能“按条件查”。

### 6. 定义自动检索工具 `vector_query`
这个函数接收：
- 查询文本
- 页码列表

内部流程是：
- 先根据页码生成 metadata filter
- 再用向量查询引擎检索相关片段
- 返回查询结果

然后再用 `FunctionTool` 把它暴露给 LLM。

也就是说，这里已经把“带过滤条件的 RAG”变成了一个工具。

### 7. 再加入摘要工具
后面又建了：
- `SummaryIndex`
- `summary_query_engine`
- `summary_tool`

于是模型现在手上同时有两类文档工具：
- 查指定页细节
- 查全文概括

### 8. 让模型自主选工具
最后通过：
- `predict_and_call([vector_query_tool, summary_tool], ...)`

让模型根据问题自己判断：
- 该查页码细节
- 还是该做整体摘要

## 整个工序可以简化成
定义 Python 函数工具 -> 验证基础 tool calling -> 加载论文并建索引 -> 把检索逻辑包装成 `vector_query_tool` -> 再加 `summary_tool` -> LLM 根据问题自主选择工具并回答

## 这一节的关键收获
- Tool Calling 不只是调业务 API，也可以调 RAG 检索链。
- 普通函数、检索引擎、摘要引擎都可以统一成“工具”。
- 一旦工具体系搭好，LLM 的角色就变成：
  - 理解问题
  - 选择工具
  - 组合最终答案

