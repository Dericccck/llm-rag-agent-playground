# 11 Agentic Protocols 学习摘要

## 对应 Notebook
- `11-mcp.ipynb`
- `11-a2a.ipynb`

## 这一章整体在做什么
这一章重点不是某个具体旅行功能，而是在讲：
- Agent 如何标准化接外部服务
- Agent 如何标准化与其他 Agent 通信

所以这里分成两条线：
- MCP：让 Agent 接外部工具/服务
- A2A：让 Agent 和 Agent 之间协作

---

## 一、`11-mcp.ipynb` 在做什么
这个 notebook 用 Semantic Kernel 连接真实的 OpenBnB MCP Server，让 Agent 可以去搜真实 Airbnb 房源。

### 这里要分清三个角色

#### `qwen-max` / `gpt-4o-mini`
- 负责理解用户要找什么房源
- 负责决定调用哪个 MCP 工具
- 负责把结果整理成可读回答

#### `MCPStdioPlugin`
- 负责把 Semantic Kernel 和外部 MCP 服务连起来
- 通信方式是 stdio

#### `OpenBnB MCP Server`
- 负责真正提供 Airbnb 搜索能力
- 它才是“真实数据来源”

### MCP notebook 的实现工序

#### 1. 先配置模型服务
先把模型接好，作为 Agent 的大脑。

#### 2. 启动 MCP 服务
通过：
- `npx -y @openbnb/mcp-server-airbnb`

启动一个外部 MCP Server。

#### 3. 建立 MCP 插件连接
用：
- `MCPStdioPlugin`

把这个服务接入到 Semantic Kernel。

#### 4. 自动发现可用工具
连接成功后，Agent 可以看到 MCP 服务暴露出来的工具，比如：
- 搜索房源
- 看详情
- 查评论

#### 5. 用户发起搜索请求
例如：
- 在 Stockholm 给 2 个成人 1 个孩子找 Airbnb

#### 6. Agent 通过 MCP 调真实服务
执行时流程是：
- 用户提需求
- Agent 判断需要调用外部服务
- 通过 MCP 工具发起查询
- OpenBnB 返回真实房源数据
- Agent 整理结果输出

### MCP notebook 的工序可以简化成
用户请求 -> 模型判断需要外部工具 -> 通过 MCP 调 OpenBnB 服务 -> 返回真实房源数据 -> 模型整理为最终回答

### MCP notebook 的关键收获
- MCP 解决的是“怎么把外部服务标准化接进 Agent”。
- 这样 Agent 不需要为每个外部系统都单独写一套奇怪接口。

---

## 二、`11-a2a.ipynb` 在做什么
这个 notebook 用 A2A 协议搭了一个多代理旅行系统。

系统里至少有三类 Agent：
- 货币兑换 Agent
- 活动规划 Agent
- 旅行管理 Agent

### 这里要分清三个角色

#### 专业 Agent
- 各自只负责一个领域
- 比如汇率、活动安排

#### 旅行管理 Agent
- 负责协调其他专业 Agent
- 相当于 orchestrator

#### A2A 协议层
- 负责这些 Agent 之间的标准通信
- 让它们可以像服务一样互相调用

### A2A notebook 的实现工序

#### 1. 先定义业务能力
比如 `CurrencyPlugin` 会去调用 Frankfurter API，提供实时汇率。

#### 2. 把 Semantic Kernel Agent 包装成 A2A Executor
这里不是直接暴露原始 Agent，而是用：
- `AgentExecutor`

把它们包装成符合 A2A 协议的执行器。

#### 3. 为每个 Agent 定义 Agent Card
`AgentCard` 类似代理身份证，描述：
- 这个 Agent 是谁
- 有什么技能
- 在哪个地址
- 用什么协议通信

#### 4. 启动多个本地 A2A 服务
通过 Uvicorn / Starlette，把不同 Agent 分别跑在不同端口上。

#### 5. 用 A2AClient 调用这些代理
客户端会：
- 先读取 Agent Card
- 再按协议发消息
- 收集响应结果

#### 6. 测试协调型 Agent
例如用户说：
- 我要去东京
- 我要换汇
- 还想知道两天可以做什么

这时旅行管理 Agent 会负责拆分并协调：
- 汇率问题交给货币 Agent
- 行程推荐交给活动 Agent
- 最后整合成一个总回答

### A2A notebook 的工序可以简化成
用户复杂请求 -> 旅行管理 Agent 接收 -> 根据任务类型协调专业 Agent -> 各 Agent 返回结果 -> 管理 Agent 汇总 -> 输出综合回答

### A2A notebook 的关键收获
- A2A 解决的是“Agent 和 Agent 怎么标准通信、互相调用”。
- 每个 Agent 可以独立部署、独立复用、独立扩展。

---

## 这一章学完最该记住什么

### MCP
- 偏“Agent 接外部工具/外部服务”

### A2A
- 偏“Agent 和 Agent 之间协作”

### 合起来看
- MCP 解决对外连接
- A2A 解决内部协作

这两个协议放在一起，就是构建复杂 Agent 系统的两个基础方向。

