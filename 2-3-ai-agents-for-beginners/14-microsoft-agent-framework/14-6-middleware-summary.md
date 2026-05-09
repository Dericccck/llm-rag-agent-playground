# 14 Middleware 学习摘要

## 对应 Notebook
- `14-middleware.ipynb`

## 这一节在做什么
这一节是在前一个条件工作流的基础上，再加入一层：
- 中间件

它展示的是：
- 不改工具函数本身
- 不改工作流结构
- 只在工具执行前后插一层逻辑
- 就能改变整个工作流的结果

示例场景是优先会员酒店预订：
- 普通用户在巴黎没房，就走替代路线
- 优先会员在巴黎没房，中间件会把结果改成“有房”，于是改走预订路线

## 这里要分清三个角色

### `hotel_booking`
- 负责正常返回酒店可用性
- 它本身不知道优先会员逻辑

### `priority_check_middleware`
- 负责拦截工具结果
- 如果用户是优先会员且原结果没房，就覆盖结果

### 工作流本身
- 仍然还是条件工作流
- 只不过它吃到的是“被中间件修改后的结果”

## 这个 notebook 里的实现工序

### 1. 定义带 `priority_override` 的输出模型
在 `BookingCheckResult` 里多加了一个字段：
- `priority_override`

它用来标记：
- 这次可用性结果是不是被中间件改写过

### 2. 定义优先会员数据
代码里模拟了一份优先会员名单，例如：
- `alice@example.com`
- `bob@example.com`
- `priority_user`

还通过 `set_user()` 切换当前测试用户身份。

### 3. 定义原始酒店查询工具
`hotel_booking()` 和前一节类似，负责返回城市房态。

### 4. 定义中间件
这一步是整个 notebook 的核心。

`priority_check_middleware` 的流程大致是：

#### 第一步：拦截函数调用
拿到当前调用上下文。

#### 第二步：先执行原函数
通过：
- `await next(context)`

让原来的 `hotel_booking()` 正常跑完。

#### 第三步：检查原始结果
读取：
- `context.result`

看看是否是“无房”。

#### 第四步：根据会员身份决定是否覆盖
如果：
- 当前用户是优先会员
- 且原始结果是没房

就直接改写 `context.result`，把它变成“有房”。

### 5. 创建带中间件的 Agent
创建 `availability_agent` 时，不只是传工具，还传了：
- `middleware=[priority_check_middleware]`

这表示：
每次这个 Agent 调 `hotel_booking()`，都会先经过中间件。

### 6. 工作流保持不变
后面的工作流图其实和条件工作流几乎一样：
- 有房 -> booking_agent
- 没房 -> alternative_agent

区别只在于：
有些“没房”结果会在中间件层被改成“有房”。

### 7. 测试三种情况

#### 普通用户 + 巴黎
- 没房
- 无 override
- 走 alternative 分支

#### 优先用户 + 巴黎
- 原始结果没房
- 中间件 override 成有房
- 走 booking 分支

#### 优先用户 + 斯德哥尔摩
- 原始就有房
- 中间件不需要改
- 正常走 booking 分支

## 整个工序可以简化成
用户请求 -> `availability_agent` 调 `hotel_booking` -> 中间件拦截并检查结果 -> 必要时改写结果 -> 条件工作流根据改写后的结果路由 -> 输出最终结果

## 这一节的关键收获
- Middleware 的价值在于“横切逻辑注入”。
- 它适合实现：
  - VIP 特权
  - 审计日志
  - 安全检查
  - 缓存/重试
  - A/B 测试
- 最重要的是：你可以改行为，而不用改工作流图本身。

