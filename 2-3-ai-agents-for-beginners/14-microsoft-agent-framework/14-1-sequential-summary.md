# 14 Sequential 学习摘要

## 对应 Notebook
- `14-sequential.ipynb`

## 这一节在做什么
这一节是在用 Microsoft Agent Framework 演示最基础的一种多 Agent 编排方式：
- 顺序编排

也就是：
- 第一个 Agent 先产出结果
- 第二个 Agent 再基于第一个 Agent 的结果继续处理

这个 notebook 用的是旅行推荐场景：
- 前台 Agent 先推荐一个景点
- 礼宾 Agent 再对这个景点做专业评审和评分

## 这里要分清三个角色

### `front_desk_agent`
- 负责先给出一个城市景点推荐
- 输出内容包括景点名称、推荐原因、停留时长、最佳参观时间等

### `concierge_agent`
- 负责审核前台的推荐
- 给出热度评分、游客评分、优缺点、替代建议

### `SequentialBuilder`
- 负责把两个 Agent 串起来
- 保证信息按照固定顺序流动

## 这个 notebook 里的实现工序

### 1. 先定义结构化输出
代码里用 Pydantic 定义了两个输出模型：
- `AttractionRecommendation`
- `AttractionReview`

这一步的作用是：
- 前台 Agent 的输出有固定格式
- 礼宾 Agent 的输出也有固定格式
- 后续解析和展示更稳定

### 2. 配置模型客户端
通过 `OpenAIChatClient` 连接到模型服务。

这里模型是整个工作流的推理引擎，但真正的流程控制由框架负责。

### 3. 创建两个专业 Agent

#### 前台 Agent
负责：
- 给用户推荐一个城市里的代表性景点
- 偏重介绍与推荐

#### 礼宾 Agent
负责：
- 审查前台给出的景点
- 偏重质量控制和专业评价

### 4. 构建顺序工作流
通过：
- `SequentialBuilder().participants([front_desk_agent, concierge_agent]).build()`

把工作流搭起来。

它的执行顺序就是：
用户输入 -> 前台 Agent -> 礼宾 Agent

### 5. 用户发起请求
比如：
- 我想去某个城市看景点

### 6. 两个 Agent 顺序执行
执行时大致流程是：
- 用户问题先给前台 Agent
- 前台 Agent 生成结构化推荐
- 这个推荐作为上下文继续传给礼宾 Agent
- 礼宾 Agent 基于前一位的输出再做评分和审查

### 7. 最后汇总与展示
代码会把两个 Agent 的 JSON 响应分别解析出来，再以更易读的形式展示。

## 整个工序可以简化成
用户提出景点需求 -> 前台 Agent 生成推荐 -> 礼宾 Agent 审查推荐 -> 输出“推荐 + 评审”的组合结果

## 这一节的关键收获
- 顺序工作流适合“先产出，再审核，再增强”的模式。
- 每个 Agent 不一定都直接面向用户，也可以是前后工位关系。
- Microsoft Agent Framework 在这里展示的是最直接的 pipeline 编排思路。

