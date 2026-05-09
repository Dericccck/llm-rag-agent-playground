# 01 Intro To AI Agents 学习摘要

## 对应 Notebook
- `01-semantic-kernel.ipynb`

## 这一节在做什么
这一节是在搭一个最基础的 Agent 骨架，让你先看清楚：一个 Agent 最少需要哪些部件，怎么跑起来。

它实现的是一个简单的旅行助手：
- 用户提需求
- Agent 理解需求
- 必要时调用一个“目的地插件”
- 给出旅行建议

这一节不是重点讲复杂能力，而是先把 Agent 的最小闭环搭出来。

## 这里要分清三个角色

### `qwen-max`
- 负责聊天
- 负责理解用户要什么
- 负责决定怎么组织回答
- 如果工具可用，也可能决定调用工具

### `DestinationsPlugin`
- 负责提供旅行目的地数据
- 它不是模型，而是 Agent 可调用的业务工具

### `Semantic Kernel`
- 负责把模型、工具、Agent、线程组织起来
- 相当于整个 Agent 的运行框架

## 这个 notebook 里的实现工序

### 1. 先定义一个插件
先写了 `DestinationsPlugin`。

这个插件里放的是旅行目的地相关能力，比如：
- 提供目的地列表
- 给 Agent 一个可以外部调用的“信息源”

这一步的意思是：
不是让大模型凭空编，而是给它一个明确可用的工具入口。

### 2. 再连接大模型
代码里通过 `AsyncOpenAI` 连接到 DashScope 的兼容接口，使用的是 `qwen-max`。

然后再用：
- `OpenAIChatCompletion`

把这个模型封装成 Semantic Kernel 能调用的聊天服务。

### 3. 创建 Agent
接着创建：
- `ChatCompletionAgent`

在创建时会告诉它三件事：
- 你叫什么名字
- 你的职责是什么
- 你可以使用哪些插件

这一步之后，Agent 才真正成型。

### 4. 建立对话线程
代码里用：
- `ChatHistoryAgentThread`

来保存对话历史。

这样后面的消息就不是孤立的一问一答，而是一个连续会话。

### 5. 用户发起请求
比如用户说：
- `Plan me a sunny vacation`

然后 Agent 开始执行：
- 读取用户消息
- 结合系统提示词理解任务
- 必要时调用插件
- 生成最终回答

## 整个工序可以简化成
用户输入 -> `qwen-max` 理解请求 -> Semantic Kernel 组织 Agent 执行 -> 需要时调用 `DestinationsPlugin` -> 返回旅行建议

## 这一节的关键收获
- Agent 不是只有一个模型调用。
- 一个最小 Agent 通常至少包含：
  - 模型
  - 提示词
  - 工具
  - 对话线程
- 这一节本质是在打基础，后面所有 notebook 基本都在这个骨架上增加新能力。

