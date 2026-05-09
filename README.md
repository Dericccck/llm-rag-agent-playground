# llm-rag-agent-playground

一个面向 LLM、RAG、Agent 的系统化学习代码仓库。内容覆盖 Python 入门、Prompt Engineering、RAG、Agentic RAG、LangChain、LangGraph、LlamaIndex，以及多种 Agent 框架实践。

这个仓库更像一份“学习实验场”而不是单一应用项目：大部分内容以 Jupyter Notebook 为主，适合按专题逐个运行、阅读和改写。

## README 里的 notebook 链接能点开吗？

可以。下面所有 notebook 名称都使用了相对路径 Markdown 链接，推到 GitHub 后点击就会直接跳转到对应文件。

## 仓库结构

- **0-AiPython 代码基础**：Python 与 AI 入门练习，重点在语法、数据结构、文件、包管理和 API 调用。
- **1-1 Generative AI for Everyone**：面向入门者的生成式 AI 课程练习，偏概念理解与简单实践。
- **1-2 ChatGPT Prompt Engineering for Developers**：经典提示词工程课程，覆盖提示原则、迭代、总结、推断、转换、扩展和聊天格式。
- **1-3 Safe and Reliable AI via Guardrails**：围绕 RAG 与聊天机器人安全性的守卫机制实验，包括幻觉、越界、PII 和竞品限制。
- **2-1 Retrieval Augmented Generation**：RAG 基础与扩展练习，覆盖提示增强、向量数据库、检索指标、分块、混合检索和系统观测。
- **2-2 Building and Evaluating Advanced RAG Applications**：高级 RAG 结构设计与评测，重点包括 pipeline、triad 指标、sentence window、auto-merging 和 reranking。
- **2-3 AI Agents for Beginners**：Agent 学习主线，覆盖框架选型、设计模式、工具调用、Agentic RAG、多代理、上下文、记忆、协议与生产化。
- **2-4 Building Agentic RAG with LlamaIndex**：用 LlamaIndex 系统学习 Agentic RAG，从路由、工具调用到长程规划、重试与评估。
- **3-1 LangChain for LLM Application Development**：LangChain 课程代码，既保留原版 notebook，也补了 modern 版本用于对照当前推荐写法。
- **3-2 AI Agents in LangGraph**：LangGraph 学习路径，覆盖 ReAct、组件、搜索、持久化、人机协同和写作型 Agent。

## Notebook 导航

下面按目录列出当前仓库中已追踪的每一个 notebook，并简要说明它是干嘛的。

### 0-AiPython 代码基础

Python 与 AI 入门练习，重点在语法、数据结构、文件、包管理和 API 调用。

