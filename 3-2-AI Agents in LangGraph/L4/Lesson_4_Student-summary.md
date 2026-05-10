# Lesson 4 Summary

## 功能概括
这个 notebook 用的是：
- LangGraph `StateGraph`
- `SqliteSaver` / `AsyncSqliteSaver`
- `thread_id` 会话隔离
- `stream` / `astream` / `astream_events`
- token 流式输出

它的作用是：
- 给 LangGraph Agent 加上状态持久化
- 让 Agent 能跨多轮对话记住上下文
- 同时展示同步/异步流式执行与 token streaming

## 对应 Notebook
- `Lesson_4_Student.ipynb`

## 这一节在做什么
这一节是在 Lesson 2 的 LangGraph Agent 基础上，加两个关键能力：
- Persistence
- Streaming

也就是：
- 不只是会工具调用
- 还要能记住历史，并且把执行过程流出来

## 这里要分清几个角色

### `AgentState`
- 保存消息历史

### `SqliteSaver`
- 负责同步方式的状态持久化

### `AsyncSqliteSaver`
- 负责异步方式的状态持久化

### `thread_id`
- 负责区分不同会话线程
- 相当于每个用户自己的上下文 ID

### LangGraph 图
- 仍然是 `llm -> action -> llm` 的 ReAct 结构

## 这个 notebook 里的实现工序

### 1. 复用 Lesson 2 的 Agent 结构
还是两个核心节点：
- `llm`
- `action`

并通过条件边判断是否需要工具调用。

### 2. 编译图时加入 checkpointer
和 Lesson 2 最大的区别是：
- `graph.compile(checkpointer=checkpointer)`

这一步后，图的状态就不只是存在内存里一瞬间，而是会被存下来。

### 3. 使用 `SqliteSaver`
先用同步版 SQLite checkpointer。

这里用的是内存数据库：
- `:memory:`

教学上方便，但 notebook 也明确说了：
- 生产环境应该改成真正持久化的数据库或文件

### 4. 用 `thread_id` 管理多轮会话
执行时传入：
- `configurable.thread_id`

这意味着：
- 同一个 `thread_id` 的消息会接着之前状态继续跑
- 不同 `thread_id` 会得到完全独立的对话状态

### 5. 演示跨轮记忆
比如先问：
- SF 天气

再问：
- LA 呢？

再问：
- 哪个更暖？

如果还是同一个 `thread_id`，Agent 就能利用前面已保存的结果。

### 6. 演示不同线程隔离
换一个新的 `thread_id` 后，再问“哪个更暖”，系统就没有之前上下文，因此会表现不同。

### 7. 演示同步流式输出
通过：
- `graph.stream(...)`

按节点输出状态变化。

### 8. 演示异步 token streaming
再切换到：
- `AsyncSqliteSaver`
- `graph.astream_events(...)`
- `graph.astream(..., stream_mode="messages")`

这样你既能看：
- 模型开始/结束事件
- 也能看逐 token 输出

### 9. 区分不同 `stream_mode`
Notebook 还解释了：
- `values`
- `updates`
- `messages`
- `custom`
- `debug`

这些模式分别适合：
- 看完整状态
- 看增量状态
- 看 token
- 看自定义事件
- 看调试细节

## 整个工序可以简化成
构建 LangGraph Agent -> 编译时加入 `SqliteSaver` -> 用 `thread_id` 区分和恢复会话 -> 多轮消息持续写入状态 -> 通过 `stream` / `astream` 把执行过程和 token 流出来

## 这一节的关键收获
- Persistence 是让 Agent 从“一次性执行”升级为“有会话记忆”的关键。
- `thread_id` 是会话管理核心。
- Streaming 让 Agent 不再是黑盒，也更适合做真实聊天 UI。

