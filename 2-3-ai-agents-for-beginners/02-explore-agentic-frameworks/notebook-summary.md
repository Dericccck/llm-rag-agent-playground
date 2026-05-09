# 02 Explore Agentic Frameworks 学习摘要

## 对应 Notebook
- `02-semantic-kernel.ipynb`

## 这一节在做什么
这一节表面上还是旅行 Agent，但重点已经不是“旅行”本身，而是在熟悉 Agent Framework 的基本工作方式。

你可以把它理解成：
用一个简单业务场景，演示 Semantic Kernel 这种框架到底帮你做了哪些事。

## 这里要分清三个角色

### `qwen-max` 或 `gpt-4o-mini`
- 负责自然语言理解和回复
- 负责根据提示词决定回答方向
- 如果工具可用，也可能调用工具

### `DestinationsPlugin`
- 负责提供旅行目的地相关信息
- 它是工具层，不负责推理

### `Semantic Kernel`
- 负责把模型调用、插件注册、对话线程、Agent 实例组织起来
- 让 Agent 不只是一次普通 LLM 请求

## 这个 notebook 里的实现工序

### 1. 定义业务工具
先定义 `DestinationsPlugin`。

这个插件给 Agent 一个可用的数据能力，让它在回答旅行问题时不是完全空口生成。

### 2. 配置模型服务
然后配置大模型客户端，代码里支持两种思路：
- DashScope 上的 `qwen-max`
- GitHub/Azure Inference 上的 `gpt-4o-mini`

再通过 `OpenAIChatCompletion` 接到 Semantic Kernel。

### 3. 创建 Agent
创建 `TravelAgent`，同时设置：
- Agent 名称
- 系统提示词
- 可用插件

这一步定义的是 Agent 的“身份”和“能力边界”。

### 4. 建立多轮对话线程
代码里不是只发一条消息，而是准备多轮 `user_inputs`。

这样你可以观察：
- Agent 是否记得上一轮说了什么
- 用户不满意时，Agent 是否能继续沿着上下文回答

### 5. 执行对话
执行时流程是：
- 用户发送消息
- Agent 读取线程上下文
- 模型理解当前请求
- 必要时调用插件
- 返回结果并更新线程

## 整个工序可以简化成
用户输入 -> 模型理解请求 -> Semantic Kernel 读取上下文线程 -> 需要时调用目的地插件 -> 生成回答 -> 更新线程 -> 继续下一轮对话

## 这一节的关键收获
- Agent Framework 的核心价值，不是让模型“更聪明”，而是让工程组织更稳定。
- 它帮你管理：
  - 消息
  - 工具
  - 上下文
  - Agent 实例
- 这一节适合用来建立“框架视角”，为后面更复杂的模式做铺垫。