- [1-Lesson_10.ipynb](0-AiPython代码/part1/1-Lesson_10.ipynb)：学习如何把重复逻辑封装成函数，并把函数用于数据处理。适合作为后续 LLM、RAG、Agent 实验前的函数基础补齐。
- [1-Lesson_4.ipynb](0-AiPython代码/part1/1-Lesson_4.ipynb)：Python 入门示例，练习运行第一个程序。重点是建立 notebook 环境下的最基础执行习惯。
- [1-Lesson_6.ipynb](0-AiPython代码/part1/1-Lesson_6.ipynb)：认识 Python 基础数据类型，如文本、整数和浮点数。后面很多 prompt 和数据处理都会用到这些概念。
- [1-Lesson_7.ipynb](0-AiPython代码/part1/1-Lesson_7.ipynb)：练习把文本输出与计算结果组合展示。适合理解字符串拼接、格式化输出和简单表达式。
- [1-Lesson_8.ipynb](0-AiPython代码/part1/1-Lesson_8.ipynb)：学习变量定义、赋值与基本使用方式。它是后续动态构造 prompt 的直接前置知识。
- [1-Lesson_9.ipynb](0-AiPython代码/part1/1-Lesson_9.ipynb)：演示如何用变量拼接提示词，构造更灵活的 LLM 输入。可以看作从 Python 基础过渡到 AI 应用的第一步。
- [2-Lesson_1.ipynb](0-AiPython代码/part2/2-Lesson_1.ipynb)：用 Python 和 AI 处理任务列表，建立自动化思维。重点是把“一个任务”扩展成“可批量处理的任务集合”。
- [2-Lesson_2.ipynb](0-AiPython代码/part2/2-Lesson_2.ipynb)：学习 for 循环，对一组任务或数据重复执行操作。后面批量评估和批量检索都会用到这类思维。
- [2-Lesson_3.ipynb](0-AiPython代码/part2/2-Lesson_3.ipynb)：使用字典组织任务及优先级，并结合 AI 做判断。适合理解结构化输入如何帮助模型更稳定地工作。
- [2-Lesson_4.ipynb](0-AiPython代码/part2/2-Lesson_4.ipynb)：结合列表、字典和 AI 做个性化食谱生成。重点是把多种数据结构组合成更真实的应用输入。
- [2-Lesson_5.ipynb](0-AiPython代码/part2/2-Lesson_5.ipynb)：学习布尔值与条件比较，为分支逻辑做准备。它是写规则判断和 guardrail 条件的最小基础。
- [2-Lesson_6.ipynb](0-AiPython代码/part2/2-Lesson_6.ipynb)：用条件判断帮助 AI 根据规则做不同决策。你会看到程序控制逻辑如何与模型输出配合。
- [2-Lesson_7.ipynb](0-AiPython代码/part2/2-Lesson_7.ipynb)：预告文件处理主题，连接到下一阶段的数据输入输出。适合作为从“内存中的变量”走向“外部数据”的过渡。
- [3-Lesson_1.ipynb](0-AiPython代码/part3/3-Lesson_1.ipynb)：学习在 Python 中读取、写入和操作本地文件。后续做 RAG 时，本地文档读入就是从这里开始。
- [3-Lesson_2.ipynb](0-AiPython代码/part3/3-Lesson_2.ipynb)：把自己的文本数据加载进 notebook 并交给 AI 处理。重点是把自有数据变成模型可消费的输入。
- [3-Lesson_3.ipynb](0-AiPython代码/part3/3-Lesson_3.ipynb)：读取文本日志并判断其是否与餐饮主题相关。适合理解简单文本分类和筛选流程。
- [3-Lesson_4.ipynb](0-AiPython代码/part3/3-Lesson_4.ipynb)：从文本中抽取餐厅名、招牌菜等结构化信息。它对应的是信息抽取类任务的最基础形态。
- [3-Lesson_5.ipynb](0-AiPython代码/part3/3-Lesson_5.ipynb)：学习读取 CSV 表格，并将结构化数据用于旅行规划。适合理解文本数据和表格数据的处理差异。
- [Lesson_6.ipynb](0-AiPython代码/part3/Lesson_6.ipynb)：把已有代码块重构成可复用函数。后面项目里拆工具、拆链路时都会复用这类做法。
- [Lesson_7.ipynb](0-AiPython代码/part3/Lesson_7.ipynb)：综合前面能力，批量生成多城市旅行路线。它更像一个小型综合实战。
- [Lesson_1.ipynb](0-AiPython代码/part4/Lesson_1.ipynb)：学习从本地 Python 文件导入并复用函数。适合理解 notebook 和独立脚本之间如何协同。
- [Lesson_2.ipynb](0-AiPython代码/part4/Lesson_2.ipynb)：使用 Python 内置包完成常见任务。重点是熟悉标准库思维，而不是所有事都从零写。
- [Lesson_3.ipynb](0-AiPython代码/part4/Lesson_3.ipynb)：体验第三方 Python 包的使用方式。它会帮助你进入真实项目的依赖使用习惯。
- [Lesson_4.ipynb](0-AiPython代码/part4/Lesson_4.ipynb)：学习用 pip 安装依赖包并管理环境。后续运行 LangChain、LlamaIndex、LangGraph 都会用到这一步。
- [Lesson_5.ipynb](0-AiPython代码/part4/Lesson_5.ipynb)：通过天气 API 获取网络数据。它是调用外部服务、处理返回结果的基础练习。
- [Lesson_6.ipynb](0-AiPython代码/part4/Lesson_6.ipynb)：调用 AI 模型 API，把 Python 与大模型接起来。可以视为所有后续 AI notebook 的共同前置。
- [Installing_Python.ipynb](0-AiPython代码/part4/installingPython/Installing_Python.ipynb)：可选环境准备指南，说明如何在本机安装 Python。适合给第一次在本地跑 notebook 的同学使用。

### 1-1 Generative AI for Everyone

面向入门者的生成式 AI 课程练习，偏概念理解与简单实践。
这一组 notebook 数量不多，但作用很明确：帮助你把“生成式 AI 是什么、能做什么”从概念层快速落到代码层和业务层。适合作为 `0-AiPython` 之后的第一组 AI 体验材料，也适合给第一次接触 LLM 应用的人做热身。

- [GENAI4E_Activity 1.ipynb](1-1-GenAIForEveryone代码/Week 2/GENAI4E_Activity 1.ipynb)：在代码里直接调用 LLM，理解提示词如何落到程序接口。它强调的是“概念到代码”的第一步连接。
- [GENAI4E_Activity2.ipynb](1-1-GenAIForEveryone代码/Week 2/GENAI4E_Activity2.ipynb)：构建一个简单的声誉监控系统，体验生成式 AI 的业务应用。适合感受模型在企业场景中的早期落地方式。

### 1-2 ChatGPT Prompt Engineering for Developers

经典提示词工程课程，覆盖提示原则、迭代、总结、推断、转换、扩展和聊天格式。
这一组更像是后面所有 LLM 应用的“通用基本功”。如果你后续会写 RAG、Agent、评测链路，那么这里学到的 prompt 设计、结构化要求、迭代修正方法，都会持续复用。建议不要只跑一遍，而是自己改 prompt 看输出变化。

