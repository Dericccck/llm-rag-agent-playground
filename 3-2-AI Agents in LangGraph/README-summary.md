# AI Agents in LangGraph Summary

## 课程概括
这套 `3-2-AI Agents in LangGraph` 主要是在用一条逐步递进的路线，带你理解：
- Agent 的底层循环长什么样
- LangGraph 怎么把这种循环变成图
- 图一旦有了状态、持久化和中断，会变成多强的工作流系统
- 最后如何把复杂 Agent 做成一个完整应用

整体脉络基本是：
1. 先手写 ReAct
2. 再图化
3. 再讲搜索能力
4. 再讲持久化和流式
5. 再讲人类介入、状态修改、时间旅行
6. 最后做复杂写作 Agent 和可视化界面

## 各 Notebook 总览

### L1 - `Lesson_1_Student.ipynb`
功能：
- 手写 ReAct Agent
- 自定义工具
- Action/Observation 循环

作用：
- 从零理解 Agent 最基本的“思考 -> 行动 -> 观察 -> 再思考”机制。

总结文件：
[Lesson_1_Student-summary.md](/Users/a1-6/Desktop/AIAgent/code/3-2-AI%20Agents%20in%20LangGraph/L1/Lesson_1_Student-summary.md)

### L2 - `Lesson_2_Student.ipynb`
功能：
- LangGraph `StateGraph`
- 节点 / 边 / 条件边
- 工具调用 Agent

作用：
- 把手写 ReAct 变成 LangGraph 状态图。

总结文件：
[Lesson_2_Student-summary.md](/Users/a1-6/Desktop/AIAgent/code/3-2-AI%20Agents%20in%20LangGraph/L2/Lesson_2_Student-summary.md)

### L3 - `Lesson_3_Student.ipynb`
功能：
- Tavily Agentic Search
- DuckDuckGo + HTML 抓取对比

作用：
- 解释为什么面向 AI 的搜索 API 比传统“搜链接再抓网页”更适合 Agent。

总结文件：
[Lesson_3_Student-summary.md](/Users/a1-6/Desktop/AIAgent/code/3-2-AI%20Agents%20in%20LangGraph/L3/Lesson_3_Student-summary.md)

### L4 - `Lesson_4_Student.ipynb`
功能：
- 状态持久化
- `SqliteSaver` / `AsyncSqliteSaver`
- token streaming

作用：
- 让 LangGraph Agent 拥有会话记忆和流式输出能力。

总结文件：
[Lesson_4_Student-summary.md](/Users/a1-6/Desktop/AIAgent/code/3-2-AI%20Agents%20in%20LangGraph/L4/Lesson_4_Student-summary.md)

### L5 - `Lesson_5_Student.ipynb`
功能：
- Human in the Loop
- 中断 / 恢复
- 状态修改
- 时间旅行 / 分支执行

作用：
- 展示 LangGraph 如何把 Agent 工作流变成可审计、可干预、可回放的系统。

总结文件：
[Lesson_5_Student-summary.md](/Users/a1-6/Desktop/AIAgent/code/3-2-AI%20Agents%20in%20LangGraph/L5/Lesson_5_Student-summary.md)

### L6 - `Lesson_6_Student.ipynb`
功能：
- 多节点写作工作流
- 规划、研究、写作、反思、修订循环
- GUI 写作界面

作用：
- 构建一个真正复杂的 Essay Writer Agent，展示 LangGraph 的应用级工作流能力。

总结文件：
[Lesson_6_Student-summary.md](/Users/a1-6/Desktop/AIAgent/code/3-2-AI%20Agents%20in%20LangGraph/L6/Lesson_6_Student-summary.md)

### L6 - `temp_test_gradio.ipynb`
功能：
- Gradio 调试面板
- 节点级暂停
- 状态查看与修改
- 线程切换

作用：
- 把 Essay Writer 图做成一个可交互的 Agent 调试/控制界面。

总结文件：
[temp_test_gradio-summary.md](/Users/a1-6/Desktop/AIAgent/code/3-2-AI%20Agents%20in%20LangGraph/L6/temp_test_gradio-summary.md)

## 这套课学完应该记住什么
- LangGraph 的核心不是“多一个 Agent 框架”，而是“把 Agent 显式建模成状态图”。
- 一旦状态图建立起来，就自然能支持：
  - 工具调用
  - 条件路由
  - 持久化
  - 流式执行
  - Human in the Loop
  - 时间旅行和状态编辑
- 从 Lesson 1 到 Lesson 6，本质上是在一步步把“一个会回答问题的 Agent”升级成“一个可控的 Agent 工作流系统”。

