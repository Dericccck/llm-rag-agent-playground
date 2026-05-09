# 04 Tool Use 学习摘要

## 对应 Notebook
- `04-semantic-kernel-tool.ipynb`

## 这一节在做什么
这一节是在专门演示：Agent 怎么“调用工具”。

也就是从“纯聊天”升级成“会去查数据、再回来回答”的 Agent。

## 这里要分清三个角色

### `qwen-max`
- 负责理解用户问题
- 负责判断应该调用哪个工具
- 负责把工具结果整理成自然语言回答

### `DestinationsPlugin`
- 负责真正提供业务数据
- 里面定义了多个函数，供 Agent 调用

### `FunctionChoiceBehavior`
- 负责控制模型的工具调用策略
- 比如：
  - 自动决定是否调用
  - 强制必须调用工具
  - 不允许调用工具

## 这个 notebook 里的实现工序

### 1. 定义插件
这里定义了一个 `DestinationsPlugin`，里面放了两个核心能力：
- `get_destinations()`：给出可选目的地
- `get_availability()`：查询某个目的地是否可用

这些函数通过：
- `@kernel_function`

暴露给 Agent，表示“这是可调用工具”。

### 2. 配置工具调用策略
这里引入了：
- `FunctionChoiceBehavior`

并设置成 `Required()`。

这表示：
模型在回答这类问题时，不是凭感觉直接编答案，而是必须先调用工具。

### 3. 配置模型
把 `qwen-max` 接到 Semantic Kernel 的聊天服务里。

### 4. 创建 Agent
创建 `TravelAgent`，告诉它：
- 你是旅行查询助手
- 你可以使用 `DestinationsPlugin`
- 你的回答要基于这些工具结果

### 5. 用户发起查询
例如用户会问：
- 有哪些目的地可用
- 巴塞罗那可用吗
- 有没有不在欧洲的目的地

### 6. Agent 调工具再回答
执行时的真实流程是：
- 用户发问
- `qwen-max` 判断需要哪个工具
- Agent 调用插件函数
- 工具返回结果
- `qwen-max` 再把结果整理成自然语言回答

## 整个工序可以简化成
用户问题 -> 模型判断需要哪个工具 -> 调用 `DestinationsPlugin` 里的函数 -> 工具返回原始结果 -> 模型把结果转成用户可读回答

## 这一节的关键收获
- Tool Use 是 Agent 和普通对话模型的重要分界线。
- 模型负责“决策和表达”，工具负责“提供外部能力”。
- 真正可用的 Agent，很多时候核心不是模型本身，而是它背后挂了哪些工具。