- [l2-guidelines.ipynb](1-2-ChatGPTPromptEngineeringForDevelopers代码/l2-guidelines.ipynb)：提示词工程基础，讲清楚高质量 prompt 的原则与套路。适合作为后面所有 LLM 应用写 prompt 的通用起点。
- [l3-iterative-prompt-development.ipynb](1-2-ChatGPTPromptEngineeringForDevelopers代码/l3-iterative-prompt-development.ipynb)：通过迭代修改 prompt 改善输出质量。重点是学会观察输出缺陷并逐轮修正。
- [l4-summarizing.ipynb](1-2-ChatGPTPromptEngineeringForDevelopers代码/l4-summarizing.ipynb)：练习文本总结，控制输出角度和粒度。适合理解“同一段内容可以按不同目标总结”。
- [l5-inferring.ipynb](1-2-ChatGPTPromptEngineeringForDevelopers代码/l5-inferring.ipynb)：练习从评论或文本中做情感、主题和意图推断。它对应很多真实业务里的分类和判断任务。
- [l6-transforming.ipynb](1-2-ChatGPTPromptEngineeringForDevelopers代码/l6-transforming.ipynb)：练习翻译、改写、纠错、风格转换等文本变换任务。适合理解模型作为文本处理器的能力边界。
- [l7-expanding.ipynb](1-2-ChatGPTPromptEngineeringForDevelopers代码/l7-expanding.ipynb)：根据输入评论或上下文扩写为更完整的回复内容。重点是把“简短信号”变成“完整输出”。
- [l8-chatbot.ipynb](1-2-ChatGPTPromptEngineeringForDevelopers代码/l8-chatbot.ipynb)：学习聊天格式与多轮对话，构建基础 chatbot。它是进入 Agent 或多轮助手前的最小原型。

### 1-3 Safe and Reliable AI via Guardrails

围绕 RAG 与聊天机器人安全性的守卫机制实验，包括幻觉、越界、PII 和竞品限制。
这一组可以视为从“把模型跑起来”进入“把模型管起来”的第一步。它讨论的不是功能本身，而是当系统开始面对真实用户、真实知识库、真实业务限制时，应该如何控制输出风险。建议在基础 RAG 或 chatbot 有概念后再回来看，会更容易理解它解决的痛点。

- [Lesson_1.ipynb](1-3-SafeandReliableAIviaGuardrails/L1/Lesson_1.ipynb)：分析 RAG 应用常见失败模式，理解为什么需要 guardrails。它更多是在建立“问题空间”而不是马上写规则。
- [Lesson_3.ipynb](1-3-SafeandReliableAIviaGuardrails/L3/Lesson_3.ipynb)：从零构建第一个 guardrail，限制模型输出行为。重点是把约束做成可执行逻辑，而不是停留在 prompt 里。
- [test.ipynb](1-3-SafeandReliableAIviaGuardrails/L3/test.ipynb)：L3 守卫规则相关的测试 notebook，用于临时验证配置或实验代码。更适合作为辅助试验场而不是正式课程主线。
- [Lesson_4.ipynb](1-3-SafeandReliableAIviaGuardrails/L4/Lesson_4.ipynb)：使用 NLI 检测回答是否出现幻觉。它把“答得像不像真的”变成可判定任务。
- [Lesson_5.ipynb](1-3-SafeandReliableAIviaGuardrails/L5/Lesson_5.ipynb)：把幻觉检测 guardrail 接入聊天机器人流程。重点是从单点检测走向端到端接入。
- [Lesson_6.ipynb](1-3-SafeandReliableAIviaGuardrails/L6/Lesson_6.ipynb)：让 chatbot 保持在限定话题内，避免跑偏。适合理解主题约束和边界控制。
- [Lesson_7.ipynb](1-3-SafeandReliableAIviaGuardrails/L7/Lesson_7.ipynb)：检测并阻止 PII 等敏感信息泄露。它对应生产环境里非常典型的合规问题。
- [Lesson_8.ipynb](1-3-SafeandReliableAIviaGuardrails/L8/Lesson_8.ipynb)：限制模型提及竞争对手等不希望出现的内容。重点是把品牌或业务规则编码进聊天系统。

### 2-1 Retrieval Augmented Generation

RAG 基础与扩展练习，覆盖提示增强、向量数据库、检索指标、分块、混合检索和系统观测。
这一组是仓库里最重要的 RAG 入门主线之一。内容从 Python 预备、LLM 调用、向量数据库、embedding、chunking，一路推进到混合检索和观测评估，基本覆盖了一个可运行 RAG 系统从 0 到 1 的骨架。建议把它当成“RAG 基础课”来系统走完。

