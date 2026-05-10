# Lesson 3 Summary

## 功能概括
这个 notebook 用的是：
- Tavily 搜索 API
- DuckDuckGo + 网页抓取
- BeautifulSoup 解析 HTML
- Agentic Search 思路对比

它的作用是：
- 对比“普通搜索流程”和“面向 Agent 的搜索流程”
- 让你理解为什么专为 AI 设计的搜索接口更适合 Agent 工作流

## 对应 Notebook
- `Lesson_3_Student.ipynb`

## 这一节在做什么
这一节不是在搭 LangGraph 图，而是在补一个很关键的 Agent 能力背景：
- 搜索

它重点比较了两种做法：
- 常规搜索：搜链接，再抓网页，再抽文本
- Agentic Search：直接返回更适合 LLM 消费的结构化结果

## 这里要分清几个角色

### DuckDuckGo / `ddgs`
- 负责传统网页搜索
- 返回的是链接列表

### `requests` + `BeautifulSoup`
- 负责抓取网页并从 HTML 里抽正文

### Tavily
- 负责 Agentic Search
- 直接返回结构化搜索结果和简洁答案

### `qwen-max`（隐含服务对象）
- 虽然这节没把完整 Agent 接起来
- 但整个对比都是在说明：什么样的搜索结果更适合给 LLM 用

## 这个 notebook 里的实现工序

### 1. 先演示 Tavily 的直接搜索
通过：
- `client.search(..., include_answer=True)`

直接拿到：
- query
- answer
- results

这说明：
- 不需要自己抓网页
- API 已经帮你做了一次“面向 LLM 的整理”

### 2. 再演示传统搜索流程
先用 DuckDuckGo 搜索天气相关网页。

这个阶段拿到的只是：
- URL 列表

### 3. 再自己抓网页
通过：
- `requests.get`
- `BeautifulSoup`

拿网页 HTML。

### 4. 再从 HTML 提取文本
遍历标题和段落标签：
- `h1`
- `h2`
- `h3`
- `p`

再把结果清洗成更像纯文本的数据。

这一步展示了传统搜索链路的问题：
- 流程长
- 容易被网站格式影响
- 要自己处理异常和清洗逻辑

### 5. 再回到 Tavily 对比
用 Tavily 搜同类问题时，直接能拿到更干净的结果。

也就是把：
- 搜索
- 初步整理
- 结构化返回

合成成一个更适合 Agent 的 API。

## 整个工序可以简化成
常规搜索：用户问题 -> 搜索引擎返回链接 -> 程序抓网页 -> 解析 HTML -> 清洗文本 -> 再交给 LLM

Agentic Search：用户问题 -> Tavily 直接返回结构化内容/答案 -> 更快交给 LLM 或 Agent 使用

## 这一节的关键收获
- Agent 并不一定要自己“像浏览器一样工作”。
- 专为 Agent 设计的搜索服务能减少大量脏活。
- 这节的意义在于让你理解：Agent 的外部工具质量，会直接决定整个系统复杂度。

