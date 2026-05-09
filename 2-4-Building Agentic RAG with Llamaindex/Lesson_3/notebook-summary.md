# Lesson 3 学习摘要

## 对应 Notebook
- `L3_Building_an_Agent_Reasoning_Loop.ipynb`

## 这一节在做什么
这一节是在讲：
- 不只是让模型调用一次工具
- 而是让 Agent 进入一个“思考 -> 调工具 -> 继续思考 -> 再回答”的推理循环

它本质上是在展示一个 LlamaIndex 里的函数调用 Agent，是怎么在多步推理里工作的。

## 这里要分清几个角色

### `gpt-4o-mini` / `qwen-max`
- 负责整个 reasoning loop 的大脑
- 决定何时调用工具、调用哪个工具、何时停止

### `vector_tool`
- 负责查文档细节

### `summary_tool`
- 负责查文档概览

### `FunctionAgent`
- 负责把“LLM + 工具 + 多轮推理”组织成一个真正的 Agent

### `Context`
- 负责保存会话状态
- 让后续问题能继承前面已经问过和查过的信息

## 这个 notebook 里的实现工序

### 1. 配置模型与 embedding
这里用了：
- function calling 模型
- 本地 `bge-small-en-v1.5`

embedding 依旧是为了文档工具提供向量能力。

### 2. 通过 `get_doc_tools` 生成两类工具
针对 `metagpt.pdf`，从工具工厂里拿到：
- `vector_tool`
- `summary_tool`

这说明 Lesson 1 和 Lesson 2 的检索能力，在这一节被复用成 Agent 的工具集。

### 3. 创建 `FunctionAgent`
通过：
- `FunctionAgent(tools=[vector_tool, summary_tool], llm=llm, verbose=True)`

把模型和工具组合成一个可执行 Agent。

### 4. 让 Agent 处理复杂问题
例如：
- 先问 MetaGPT 里的 agent roles
- 再问它们如何通信

这种问题往往不是一句话直接答，而是要先决定：
- 要不要查摘要
- 要不要查具体片段
- 多个工具结果如何拼起来

### 5. 读取工具调用结果
Notebook 里会检查：
- `response.tool_calls`

以及工具返回的：
- `source_nodes`

这样你能看到 Agent 实际用了哪些资料，而不是只看最终一句答案。

### 6. 演示上下文传递
这里用：
- `Context(agent)`

显式创建上下文。

然后连续两次提问：
- 第一次问用了哪些评估数据集
- 第二次问上面某个数据集的结果

第二个问题本身是不完整的，但因为共用了同一个 `ctx`，Agent 可以理解“above datasets”指的是上一轮内容。

### 7. 演示更底层的事件流调试
后半部分是这一节非常关键的点：
- 不是只拿最终结果
- 而是逐步看 Agent 在运行时到底发生了什么

代码里通过：
- `handler.stream_events()`

观察不同事件，例如：
- `AgentInput`
- `AgentOutput`
- `ToolCallResult`
- `AgentStream`

这让 Agent 推理过程变得可调试。

### 8. 演示异步执行与取消
最后还展示了：
- 不 `await` 直接启动 handler
- 查看任务是否完成
- 取消任务

说明这个 Agent loop 不只是同步黑盒，而是可控制的异步流程。

## 整个工序可以简化成
准备文档工具 -> 创建 `FunctionAgent` -> 用户提复杂问题 -> Agent 决定工具调用顺序 -> 工具返回证据 -> Agent 继续推理并输出结果 -> 通过 `Context` 保持多轮状态 -> 通过事件流调试每一步

## 这一节的关键收获
- 这一节真正讲的是“Agent loop”，不是单次 tool calling。
- `FunctionAgent` 让模型具备多步工具推理能力。
- `Context` 和事件流让这个过程既能连续，又能调试。