- [Advanced_Hybrid_Search_Scoring_and_Evaluation.ipynb](2-1-RetrievalAugmentedGeneration/Advanced_Hybrid_Search_Scoring_and_Evaluation.ipynb)：补强混合检索部分，研究分数融合、权重调优与检索效果评估。适合在已经理解基础向量检索后继续往效果优化走。
- [C1M2_Ungraded_Lab_1.ipynb](2-1-RetrievalAugmentedGeneration/Module2/ungraded_lab_1/C1M2_Ungraded_Lab_1.ipynb)：理解 embedding 向量如何把文本映射到可检索空间。它解释的是 RAG 里“为什么能搜到相近内容”。
- [C1M2_Ungraded_Lab_2.ipynb](2-1-RetrievalAugmentedGeneration/Module2/ungraded_lab_2/C1M2_Ungraded_Lab_2.ipynb)：学习检索指标，如相似度、召回与排序效果。重点是把“搜得好不好”量化出来。
- [C1M3_Ungraded_Lab_1.ipynb](2-1-RetrievalAugmentedGeneration/Module3/ungraded_lab_1/C1M3_Ungraded_Lab_1.ipynb)：熟悉 Weaviate API 及向量数据库基本用法。适合作为从理论转到向量库操作的第一步。
- [C1M3_Ungraded_Lab_2.ipynb](2-1-RetrievalAugmentedGeneration/Module3/ungraded_lab_2/C1M3_Ungraded_Lab_2.ipynb)：专门练习 chunking，把长文本切成更适合检索的小块。chunk 的质量会直接影响后面回答的质量。
- [C1M4_Ungraded_Lab_1.ipynb](2-1-RetrievalAugmentedGeneration/Module4/ungraded_lab_1/C1M4_Ungraded_Lab_1.ipynb)：探索 LLM 参数与对话上下文管理能力。它更像是 RAG 周边但很实用的模型行为实验。
- [C1M4_Ungraded_Lab_2.ipynb](2-1-RetrievalAugmentedGeneration/Module4/ungraded_lab_2/C1M4_Ungraded_Lab_2.ipynb)：练习 prompt engineering，优化 RAG 里的提问与回答过程。重点在于检索之后如何更好地组织生成。
- [C1M5_Ungraded_Lab_1.ipynb](2-1-RetrievalAugmentedGeneration/Module5/ungraded_lab_1/C1M5_Ungraded_Lab_1.ipynb)：用 Weaviate 与 Phoenix 跟踪、观测并评估 RAG 系统。适合从“能跑”走向“可观测、可排障”。
- [Vector_Database.ipynb](2-1-RetrievalAugmentedGeneration/Vector_Database.ipynb)：演示如何连接向量数据库、建集合并执行检索。它是整个 RAG 主线里非常核心的一份 notebook。
- [C1M1_Ungraded_Lab_1.ipynb](2-1-RetrievalAugmentedGeneration/module1/C1M1_Ungraded_Lab_1.ipynb)：可选 Python 预备实验，补齐后续 RAG 课程所需的基础语法。适合 Python 不熟但想直接进 RAG 的读者。
- [C1M1_Ungraded_Lab_2.ipynb](2-1-RetrievalAugmentedGeneration/module1/C1M1_Ungraded_Lab_2.ipynb)：练习基本 LLM 调用和简单的增强式 prompt。它对应的是进入完整 RAG 前的最小增强式问答。
- [Rag.ipynb](2-1-RetrievalAugmentedGeneration/module1/Rag.ipynb)：一个本地文档型 RAG 示例，支持把自有文档放进 `shared_data` 做检索问答。适合拿自己的资料快速改造成小型知识库。

### 2-2 Building and Evaluating Advanced RAG Applications

高级 RAG 结构设计与评测，重点包括 pipeline、triad 指标、sentence window、auto-merging 和 reranking。
如果说 `2-1` 解决的是“先把 RAG 搭出来”，那么这一组解决的就是“怎样把 RAG 做得更准、更稳、更可评估”。它更偏向中高级主题，适合在已经理解基本检索流程后，再去研究上下文组织方式、检索后处理和评测指标体系。

- [L1-Advanced_RAG_Pipeline.ipynb](2-2-BuildingAndEvaluatingAdvancedRAGApplications/L1/L1-Advanced_RAG_Pipeline.ipynb)：搭建高级 RAG pipeline，理解检索、合成与回答链路。重点是比基础 RAG 多出哪些结构化环节。
- [L2-RAG_Triad_of_metrics.ipynb](2-2-BuildingAndEvaluatingAdvancedRAGApplications/L2/L2-RAG_Triad_of_metrics.ipynb)：学习 RAG Triad 评测指标，评估回答质量、相关性与上下文匹配。它帮助你建立“评测先行”的习惯。
- [L3-Sentence_window_retrieval.ipynb](2-2-BuildingAndEvaluatingAdvancedRAGApplications/L3/L3-Sentence_window_retrieval.ipynb)：用 sentence window 提升检索上下文的完整性。适合理解“拿到一点上下文”与“拿到正确上下文窗口”的差别。
- [L4-Auto-merging_Retrieval.ipynb](2-2-BuildingAndEvaluatingAdvancedRAGApplications/L4/L4-Auto-merging_Retrieval.ipynb)：学习 auto-merging retrieval，把碎片化结果自动合并成更完整上下文。它解决的是长文档被切碎后语义不连贯的问题。
- [L5-Reranking_Tradeoffs_and_Evaluation.ipynb](2-2-BuildingAndEvaluatingAdvancedRAGApplications/L5/L5-Reranking_Tradeoffs_and_Evaluation.ipynb)：深入研究 reranking 的收益、代价、失败案例和评估方法。适合你开始关心系统效果而不只是功能完整时阅读。

