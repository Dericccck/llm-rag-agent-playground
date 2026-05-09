# 06 Building Trustworthy Agents 学习摘要

## 对应 Notebook
- `06-system-message-framework.ipynb`

## 这一节在做什么
这一节不是在做一个完整业务 Agent，而是在做“系统提示词生成器”。

也就是：
先让一个大模型根据角色、公司、职责，帮你生成另一个 Agent 的系统消息。

为什么这和 trustworthy agent 有关？
因为很多 Agent 不稳定，不是工具不行，而是系统提示词太弱、太含糊、太短。

## 这里要分清三个角色

### `qwen-max` / `gpt-4o`
- 这里不是拿来当最终业务 Agent
- 而是拿来生成“系统提示词草稿”

### 输入参数
- `role`
- `company`
- `responsibility`

这些决定最终提示词会是什么样。

### 生成出来的 system prompt
- 才是后续真正给业务 Agent 使用的行为规范

## 这个 notebook 里的实现工序

### 1. 先定义目标岗位
代码里给出：
- 角色：`travel agent`
- 公司：`contoso travel`
- 职责：`booking flights`

### 2. 给大模型一个更高层的指令
系统消息大意是：
- 你是一个擅长为 AI Agent 编写系统提示词的专家
- 我会给你公司、角色、职责
- 你帮我生成一个结构化、描述清楚的 system prompt

这一步其实是一种 meta prompting：
让模型去写另一个模型该怎么工作。

### 3. 模型生成 system prompt
接着模型根据输入角色和职责，生成一份适合“旅行代理”的系统提示词。

### 4. 对比不同模型效果
这个 notebook 里同时保留了两种做法：
- 改写版：`qwen-max`
- 原版：Azure / `gpt-4o`

这样你可以直观看到：
- 不同模型生成系统提示词的细致程度和稳定性会有差异

## 整个工序可以简化成
给定角色/公司/职责 -> 大模型理解你要构建什么 Agent -> 生成系统提示词 -> 这份提示词可继续拿去构建真正业务 Agent

## 这一节的关键收获
- 一个 Agent 的可靠性，很大程度取决于它的 system prompt。
- 你完全可以先用一个模型，专门去生成另一个 Agent 的系统规则。
- Trustworthy 不只是“防越狱”，也包括：
  - 角色清晰
  - 职责明确
  - 行为边界稳定

