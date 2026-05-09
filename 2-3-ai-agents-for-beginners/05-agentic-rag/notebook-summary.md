# 05 Agentic RAG 学习摘要

## 对应 Notebook
- `05-semantic-kernel-chromadb.ipynb`

## 这一节在做什么
这一节是在讲：Agent 怎么接入 RAG。

也就是用户提问后，Agent 不是直接回答，而是先去知识库里检索相关资料，再结合这些资料生成回复。

## 这里要分清三个角色

### `qwen-max`
- 负责理解用户问题
- 负责决定调用哪些插件
- 负责把检索到的上下文整理成最终回答

### `ChromaDB`
- 负责存储旅行文档
- 负责做向量检索
- 它是知识库，不是大模型

### `PromptPlugin / WeatherInfoPlugin / DestinationsPlugin`
- `PromptPlugin`：负责从 ChromaDB 取回上下文并拼成增强提示
- `WeatherInfoPlugin`：负责提供气温信息
- `DestinationsPlugin`：负责提供旅行目的地详情

## 这个 notebook 里的 RAG 工序

### 1. 先准备知识库
代码先创建了一个 ChromaDB 集合：
- `travel_documents`

然后把一些旅行文档写进去，比如：
- Contoso 提供什么旅行服务
- 有什么保险保障
- 热门旅行目的地有哪些

这一步是在做“可检索知识底座”。

### 2. 定义检索插件
这里的重点插件是 `PromptPlugin`，主要做两件事：

#### `retrieve_context`
- 接收用户问题
- 去 ChromaDB 检索最相关的文档
- 把文档和 metadata 取回来

#### `build_augmented_prompt`
- 把“用户原问题 + 检索到的上下文”拼成一个增强提示
- 告诉模型：请基于这些上下文回答

### 3. 定义其他业务工具
除此之外还加了：
- `WeatherInfoPlugin`
- `DestinationsPlugin`

所以这个 Agent 不只是“查知识库”，还可以同时查温度和目的地信息。

### 4. 配置模型与 Agent
接着把 `qwen-max` 接到 Semantic Kernel，并创建 `TravelAgent`。

创建时特别强调一条规则：
- 回答旅行问题时先检索上下文

### 5. 用户发问
例如：
- Contoso 的保险包含什么
- 马尔代夫平均气温是多少
- 推荐一个寒冷目的地并说说温度

### 6. Agent 先检索，再回答
执行时大致流程是：
- 用户提问
- Agent 调用检索插件
- 插件去 ChromaDB 找相关文档
- 检索结果被拼成增强提示
- 必要时再结合天气或目的地插件
- 最后由 `qwen-max` 生成回答

## 整个工序可以简化成
用户问题 -> Agent 判断需要检索 -> `PromptPlugin` 去 ChromaDB 取上下文 -> 检索结果拼进提示词 -> 必要时调用其他业务工具 -> `qwen-max` 基于上下文回答

## 这一节的关键收获
- RAG 不是“把向量库接上就完了”，还需要把检索结果正确送回模型。
- 这个 notebook 体现的是 Agentic RAG：
  - Agent 负责决策
  - 向量库负责检索
  - 模型负责生成
- 一个 Agent 可以把“知识检索”和“业务工具调用”组合在同一次回答里。