### 2-3 AI Agents for Beginners

Agent 学习主线，覆盖框架选型、设计模式、工具调用、Agentic RAG、多代理、上下文、记忆、协议与生产化。
这是仓库里最完整的一条 Agent 学习线，范围也最大。它不只是在讲某个框架怎么用，而是在讲 Agent 能力是如何逐层长出来的：先有单 Agent，再有工具，再有 RAG，再有规划、多代理、记忆、协议、生产治理。如果你想系统理解“Agent 到底比普通 chatbot 多了什么”，这组内容值得完整过一遍。

- [01-semantic-kernel.ipynb](2-3-ai-agents-for-beginners/01-intro-to-ai-agents/01-semantic-kernel.ipynb)：用 Semantic Kernel 构建最基础的 Agent，作为整套课程起点。它强调的是 Agent 最小闭环。
- [02-autogen.ipynb](2-3-ai-agents-for-beginners/02-explore-agentic-frameworks/02-autogen.ipynb)：用 AutoGen 搭建基础 Agent，理解另一套主流框架。适合拿来和 Semantic Kernel 对照。
- [02-semantic-kernel.ipynb](2-3-ai-agents-for-beginners/02-explore-agentic-frameworks/02-semantic-kernel.ipynb)：继续用 Semantic Kernel 对照不同 Agent 框架的设计方式。你可以观察抽象层次和组件组织的差异。
- [03-python-agent-framework.ipynb](2-3-ai-agents-for-beginners/03-agentic-design-patterns/03-python-agent-framework.ipynb)：用 Python 版本演示常见 Agent 设计模式。更贴近本仓库后续大多数 notebook 的运行环境。
- [03-semantic-kernel.ipynb](2-3-ai-agents-for-beginners/03-agentic-design-patterns/03-semantic-kernel.ipynb)：用 Semantic Kernel 再实现一次 Agent 设计模式。重点在于模式本身，而不是某个框架 API。
- [04-autogen.ipynb](2-3-ai-agents-for-beginners/04-tool-use/04-autogen.ipynb)：在 AutoGen 中演示 Agent 如何调用外部工具。它是从“只会聊天”走向“能行动”的关键一步。
- [04-semantic-kernel-tool.ipynb](2-3-ai-agents-for-beginners/04-tool-use/04-semantic-kernel-tool.ipynb)：在 Semantic Kernel 中演示工具注册与调用。重点是理解函数描述如何影响工具选择。
- [05-autogen-chromadb.ipynb](2-3-ai-agents-for-beginners/05-agentic-rag/05-autogen-chromadb.ipynb)：使用 AutoGen + ChromaDB 实现 Agentic RAG。适合本地快速跑通“代理 + 检索”的组合。
- [05-semantic-kernel-chromadb.ipynb](2-3-ai-agents-for-beginners/05-agentic-rag/05-semantic-kernel-chromadb.ipynb)：用 Semantic Kernel + ChromaDB 实现本地可运行的 Agentic RAG。它更适合边看边改。
- [06-system-message-framework.ipynb](2-3-ai-agents-for-beginners/06-building-trustworthy-agents/06-system-message-framework.ipynb)：构建可复用的系统消息框架，提升多代理系统的一致性。适合理解 trustworthy agent 的提示层治理。
- [07-autogen.ipynb](2-3-ai-agents-for-beginners/07-planning-design/07-autogen.ipynb)：使用 AutoGen 演示规划型 Agent 的任务拆解与执行流程。重点是“先规划再执行”的模式。
- [07-semantic-kernel.ipynb](2-3-ai-agents-for-beginners/07-planning-design/07-semantic-kernel.ipynb)：使用 Semantic Kernel 演示规划式 Agent，并补充了通义千问调用对照。可以顺便观察不同模型的结构化输出差异。
- [08-autogen.ipynb](2-3-ai-agents-for-beginners/08-multi-agent/08-autogen.ipynb)：演示 AutoGen 框架下的多代理协作。它适合用来理解角色分工与消息传递。
- [08-semantic-kernel.ipynb](2-3-ai-agents-for-beginners/08-multi-agent/08-semantic-kernel.ipynb)：Semantic Kernel 多代理协作实验示例，偏框架能力了解与版本兼容说明。适合拿来判断框架成熟度和限制。
- [09-semantic-kernel.ipynb](2-3-ai-agents-for-beginners/09-metacognition/09-semantic-kernel.ipynb)：展示 Agent 的元认知能力，即自我监控、反思和调整策略。它体现的是更高阶的智能体行为。
- [10-expense_claim-demo.ipynb](2-3-ai-agents-for-beginners/10-ai-agents-production/10-expense_claim-demo.ipynb)：生产场景中的费用报销 Agent Demo，展示业务流程编排与审批链路。适合理解 Agent 不只是聊天，而是可嵌入业务系统。
- [10-semantic-kernel.ipynb](2-3-ai-agents-for-beginners/10-ai-agents-production/10-semantic-kernel.ipynb)：演示生产环境中的服务降级、故障转移与容错。重点是生产可靠性，而不是功能演示。
- [10_autogen_evaluation.ipynb](2-3-ai-agents-for-beginners/10-ai-agents-production/10_autogen_evaluation.ipynb)：结合 Langfuse 监控与评估 AutoGen 代理。适合从“能跑”进一步走向“能持续评估”。
- [11-a2a.ipynb](2-3-ai-agents-for-beginners/11-agentic-protocols/11-a2a.ipynb)：学习 Agent-to-Agent 协议，理解多代理之间的标准化通信。它把协作问题从“框架内部”扩展到“系统之间”。
- [11-mcp.ipynb](2-3-ai-agents-for-beginners/11-agentic-protocols/11-mcp.ipynb)：MCP 协议示例，说明如何让 Agent 通过工具协议访问外部能力。重点是外部工具和数据源的标准化接入。
- [12-chat_summarization.ipynb](2-3-ai-agents-for-beginners/12-context-engineering/12-chat_summarization.ipynb)：上下文工程示例，演示如何通过聊天摘要压缩长对话上下文。适合理解上下文长度受限时的处理策略。
- [13-agent-memory-chromadb.ipynb](2-3-ai-agents-for-beginners/13-agent-memory/13-agent-memory-chromadb.ipynb)：把 Agent memory 方案改写为本地 ChromaDB 版本，便于学习和运行。它更适合没有 Azure 环境的读者。
- [13-agent-memory.ipynb](2-3-ai-agents-for-beginners/13-agent-memory/13-agent-memory.ipynb)：原版 Azure AI Search 记忆方案，用来理解云端 Agent memory。适合与本地版做实现差异对照。
- [14-1-sequential.ipynb](2-3-ai-agents-for-beginners/14-microsoft-agent-framework/14-1-sequential.ipynb)：使用 Microsoft Agent Framework 演示顺序编排。重点在于明确多步流程中的串行控制。
- [14-2-concurrent.ipynb](2-3-ai-agents-for-beginners/14-microsoft-agent-framework/14-2-concurrent.ipynb)：使用 Microsoft Agent Framework 演示并发编排。适合理解多个子任务并行执行时的收益。
- [14-3-conditional-workflow.ipynb](2-3-ai-agents-for-beginners/14-microsoft-agent-framework/14-3-conditional-workflow.ipynb)：演示带条件分支的 Agent workflow。重点在“不同输入走不同链路”的流程控制。
- [14-4-handoff.ipynb](2-3-ai-agents-for-beginners/14-microsoft-agent-framework/14-4-handoff.ipynb)：演示不同专家代理之间的 handoff 交接。适合理解职责切换和上下文传递。
- [14-5-human-loop.ipynb](2-3-ai-agents-for-beginners/14-microsoft-agent-framework/14-5-human-loop.ipynb)：演示 Human-in-the-Loop，让关键步骤由人来确认。重点是把自动化和人工审核结合起来。
- [14-6-middleware.ipynb](2-3-ai-agents-for-beginners/14-microsoft-agent-framework/14-6-middleware.ipynb)：演示在 Agent workflow 中加入中间件层。它对应的是更工程化的扩展点设计。
- [15-advanced-memory-architectures.ipynb](2-3-ai-agents-for-beginners/15-advanced-memory/15-advanced-memory-architectures.ipynb)：补强高级记忆架构，讨论分层记忆、遗忘、冲突解决与评估。适合从“会存记忆”走向“会管理记忆”。

