# 14 Conditional Workflow 学习摘要

## 对应 Notebook
- `14-conditional-workflow.ipynb`

## 这一节在做什么
这一节是在讲：
- 工作流不是只能固定顺序跑
- 也可以根据前一步结果，走不同分支

这就是条件工作流。

这个 notebook 的例子是酒店预订：
- 先查某个城市有没有房间
- 如果有房间，就走“鼓励预订”路径
- 如果没房间，就走“推荐替代城市”路径

## 这里要分清三个角色

### `hotel_booking`
- 这是工具函数
- 负责返回某个城市有没有房间

### `availability_agent`
- 负责调用 `hotel_booking`
- 输出结构化的可用性结果

### 条件函数
- `has_availability_condition`
- `no_availability_condition`

它们负责检查上一步结果，然后决定工作流走哪条边。

## 这个 notebook 里的实现工序

### 1. 定义结构化输出模型
这里定义了三类结果：
- `BookingCheckResult`
- `AlternativeResult`
- `BookingConfirmation`

作用分别是：
- 可用性检查结果
- 替代城市建议
- 预订确认建议

### 2. 定义酒店查询工具
通过：
- `@ai_function`

把 `hotel_booking()` 暴露成 Agent 可调用工具。

这个函数内部其实是模拟逻辑：
- 某些城市有房
- 某些城市没房

### 3. 定义条件函数
这一步是条件工作流的核心。

代码会：
- 读取 `availability_agent` 的结构化 JSON 输出
- 判断 `has_availability` 是真还是假
- 返回 `True/False`

然后框架就用这个布尔值决定走哪条边。

### 4. 创建三个 Agent / 执行器

#### `availability_agent`
- 调工具查房

#### `alternative_agent`
- 没房时推荐别的城市

#### `booking_agent`
- 有房时推动用户预订

### 5. 创建显示执行器
还定义了一个自定义 executor：
- `display_result`

它负责把最终结果作为工作流输出抛出来。

### 6. 用 `WorkflowBuilder` 搭图
工作流结构大致是：

`availability_agent`
-> 如果没房，走 `alternative_agent`
-> 如果有房，走 `booking_agent`
-> 两条分支最终都到 `display_result`

### 7. 测试不同输入
例如：
- 巴黎：没房，走替代方案路径
- 斯德哥尔摩：有房，走预订路径

## 整个工序可以简化成
用户请求预订酒店 -> `availability_agent` 调工具查房 -> 条件函数检查结果 -> 有房走 booking 分支 -> 没房走 alternative 分支 -> 输出最终结果

## 这一节的关键收获
- 条件工作流的关键不是多 Agent，而是“边有条件”。
- 结构化输出很重要，因为条件函数要稳定读取字段来路由。
- 这是最典型的“决策树式 Agent Workflow”。

