# 07 Planning Design 学习摘要

## 对应 Notebook
- `07-semantic-kernel.ipynb`

## 这一节在做什么
这一节是在做一个“规划型 Agent”。

它不是直接帮用户把旅行问题一步做完，而是先把大任务拆成多个子任务，再把每个子任务分配给合适的专业 Agent。

换句话说，这里重点不是执行，而是“先规划”。

## 这里要分清三个角色

### `qwen-max`
- 负责理解用户的大任务
- 负责把任务拆解成结构化子任务
- 负责决定每个子任务该交给哪个专业 Agent

### `TravelPlan` / `SubTask`
- 这是结构化输出的数据格式
- 不是模型，不是工具，而是“规划结果的标准模板”

### Planner Agent
- 负责输出任务分解方案
- 相当于一个总控调度器

## 这个 notebook 里的实现工序

### 1. 先定义结构化结果格式
代码里用 Pydantic 定义了两个类：

#### `SubTask`
表示一个子任务，里面至少包括：
- 分配给哪个 Agent
- 这个子任务要做什么

#### `TravelPlan`
表示整个规划结果，里面包括：
- 主任务
- 一组 `SubTask`

这一步的作用是：
不要让模型随便输出自然语言，而是强制它返回一个机器可解析的计划结构。

### 2. 定义可用 Agent 列表
在系统提示词里告诉 Planner：
你手下可用的 Agent 有哪些，例如：
- FlightBooking
- HotelBooking
- CarRental
- ActivitiesBooking
- DestinationInfo
- DefaultAgent

### 3. 配置结构化输出
这里的关键设置是：
- `OpenAIChatPromptExecutionSettings(response_format=TravelPlan)`

意思是：
模型输出必须符合 `TravelPlan` 这个结构。

### 4. 创建 Planner Agent
然后创建 `ChatCompletionAgent`，并把：
- 系统提示词
- 结构化输出约束

一起传进去。

### 5. 用户提出复杂需求
例如：
- 帮一个四口之家从新加坡去墨尔本做旅行规划

### 6. Agent 先做任务拆解
执行时流程是：
- 模型读取用户需求
- 理解这其实不是单一问题，而是多步骤问题
- 按预设角色清单拆分任务
- 输出 JSON 结构的规划结果

### 7. 再用 Pydantic 校验
拿到模型输出后，代码会再做一层验证：
- 如果格式合法，展示结构化计划
- 如果格式不合法，显示校验错误和原始输出

## 整个工序可以简化成
用户复杂需求 -> Planner Agent 读取任务 -> 按可用 Agent 类型拆分子任务 -> 输出结构化 JSON -> Pydantic 校验 -> 得到可执行计划

## 这一节的关键收获
- 复杂 Agent 系统经常要先规划，再执行。
- 结构化输出是让“模型想法”变成“程序可执行结果”的关键。
- 这类 notebook 非常适合理解 orchestrator / planner 角色。