### 2-4 Building Agentic RAG with LlamaIndex

用 LlamaIndex 系统学习 Agentic RAG，从路由、工具调用到长程规划、重试与评估。
这一组比普通 RAG 更进一步，核心主题不是“检索到答案”，而是“让系统围绕检索做规划、选择、批判和重试”。它非常适合在你已经看过 `2-1` 和 `2-3` 之后，再来理解 Agentic RAG 为什么会成为一个独立主题。

- [L1_Router_Engine.ipynb](2-4-Building Agentic RAG with Llamaindex/Lesson_1/L1_Router_Engine.ipynb)：使用 Router Engine 在多个索引或查询引擎之间做路由选择。重点在于把“问什么问题去查哪里”自动化。
- [L2_Tool_Calling.ipynb](2-4-Building Agentic RAG with Llamaindex/Lesson_2/L2_Tool_Calling.ipynb)：演示 LlamaIndex Agent 如何接入工具调用，让检索与动作结合。适合理解 Agent 不只是查询，还能执行操作。
- [L3_Building_an_Agent_Reasoning_Loop.ipynb](2-4-Building Agentic RAG with Llamaindex/Lesson_3/L3_Building_an_Agent_Reasoning_Loop.ipynb)：构建 Agent 的 reasoning loop，让它能多轮思考、观察与执行。它是 Agentic RAG 进入“行动链”的关键。
- [L4_Building_a_Multi-Document_Agent.ipynb](2-4-Building Agentic RAG with Llamaindex/Lesson_4/L4_Building_a_Multi-Document_Agent.ipynb)：构建跨多文档问答的 Agent，能在多篇论文之间做检索与综合。重点是多源信息整合。
- [L5_Query_Planning_and_Long_Horizon_Agentic_RAG.ipynb](2-4-Building Agentic RAG with Llamaindex/Lesson_5/L5_Query_Planning_and_Long_Horizon_Agentic_RAG.ipynb)：补上 query planning 与长程任务拆解能力。适合看复杂问题如何被分解成多个子检索步骤。
- [L6_Retrieval_Critique_and_Agentic_Retry.ipynb](2-4-Building Agentic RAG with Llamaindex/Lesson_6/L6_Retrieval_Critique_and_Agentic_Retry.ipynb)：学习检索批判与失败后重试，让 Agentic RAG 更稳。重点是提升系统自我修正能力。
- [L7_Evaluating_Agentic_RAG_Systems.ipynb](2-4-Building Agentic RAG with Llamaindex/Lesson_7/L7_Evaluating_Agentic_RAG_Systems.ipynb)：系统评估 Agentic RAG 的流程、动作与最终回答质量。适合在系统已经复杂起来之后建立评测闭环。

