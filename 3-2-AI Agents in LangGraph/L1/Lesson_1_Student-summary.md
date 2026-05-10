# Lesson 1 Summary

## 功能概括
这个 notebook 用的是：
- 手写 ReAct 循环
- OpenAI 兼容接口上的 `qwen-max`
- 自定义工具函数
- 正则解析 `Action`

它的作用是：
- 不依赖 LangGraph
- 先从最底层手写一个 “Thought -> Action -> Observation -> Answer” 的 Agent
- 帮你理解后面 LangGraph Agent 的原始工作原理

## 对应 Notebook
- `Lesson_1_Student.ipynb`

## 这一节在做什么
这一节是在从零手写一个最简单的 ReAct Agent。

重点不是框架，而是先让你理解：
- Agent 为什么会循环思考
- 工具调用是怎么插进对话流程里的
- “Observation” 为什么能驱动下一步推理

## 这里要分清几个角色

### `qwen-max`
- 负责生成 Thought / Action / Answer
- 不直接执行工具
- 只是告诉系统“下一步该调用哪个工具”

### `calculate`
- 负责数学计算

### `average_dog_weight`
- 负责返回狗的平均体重

### `Agent` 类
- 负责管理消息历史
- 负责调用模型
- 但最开始还不会自动循环执行工具

## 这个 notebook 里的实现工序

### 1. 先连接模型
通过 OpenAI 兼容接口连到 DashScope 的 `qwen-max`。

### 2. 写一个最小 Agent 类
这个类做的事情很简单：
- 保存 system prompt
- 保存消息历史
- 每次把所有消息发给模型
- 拿回文本回答

此时它还只是“会聊天”，还不是完整 Agent。

### 3. 用 prompt 规定 ReAct 协议
系统提示词里明确规定了输出结构：
- `Thought`
- `Action`
- `PAUSE`
- `Observation`
- 最终 `Answer`

也就是说：
ReAct 的行为模式并不是框架魔法，而是提示词先定出来的。

### 4. 定义外部工具
这里定义了两个可执行动作：
- `calculate`
- `average_dog_weight`

并用 `known_actions` 保存成一个工具映射表。

### 5. 手动演示一次 Agent 循环
先问：
- Toy Poodle 多重

模型会先输出：
- Thought
- Action: `average_dog_weight: Toy Poodle`

然后程序员手动执行工具，再把：
- `Observation: ...`

发回模型，模型才会得出最终答案。

### 6. 手动演示多步工具推理
再问两只狗的总重量。

这时流程会变成：
- 先查第一只狗
- 再查第二只狗
- 再调用计算
- 最后输出总结果

这一步说明：
一个 Agent 可以不是一次动作，而是多次“行动-观察”循环。

### 7. 加上自动循环
最后定义 `query()`：
- 自动解析模型返回中的 `Action`
- 自动执行对应工具
- 自动把结果写成 `Observation`
- 再喂回模型
- 直到模型不再输出 Action 为止

这时才变成一个真正能自己跑循环的简易 Agent。

## 整个工序可以简化成
用户提问 -> `qwen-max` 输出 Thought 和 Action -> 程序解析 Action -> 执行工具 -> 把结果作为 Observation 回传 -> 模型继续思考 -> 循环直到输出最终 Answer

## 这一节的关键收获
- Agent 的本质不是“更强的聊天”，而是“模型 + 工具 + 循环”。
- ReAct 模式可以不用框架，手写也能跑通。
- 后面 LangGraph 课程本质上是在把这套循环图结构化、可维护化。

