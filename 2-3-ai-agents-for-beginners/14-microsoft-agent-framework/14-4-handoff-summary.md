# 14 Handoff 学习摘要

## 对应 Notebook
- `14-handoff.ipynb`

## 这一节在做什么
这一节是在演示：
- 不是固定条件分支
- 也不是简单串行
- 而是由一个总入口 Agent 动态判断该把用户请求“交接”给哪个专家 Agent

这就是 handoff。

场景是旅行客服系统：
- 用户可能来订票
- 也可能来退款
- 也可能来确认行程

系统先由客服 Agent 接待，再交给正确的专家 Agent。

## 这里要分清四个角色

### `customer_support_agent`
- 总入口 Agent
- 负责初步判断用户需求属于哪类

### `booking_agent`
- 负责航班预订

### `disputes_agent`
- 负责退款、争议、账单问题

### `trip_check_agent`
- 负责旅行计划确认、行程核对

### `HandoffBuilder`
- 负责构建交接型工作流
- 让总入口 Agent 能把请求动态转交给专家

## 这个 notebook 里的实现工序

### 1. 定义各专家的结构化输出
代码里定义了：
- `FlightBookingResult`
- `DisputeResult`
- `TripCheckResult`

这样不同专家 Agent 的输出都能稳定解析。

### 2. 配置模型客户端
通过 `OpenAIChatClient` 连接模型服务。

### 3. 创建四个专业 Agent

#### 客服 Agent
负责：
- 理解用户意图
- 判断是订票、退款还是行程确认
- 触发 handoff

#### 订票 Agent
负责：
- 收集出发地、目的地、时间
- 返回订票确认 JSON

#### 争议 Agent
负责：
- 处理取消、退款、账单争议
- 返回退款处理结果

#### 行程核查 Agent
负责：
- 检查旅行计划是否确认
- 返回行程确认结果

### 4. 构建 handoff 工作流
通过：
- `HandoffBuilder`

设置：
- 参与者有哪些
- 谁是 coordinator
- coordinator 可以交接给谁

这里的 coordinator 就是：
- `customer_support_agent`

### 5. 运行流式工作流
这个 notebook 用的是：
- `workflow.run_stream()`

因为 handoff 过程可能不是一次问答就结束，而是一个多轮客服过程。

### 6. 处理事件与补充输入
代码里定义了事件处理函数，用来：
- 读取工作流状态
- 查看最终对话
- 处理需要用户继续补充的信息

这让整个 handoff 更像真实客服系统，而不是一次性请求。

### 7. 测试三类请求

#### 订票请求
- 客服 Agent 判断是 booking
- 交给 `booking_agent`

#### 退款请求
- 客服 Agent 判断是 dispute/refund
- 交给 `disputes_agent`

#### 行程确认请求
- 客服 Agent 判断是 trip check
- 交给 `trip_check_agent`

## 整个工序可以简化成
用户请求进入客服 Agent -> 客服 Agent 判断问题类型 -> handoff 给对应专家 Agent -> 专家 Agent 处理具体业务 -> 输出结构化结果

## 这一节的关键收获
- Handoff 的重点是“动态转交控制权”。
- 和条件工作流不同，这里更像“客服分诊”。
- 这类模式很适合：
  - 客服系统
  - 多部门协作
  - 多专业 Agent 平台