### 3-1 LangChain for LLM Application Development

LangChain 课程代码，既保留原版 notebook，也补了 modern 版本用于对照当前推荐写法。
这一组的价值不只是“学 LangChain API”，更在于帮助你理解生态演进。仓库里同时保留了旧版课程 notebook 和较新的 modern 改写版本，所以很适合拿来观察：同一类能力在不同 LangChain 版本里是怎么表达的、哪些抽象被淘汰了、哪些方式更值得在新项目里继续使用。

- [L1-Model_prompt_parser.ipynb](3-1-LangChainForLLMApplicationDevelopment/L1-Model_prompt_parser.ipynb)：LangChain 入门，学习模型、Prompt Template 与输出解析器。它对应的是 LangChain 最常见的三件套。
- [L2-Memory-modern.ipynb](3-1-LangChainForLLMApplicationDevelopment/L2-Memory-modern.ipynb)：用 LangChain 1.x 推荐方式重写 memory 用法。适合避免直接照搬旧 API。
- [L2-Memory.ipynb](3-1-LangChainForLLMApplicationDevelopment/L2-Memory.ipynb)：原版 LangChain memory 示例。更适合作为理解历史写法和迁移背景的参考。
- [L3-Chains-modern.ipynb](3-1-LangChainForLLMApplicationDevelopment/L3-Chains-modern.ipynb)：用 LCEL 重写 Chains。重点是学习新版表达式式组合方式。
- [L3-Chains.ipynb](3-1-LangChainForLLMApplicationDevelopment/L3-Chains.ipynb)：原版 Chains API 示例。适合拿来和 modern 版逐格对照。
- [L4-QnA.ipynb](3-1-LangChainForLLMApplicationDevelopment/L4-QnA.ipynb)：旧版文档问答示例，仓库里也提供了更新的 RAG 写法。它更像历史版本参考。
- [L4-RAG-modern.ipynb](3-1-LangChainForLLMApplicationDevelopment/L4-RAG-modern.ipynb)：用更新的 LangChain 写法实现商品目录检索问答。适合直接借来做现代表达方式的模板。
- [L4-RAG.ipynb](3-1-LangChainForLLMApplicationDevelopment/L4-RAG.ipynb)：经典 RAG 文档问答示例。它更适合用来理解旧教程中的核心思路。
- [L5-Evaluation-modern.ipynb](3-1-LangChainForLLMApplicationDevelopment/L5-Evaluation-modern.ipynb)：用现代评测思路替代旧版 LangChain evaluation 组件。重点是把评测方式更新到当前生态。
- [L5-Evaluation.ipynb](3-1-LangChainForLLMApplicationDevelopment/L5-Evaluation.ipynb)：原版评测 notebook，并标记了已过时的做法。适合知道“以前怎么做”和“为什么现在不这么做”。
- [L6-Agents-modern.ipynb](3-1-LangChainForLLMApplicationDevelopment/L6-Agents-modern.ipynb)：用较新的 LangChain Agent 接口演示工具调用。它更贴近当前官方推荐实践。
- [L6-Agents.ipynb](3-1-LangChainForLLMApplicationDevelopment/L6-Agents.ipynb)：原版 LangChain Agents 示例。适合作为历史写法和现代写法之间的对照。
- [L6-Agents_new.ipynb](3-1-LangChainForLLMApplicationDevelopment/L6-Agents_new.ipynb)：新版 Agent notebook，作为旧版的替代实现。重点是给你一个更能直接复用的参考。

### 3-2 AI Agents in LangGraph

LangGraph 学习路径，覆盖 ReAct、组件、搜索、持久化、人机协同和写作型 Agent。
这一组更偏“图式编排”视角。它和前面的 Agent 课程不同，不是单纯讲工具调用或角色协作，而是强调状态机、节点、边、持久化、人机协同这些更接近工作流系统设计的能力。适合在已经理解基本 Agent 概念后，再把注意力转向更复杂的执行流控制。

