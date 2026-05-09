# 08 Multi Agent 学习摘要

## 对应 Notebook
- `08-autogen.ipynb`

## 这一节在做什么
这一节是在用 AutoGen 演示多 Agent 协作。

场景很简单，但很典型：
- 一个 Agent 负责提出旅行建议
- 另一个 Agent 负责审查这个建议是不是够地道、够好
- 不够好就继续改，直到通过

## 这里要分清三个角色

### `planner_agent` / `frontdesk_agent`
- 负责先提出旅行建议
- 强调简洁、高效、一次只给一个建议

### `concierge_agent`
- 负责审稿
- 判断这个建议是不是足够本地化、非游客套路
- 如果满意就回复 `APPROVE`
- 不满意就给出改进方向

### `RoundRobinGroupChat`
- 负责让两个 Agent 轮流发言
- 管理整个协作流程

## 这个 notebook 里的实现工序

### 1. 配置模型客户端
代码里展示了两种模型接法：
- DashScope 的 `qwen-max`
- Azure/GitHub Inference 的 `gpt-4o-mini`

### 2. 创建两个 Agent

#### 前台旅行代理
负责：
- 生成旅行建议
- 回答要简洁
- 聚焦当前问题

#### 酒店礼宾代理
负责：
- 对前台建议进行评估
- 如果不够好，提出 refinement 方向
- 如果已经达标，直接说 `APPROVE`

### 3. 设置终止条件
这里用了：
- `TextMentionTermination("APPROVE")`

意思是：
只要某轮对话里出现 `APPROVE`，整个多 Agent 讨论就结束。

### 4. 用轮询团队组织协作
通过：
- `RoundRobinGroupChat`

让两个 Agent 按顺序轮流说话。

### 5. 执行任务
给团队一个初始任务：
- 规划一次巴黎旅行

然后流程会变成：
- 前台 Agent 先提建议
- 礼宾 Agent 审查
- 如果不够好，前台继续改
- 直到礼宾给出 `APPROVE`

## 整个工序可以简化成
用户任务 -> 规划 Agent 先给方案 -> 审核 Agent 评估方案 -> 不通过就继续优化 -> 通过后输出 `APPROVE` -> 对话结束

## 这一节的关键收获
- 多 Agent 的核心不是“多”，而是“分工”。
- 一个提案型 Agent 加一个审核型 Agent，是非常经典的协作模式。
- AutoGen 在这里主要体现的是：
  - 多 Agent 角色定义
  - 消息流转
  - 终止条件控制

