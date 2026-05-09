# 14 Concurrent 学习摘要

## 对应 Notebook
- `14-concurrent.ipynb`

## 这一节在做什么
这一节是在演示另一种常见编排方式：
- 并发编排

和顺序编排不同，它不是一个 Agent 做完再轮到下一个，而是让多个专业 Agent 同时处理同一个问题，再把结果汇总起来。

这个 notebook 的场景是旅行推荐：
- 一个 Agent 看景点
- 一个 Agent 看美食
- 一个 Agent 看历史文化

## 这里要分清三个角色

### `attractions_agent`
- 负责景点、活动、交通等建议

### `dining_agent`
- 负责当地美食、餐厅、饮食文化

### `history_agent`
- 负责历史背景、文化亮点、重要时期

### `ConcurrentBuilder`
- 负责把同一个输入分发给多个 Agent 并行运行
- 再把结果聚合回来

## 这个 notebook 里的实现工序

### 1. 先定义三类结构化输出
代码里定义了：
- `AttractionsRecommendation`
- `DiningRecommendation`
- `HistoryRecommendation`

这一步的作用是让三个 Agent 各自输出不同维度、但格式稳定的结果。

### 2. 配置模型客户端
通过 `OpenAIChatClient` 连接模型服务。

### 3. 创建三个专业 Agent

#### 景点 Agent
输出：
- 热门景点
- 推荐活动
- 最佳旅行时间
- 交通建议

#### 美食 Agent
输出：
- 当地菜系
- 必吃菜品
- 推荐餐厅
- 饮食礼仪

#### 历史 Agent
输出：
- 历史意义
- 文化亮点
- 重要历史时期
- 有趣事实

### 4. 构建并发工作流
通过：
- `ConcurrentBuilder().participants([...]).build()`

把三个 Agent 放进一个并发图里。

它的工作方式相当于：
- 一次用户输入
- 同时 fan-out 到 3 个 Agent
- 3 个 Agent 并行工作
- 再 fan-in 聚合结果

### 5. 用户提出旅行目的地
比如：
- 给我东京的完整旅行建议

### 6. 三个 Agent 同时处理
执行时大致流程是：
- 同一条用户请求被分发给三个 Agent
- 每个 Agent 只看自己专业领域
- 三份结果分别返回
- 聚合器把它们收拢成一个完整结果集

### 7. 性能对比
这个 notebook 还专门测了：
- 并发执行时间
- 顺序执行时间

目的就是让你看到：
当多个任务彼此独立时，并发编排通常更快。

## 整个工序可以简化成
用户提出目的地 -> 输入同时分发给景点/美食/历史 Agent -> 三者并行生成结果 -> 聚合输出完整旅行指南

## 这一节的关键收获
- 并发编排适合“多个子任务互不依赖”的场景。
- 它的核心结构是：
  - fan-out
  - parallel execution
  - fan-in
- 这类模式很适合做综合分析、报告、多维度推荐。

