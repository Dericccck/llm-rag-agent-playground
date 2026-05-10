# Lesson 6 Summary

## 功能概括
这个 notebook 用的是：
- 多节点 LangGraph 工作流
- 规划、研究、写作、反思、再研究循环
- `SqliteSaver` 持久化
- Tavily 搜索
- 结构化输出生成搜索 queries
- GUI 写作界面

它的作用是：
- 构建一个会自己规划、查资料、写草稿、反思修改的 Essay Writer Agent
- 展示 LangGraph 如何支撑一个真正复杂的多步骤生产型 Agent

## 对应 Notebook
- `Lesson_6_Student.ipynb`

## 这一节在做什么
这一节是在搭一个比较完整的 Agent 应用：
- 不是单轮问答
- 也不是单次工具调用
- 而是一整个写作工作流

这个 Agent 会：
- 先做写作大纲
- 再做资料搜索
- 写初稿
- 自己批改
- 再针对批评继续研究和修订

## 这里要分清几个角色

### `plan_node`
- 负责写作规划

### `research_plan_node`
- 负责围绕主题先搜资料

### `generation_node`
- 负责根据大纲和资料生成草稿

### `reflection_node`
- 负责像老师一样批改草稿

### `research_critique_node`
- 负责根据批评意见再搜补充资料

### `should_continue`
- 负责决定是否继续修订循环

### Tavily
- 负责给写作和修改提供外部资料

## 这个 notebook 里的实现工序

### 1. 定义 AgentState
状态里不再只有 messages，而是一个完整写作任务状态：
- `task`
- `plan`
- `draft`
- `critique`
- `content`
- `revision_number`
- `max_revisions`

这说明：
- 复杂 Agent 的状态不一定是聊天消息
- 也可以是结构化业务变量

### 2. 定义五种提示词
分别对应：
- 规划
- 写作
- 反思
- 为写作搜资料
- 为修订搜资料

这一步本质上是在给不同节点分配不同角色。

### 3. 定义结构化输出 `Queries`
研究节点不会随便输出文字，而是结构化地产生搜索 query 列表。

这让 Tavily 搜索能稳定执行。

### 4. 定义五个节点

#### `plan_node`
- 根据用户任务写一个文章提纲

#### `research_plan_node`
- 根据任务生成几个搜索 query
- 用 Tavily 搜索并把结果存进 `content`

#### `generation_node`
- 把 `task + plan + content` 组合起来生成草稿
- 同时递增修订次数

#### `reflection_node`
- 把当前 draft 交给“老师人格”模型批改

#### `research_critique_node`
- 根据 critique 再生成新的搜索 query
- 补充资料到 `content`

### 5. 定义循环条件
通过：
- `should_continue`

控制：
- 如果修订次数超限，就结束
- 否则继续 `reflect -> research_critique -> generate`

### 6. 构建图结构
整体流程大致是：

`planner -> research_plan -> generate`

然后从 `generate` 出来：
- 如果结束，就结束
- 如果继续，就走：
  - `reflect -> research_critique -> generate`

这就是一个真正的 revision loop。

### 7. 编译并运行图
加上 `SqliteSaver` 后，整个写作状态还能持久化保存。

### 8. 演示 GUI
最后还通过 helper 里的：
- `ewriter()`
- `writer_gui(...)`

把这套 Essay Writer 包成一个可交互界面。

这说明这个 notebook 不只是算法 demo，而是已经在往可用应用走。

## 整个工序可以简化成
用户给主题 -> `plan_node` 写提纲 -> `research_plan_node` 搜资料 -> `generation_node` 产出草稿 -> `reflection_node` 批改 -> `research_critique_node` 补资料 -> 再次生成 -> 直到达到最大修订次数

## 这一节的关键收获
- LangGraph 很适合这种多步骤、带循环、带状态变量的复杂 Agent。
- 复杂 Agent 不一定围绕聊天消息构建，也可以围绕业务状态构建。
- 这个 notebook 已经很接近一个实际应用原型了。

