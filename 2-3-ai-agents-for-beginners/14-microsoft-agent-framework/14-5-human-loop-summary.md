# 14 Human Loop 学习摘要

## 对应 Notebook
- `14-human-loop.ipynb`

## 这一节在做什么
这一节是在讲：
- 某些工作流不能让 AI 全自动做完
- 中间必须停下来，等人类确认或补充信息

这就是 human-in-the-loop。

这个 notebook 是在条件工作流基础上，加了一段“人工确认是否查看替代酒店”的暂停流程。

## 这里要分清几个关键角色

### `availability_agent`
- 负责查酒店是否有房

### `confirmation_agent`
- 当没房时，负责生成一个要问用户的问题
- 例如：要不要看替代目的地

### `RequestInfoExecutor`
- 这是 HITL 的核心组件
- 负责暂停工作流并发出“需要人工输入”的事件

### `DecisionManager`
- 负责接收人的回答
- 决定后续走哪条分支

### `alternative_agent` / `cancellation_agent` / `booking_agent`
- 分别负责：
  - 推荐替代方案
  - 处理用户拒绝替代方案
  - 有房时直接推动预订

## 这个 notebook 里的实现工序

### 1. 定义结构化模型
除了条件工作流里的模型，还新增了两类：

#### `ConfirmationQuestion`
- 这是 `confirmation_agent` 输出给系统的问题格式

#### `HumanFeedbackRequest`
- 这是发给 `RequestInfoExecutor` 的请求负载
- 它不是给模型看的，而是给“人类输入环节”看的

### 2. 复用酒店查询工具
依然使用：
- `hotel_booking`

作为房态查询工具。

### 3. 定义四类条件函数

#### 前两类
- 是否有房
- 是否没房

#### 后两类
- 用户是否想看替代方案
- 用户是否拒绝替代方案

这意味着现在不仅看“业务状态”，还看“人类决策”。

### 4. 创建 `DecisionManager`
这是这个 notebook 的核心之一。

它会：
- 接收 `RequestResponse`
- 读取用户回答是 `yes` 还是 `no`
- 再构造下一跳消息

也就是说，人的输入不会直接跳到某个 Agent，而是先由决策管理器消化后再路由。

### 5. 定义 `prepare_human_request`
这里还专门加了一个转换 executor：
- 把 `confirmation_agent` 的 JSON 输出
- 转成 `HumanFeedbackRequest`

因为 Agent 的输出格式，和 `RequestInfoExecutor` 需要的请求类型，不是同一个东西。

### 6. 构建带暂停点的工作流
整体图大致是：

有房：
- `availability_agent -> booking_agent -> display_result`

没房：
- `availability_agent -> confirmation_agent -> prepare_human_request -> request_info_executor`

然后工作流暂停，等待人工输入。

人类回答后：
- `request_info_executor -> decision_manager`
- 用户说 yes -> `alternative_agent`
- 用户说 no -> `cancellation_agent`

### 7. 用事件驱动方式恢复工作流
执行时不会一次跑完，而是：

#### 第一次
- `workflow.run_stream(initial_request)`

#### 发现暂停点后
- 应用代码监听 `RequestInfoEvent`
- 收集人的输入

#### 继续执行
- `workflow.send_responses_streaming(pending_responses)`

这一步非常关键，它说明 HITL 工作流是“可暂停、可恢复”的。

### 8. 测试两种情况

#### 巴黎
- 无房
- 触发人工确认
- 根据人工回答决定是否给替代方案

#### 斯德哥尔摩
- 有房
- 直接走 booking 路径
- 完全绕过人工输入

## 整个工序可以简化成
用户请求酒店 -> `availability_agent` 查房 -> 没房时 `confirmation_agent` 生成提问 -> `RequestInfoExecutor` 暂停工作流 -> 人类输入 yes/no -> `DecisionManager` 路由 -> 替代方案或取消结果

## 这一节的关键收获
- HITL 的关键不是“问用户一句话”，而是“工作流能暂停并恢复”。
- `RequestInfoExecutor` 负责停下来，应用代码负责收集输入，`DecisionManager` 负责继续路由。
- 这种模式特别适合：
  - 审批
  - 高风险决策
  - 用户确认
  - 模糊场景澄清

