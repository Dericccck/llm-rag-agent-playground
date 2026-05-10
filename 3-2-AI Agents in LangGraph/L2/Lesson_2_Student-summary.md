# Lesson 2 Summary

## 功能概括
这个 notebook 用的是：
- LangGraph `StateGraph`
- LangChain 消息对象
- 工具绑定 `bind_tools`
- 条件边和循环边
- Tavily 搜索工具

它的作用是：
- 把 Lesson 1 里手写的 ReAct Agent，改写成一个真正的 LangGraph 状态图
- 让 Agent 的思考、工具调用、状态更新都变成可视化图结构

## 对应 Notebook
- `Lesson_2_Student.ipynb`

## 这一节在做什么
这一节是在介绍 LangGraph 最核心的组件：
- 状态
- 节点
- 边
- 条件路由

并用一个搜索型 Agent 来演示图是怎么跑起来的。

## 这里要分清几个角色

### `AgentState`
- 这是图里流动的状态对象
- 这里主要保存 `messages`

### `llm` 节点
- 负责让模型思考
- 决定是否发起工具调用

### `action` 节点
- 负责真正执行工具

### `StateGraph`
- 负责定义整个工作流的图结构

### Tavily 工具
- 负责联网搜索外部信息

## 这个 notebook 里的实现工序

### 1. 先定义状态
这里用 `TypedDict` 定义 `AgentState`，里面最关键的是：
- `messages: Annotated[list[AnyMessage], operator.add]`

这意味着：
- 状态更新时不是覆盖消息
- 而是把新消息追加到旧消息后面

### 2. 初始化工具
用 Tavily 搜索作为 Agent 唯一工具。

### 3. 创建 Agent 类
这个类内部不是只保存 prompt，而是直接构建一张图。

### 4. 在图里定义两个节点

#### `llm`
- 调模型
- 看当前消息历史
- 输出 AIMessage，可能包含 tool calls

#### `action`
- 读取最后一条消息里的 tool calls
- 检查工具名是否存在
- 调用工具
- 把结果封成 ToolMessage 回写到状态里

### 5. 定义条件边
从 `llm` 节点出来后，代码会判断：
- 最后一条消息里有没有 `tool_calls`

如果有：
- 走到 `action`

如果没有：
- 直接结束

### 6. 定义循环边
工具执行完之后，一定回到 `llm`。

于是整个图就形成了：
- `llm -> action -> llm`

直到没有工具调用为止。

### 7. 编译图并运行
通过：
- `graph.compile()`

把定义好的结构变成可执行图。

之后用户发一个问题，比如天气问题，图就会自动：
- 思考
- 搜索
- 把结果再交给模型总结

## 整个工序可以简化成
用户消息进入状态 -> `llm` 节点决定是否需要工具 -> 如需要则走 `action` 节点调用 Tavily -> 工具结果回写状态 -> 回到 `llm` 继续思考 -> 没有工具调用时结束

## 这一节的关键收获
- LangGraph 把 Agent 循环显式变成了图结构。
- `StateGraph` 的核心思想是“状态驱动节点执行”。
- Lesson 1 的手写 ReAct，到这里就变成了可编排、可扩展的图式 Agent。

