# Lesson 5 Summary

## 功能概括
这个 notebook 用的是：
- LangGraph interrupt / resume
- `interrupt_before`
- `get_state` / `get_state_history`
- `update_state`
- time travel / branching
- 自定义 reducer 替换消息

它的作用是：
- 给 LangGraph Agent 加上 Human in the Loop
- 让你能在工具调用前暂停、检查状态、修改状态、回到过去重新分支执行

## 对应 Notebook
- `Lesson_5_Student.ipynb`

## 这一节在做什么
这一节是在讲 LangGraph 最强的一类能力之一：
- 可暂停
- 可恢复
- 可修改历史
- 可回放分支

也就是：
不只是“记住状态”
而是“把状态当成可操控对象”。

## 这里要分清几个角色

### `interrupt_before=["action"]`
- 负责让图在工具执行前自动暂停

### `get_state()`
- 负责查看当前状态快照

### `update_state()`
- 负责人工修改状态

### `get_state_history()`
- 负责查看完整历史快照链

### 自定义 `reduce_messages`
- 负责在消息更新时支持“替换同 ID 消息”，而不只是简单追加

## 这个 notebook 里的实现工序

### 1. 先定义更强的消息 reducer
前面课程里消息通常只是追加。

这一节改成了自定义 `reduce_messages`：
- 如果消息 ID 相同，就替换
- 如果消息 ID 不同，就追加

这一步很关键，因为后面你要修改某一条已有消息。

### 2. 编译图时设置中断点
通过：
- `interrupt_before=["action"]`

告诉 LangGraph：
- 在工具真正执行前停下来

这就是 HITL 的入口。

### 3. 先运行到中断点
用户发出问题后，图会先走到：
- `llm`

生成一个带工具调用的 AIMessage，但在执行工具前暂停。

### 4. 查看暂停时的当前状态
通过：
- `graph.get_state(thread)`

你能看到：
- 当前 messages
- 下一步节点 `next`
- 当前 checkpoint 配置

也就是说，此时 Agent 的“脑内状态”已经完全可见。

### 5. 继续执行
通过：
- `graph.invoke(None, thread)`

不传新输入，只是让图从暂停点继续。

这相当于人工点击“批准执行”。

### 6. 手动逐步审批
Notebook 还写了一个 while 循环：
- 每次暂停都先看状态
- 人工输入 `y`
- 才继续执行下一步

这模拟了真实的人类审批流。

### 7. 修改当前状态
这一步是本节最有意思的部分之一。

图停在 action 前时，你可以直接改：
- 工具调用参数

例如把：
- 查询 SF 天气

改成：
- 查询 Louisiana 天气

再用：
- `update_state(...)`

把修改后的状态写回去。

这样后续执行时，Agent 会沿着“被你修改后的世界线”继续跑。

### 8. 查看状态历史
通过：
- `get_state_history(thread)`

可以拿到整条状态链。

每个快照都像一个可回到的存档点。

### 9. Time Travel
挑一个旧状态的 config，再：
- `graph.invoke(None, old_config)`

就可以从过去某个点重新继续执行。

这就是时间旅行。

### 10. 回到过去后改历史，形成新分支
更进一步，你还可以：
- 选一个旧状态
- 改它的 tool call 或消息
- `update_state(...)`

于是系统不只是“回放过去”，而是能“从过去分叉出新未来”。

### 11. 手动注入 ToolMessage
Notebook 还演示了：
- 不真的跑工具
- 而是人工构造一个 ToolMessage 当作工具结果
- 直接插入状态里

这相当于：
- 模拟工具输出
- 或人工修正工具结果

### 12. 额外练习：用一个更简单的小图理解状态历史
最后又做了一个二节点小图：
- Node1 -> Node2 -> Node1 ...

专门让你练习：
- 看状态历史
- 回到过去
- 修改状态
- 用 `as_node` 指定从哪个节点继续推理

## 整个工序可以简化成
运行图到中断点 -> 查看状态 -> 人工决定继续 / 修改工具调用 / 注入消息 -> `update_state` 写回 -> 从当前或历史 checkpoint 继续执行 -> 必要时形成新分支

## 这一节的关键收获
- HITL 在 LangGraph 里不是简单弹个确认框，而是状态级控制。
- 状态可见、可改、可回放、可分叉，是 LangGraph 很强的一点。
- 这让 Agent 从“自动流程”升级成“可审计、可干预、可调试的工作流系统”。