- [Lesson_1_Student.ipynb](3-2-AI Agents in LangGraph/L1/Lesson_1_Student.ipynb)：从零实现一个简单的 ReAct Agent。适合理解“思考-行动-观察”循环的最小结构。
- [Lesson_2_Student.ipynb](3-2-AI Agents in LangGraph/L2/Lesson_2_Student.ipynb)：学习 LangGraph 的核心组件和图式编排方式。它是后续所有状态图设计的基础。
- [Lesson_3_Student.ipynb](3-2-AI Agents in LangGraph/L3/Lesson_3_Student.ipynb)：用 Agentic Search 方式组织搜索与推理。重点是把搜索过程显式纳入图状态。
- [Lesson_4_Student.ipynb](3-2-AI Agents in LangGraph/L4/Lesson_4_Student.ipynb)：学习 LangGraph 的持久化与流式输出能力。适合理解长流程任务如何保留状态并边生成边输出。
- [Lesson_5_Student.ipynb](3-2-AI Agents in LangGraph/L5/Lesson_5_Student.ipynb)：演示 Human in the Loop 工作流。重点是图流程里如何插入人工决策节点。
- [Lesson_6_Student.ipynb](3-2-AI Agents in LangGraph/L6/Lesson_6_Student.ipynb)：构建一个 Essay Writer 写作型 Agent。它综合展示了规划、写作、反馈和多轮迭代。
- [temp_test_gradio.ipynb](3-2-AI Agents in LangGraph/L6/temp_test_gradio.ipynb)：Lesson 6 的临时 Gradio 交互测试 notebook，用于界面联调。更适合作为实验辅助文件阅读。

## 推荐学习顺序

如果你是第一次系统接触这批内容，建议按下面这条路径走，而不是直接随机打开 notebook：

1. **Python 与最小 AI 调用阶段**
   先完成 `0-AiPython代码`，至少把变量、循环、字典、文件、函数、包管理、API 调用这些主题跑一遍。这里不是为了学语法本身，而是为了给后面的 RAG 和 Agent 实验补齐最小工程能力。
2. **LLM 基础认知与 Prompt 基本功**
   接着看 `1-1-GenAIForEveryone代码` 和 `1-2-ChatGPTPromptEngineeringForDevelopers代码`。前者帮助你快速建立“生成式 AI 能干什么”的直觉，后者帮助你建立“怎样更稳定地驱动模型”的方法论。
3. **安全与约束意识建立**
   然后看 `1-3-SafeandReliableAIviaGuardrails`。这一步建议不要太早跳过，因为后面无论你做 RAG 还是 Agent，都会遇到幻觉、越界和敏感信息泄露这类问题。
4. **RAG 基础搭建**
   主线从 `2-1-RetrievalAugmentedGeneration` 开始。这里建议按“module1 -> Module2 -> Module3 -> Module4 -> Module5”的顺序完整跑一遍，因为它对应的是一个 RAG 系统从输入、向量化、存储、生成到观测的逐层展开。
5. **RAG 效果优化与评测**
   在理解基础 RAG 后，进入 `2-2-BuildingAndEvaluatingAdvancedRAGApplications`。这时你会更容易理解 sentence window、auto-merging、reranking 和 triad metrics 到底是在修补哪些真实问题。
6. **Agent 基础到进阶主线**
   然后进入 `2-3-ai-agents-for-beginners`。比较推荐的阅读顺序是：`01 -> 04 -> 05 -> 07 -> 08 -> 09 -> 10 -> 11 -> 12 -> 13 -> 14 -> 15`。
   `02` 和 `03` 更适合作为框架横向对照材料插空阅读，不一定非得严格跟主线同步。
7. **Agentic RAG 专项深入**
   如果你已经理解了基础 RAG 和基础 Agent，再看 `2-4-Building Agentic RAG with Llamaindex`。这一组最适合拿来回答一个关键问题：为什么“会检索”不等于“会解决复杂问题”。
8. **框架实践与现代写法对照**
   最后看 `3-1-LangChainForLLMApplicationDevelopment` 和 `3-2-AI Agents in LangGraph`。这两组更像“框架专项训练”，适合在你已经知道核心概念之后，再去吸收不同生态的表达方式和工程组织方法。

## 使用建议

- 如果你的目标是“尽快做出一个本地可跑的小型 RAG 项目”，优先看 `0-* -> 1-2 -> 2-1 -> 2-2`。
- 如果你的目标是“系统理解 Agent”，优先看 `0-* -> 1-2 -> 1-3 -> 2-3 -> 2-4 -> 3-2`。
- 如果你的目标是“跟着框架学现代实现方式”，优先看 `2-*` 主线打底，再回到 `3-1` 和 `3-2`。
- 需要云服务的 notebook 已在仓库中尽量保留说明；如果某些示例依赖 Azure 等外部服务，可以优先阅读本地可运行版本或对照改写版本。
- 运行前优先查看各子目录下的 `requirements.txt`、`notebook-summary.md` 和相关说明文件。
