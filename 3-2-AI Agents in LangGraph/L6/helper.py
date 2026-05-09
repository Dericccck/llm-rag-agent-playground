# 导入警告模块，用于过滤特定警告信息
import warnings
# 忽略与Tqdm相关的警告（Tqdm是进度条库）
warnings.filterwarnings("ignore", message=".*TqdmWarning.*")
# 导入环境变量管理工具，用于加载 .env 文件中的 API 密钥等配置
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量（如 API 密钥等）
_ = load_dotenv()

# 导入 LangGraph 的核心组件 StateGraph 用于构建状态机
from langgraph.graph import StateGraph, END
# 导入类型注解相关工具
from typing import TypedDict, Annotated, List
import operator  # 导入运算符模块，用于状态更新操作
# 导入 SQLite 检查点保存器，用于保存和恢复对话状态
from langgraph.checkpoint.sqlite import SqliteSaver
# 导入 LangChain 的消息类型，用于构建对话历史
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, AIMessage, ChatMessage
from langchain_community.chat_models.tongyi import ChatTongyi
# 导入 Pydantic 模型，用于结构化输出
from pydantic import BaseModel
# 导入 Tavily 搜索客户端，用于获取实时网络信息
from tavily import TavilyClient
import os  # 导入操作系统接口模块
import sqlite3  # 导入 SQLite 数据库模块

class AgentState(TypedDict):
    """定义代理状态类型，使用 TypedDict 确保类型安全
    
    这个类定义了论文写作过程中需要跟踪的所有状态变量。
    TypedDict 是一种类型提示，它确保我们在使用状态字典时不会出错。
    """
    task: str  # 用户请求的论文主题
    lnode: str  # 刚执行完的节点的节点名称（用于界面显示）
    plan: str  # 论文大纲/计划
    draft: str  # 论文草稿
    critique: str  # 对草稿的批评意见
    content: List[str]  # 研究收集的内容列表
    queries: List[str]  # 搜索查询列表
    revision_number: int  # 当前修订次数
    max_revisions: int  # 最大允许修订次数
    count: Annotated[int, operator.add]  # 计数器，使用 operator.add 表示它会累加


class Queries(BaseModel):
    """定义查询模型，确保输出是包含查询列表的对象
    
    这个类用于结构化输出，让模型返回符合特定格式的查询列表。
    """
    queries: List[str]
    
class ewriter():
    """论文写作者类，封装了整个论文写作流程
    - 这是一个"状态机"，像自动售货机一样按步骤处理任务
    - 每个步骤（节点）只做一件事，完成后传递结果给下一步
    - 使用LangGraph框架管理复杂的工作流程
    """
    def __init__(self):
        """初始化论文写作代理
        - 所有准备工作都在这里完成
        - 模型是"大脑"，提示词是"操作手册"，状态图是"工作流程图"
        """
        self.model = ChatTongyi(
            model="qwen-max",  # 或其他通义千问模型
            dashscope_api_key=os.getenv("DASHSCOPE_API_KEY"),  # 通义千问 API key
            temperature=0.1, 
            streaming=True
        )

        # 您是一位经验丰富的写手，任务是撰写一篇论文的高级提纲。
        # 请根据用户提供的主题撰写一份提纲。提纲应包含文章的概要以及各部分相关的注释或说明。
        self.PLAN_PROMPT = ("You are an expert writer tasked with writing a high level outline of a short 3 paragraph essay. "
                            "Write such an outline for the user provided topic. Give the three main headers of an outline of "
                             "the essay along with any relevant notes or instructions for the sections. ")
        # 你是一名论文助教，任务是撰写优秀的五段式论文。
        # 根据用户的要求和初始提纲，生成尽可能最好的论文。
        # 如果用户提出批评意见，请回复修改后的版本。
        # 请根据需要使用以下所有信息：
        self.WRITER_PROMPT = ("You are an essay assistant tasked with writing excellent 3 paragraph essays. "
                              "Generate the best essay possible for the user's request and the initial outline. "
                              "If the user provides critique, respond with a revised version of your previous attempts. "
                              "Utilize all the information below as needed: \n"
                              "------\n"
                              "{content}")
        # 你是一名研究员，负责提供撰写以下论文所需的信息。
        # 请生成一份搜索查询列表，以收集所有相关信息。
        # 最多只能生成 3 个查询。
        self.RESEARCH_PLAN_PROMPT = ("You are a researcher charged with providing information that can "
                                     "be used when writing the following essay. Generate a list of search "
                                     "queries that will gather "
                                     "any relevant information. Only generate 3 queries max.")
        # 您是一位老师，正在批改一篇三段式作文。
        # 请对这篇作文进行点评并提出修改建议。
        # 建议需详细阐述，包括对文章长度、深度、风格等方面的要求。
        self.REFLECTION_PROMPT = ("You are a teacher grading an 3 paragraph essay submission. "
                                  "Generate critique and recommendations for the user's submission. "
                                  "Provide detailed recommendations, including requests for length, depth, style, etc.")
        # 您是一名研究员，负责提供信息，以便在进行任何所需的修改时使用（如下所述）。
        # 请生成一个搜索查询列表，以收集所有相关信息。最多只能生成 2 个查询。
        self.RESEARCH_CRITIQUE_PROMPT = ("You are a researcher charged with providing information that can "
                                         "be used when making any requested revisions (as outlined below). "
                                         "Generate a list of search queries that will gather any relevant information. "
                                         "Only generate 2 queries max.")
        
        # 初始化Tavily搜索客户端（获取实时网络信息）
        # Tavily就像AI的"搜索引擎"，能获取最新资料
        self.tavily = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

        # 创建状态图构建器（工作流程的"画布"）
        builder = StateGraph(AgentState)

        # 添加工作流程节点（每个节点是一个步骤）
        builder.add_node("planner", self.plan_node)  # 大纲生成站
        builder.add_node("research_plan", self.research_plan_node)  # 研究计划站
        builder.add_node("generate", self.generation_node)  # 论文生成站
        builder.add_node("reflect", self.reflection_node)  # 批改反馈站
        builder.add_node("research_critique", self.research_critique_node)  # 研究修改站
        
        # 设置工作流程起点（从"planner"开始）
        builder.set_entry_point("planner")  

        # 添加边
        # 添加条件边（智能判断下一步）
        builder.add_conditional_edges(
            "generate",  # 从"generate"节点出发
            self.should_continue,  # 用这个方法判断
            {END: END, "reflect": "reflect"}  # 如果达到最大修改次数就结束，否则去批改
        )
        # 添加固定边
        builder.add_edge("planner", "research_plan")  # 大纲 → 研究
        builder.add_edge("research_plan", "generate")  # 研究 → 生成
        builder.add_edge("reflect", "research_critique")  # 批改 → 研究修改
        builder.add_edge("research_critique", "generate")  # 研究修改 → 生成
        
        # 创建内存检查点（保存工作进度）
        memory = SqliteSaver(conn=sqlite3.connect(":memory:", check_same_thread=False))
        # 编译最终工作流程图
        # interrupt_after是设置断点，在哪些节点后面设置断点，设置断点后，运行完列表里的步骤后会暂停
        self.graph = builder.compile(
            checkpointer=memory,
            interrupt_after=['planner', 'generate', 'reflect', 'research_plan', 'research_critique']
        )


    def plan_node(self, state: AgentState):
        """大纲生成节点
        输入：当前状态（包含用户主题）
        输出：生成的大纲 + 状态更新
        
        - 这个节点只负责生成论文大纲
        - 使用SYSTEM消息设定角色，HUMAN消息传递主题
        - 返回的字典会自动更新到状态中
        """
        messages = [
            SystemMessage(content=self.PLAN_PROMPT), 
            HumanMessage(content=state['task'])
        ]
        # 调用大模型生成大纲
        response = self.model.invoke(messages)
        # 返回需要更新的状态字段
        # 注意：只返回变化的部分！其他状态保持不变
        return {
            "plan": response.content,  # 保存生成的大纲
            "lnode": "planner",  # 记录最后执行的节点
            "count": 1,  # 触发计数器+1（Annotated机制）
        }
    def research_plan_node(self, state: AgentState):
        """研究计划节点
        输入：当前状态（包含主题和大纲）
        输出：搜索结果 + 状态更新
        
        - with_structured_output：强制AI返回特定格式数据
        """
        # 让AI生成搜索查询问题列表（结构化输出）
        queries = self.model.with_structured_output(Queries).invoke([
            SystemMessage(content=self.RESEARCH_PLAN_PROMPT),
            HumanMessage(content=state['task'])
        ])

        # 如果queries为None，则创建一个空的Queries对象
        if queries is None:
            queries = Queries(queries=[])
        # 获取之前的content内容，content是研究收集的内容列表，是genenrate节点需要的信息
        content = state.get('content', [])  # add to content
        # 循环问题列表，对每个问题进行网络搜索并将搜索结果放入content中
        for q in queries.queries:
            response = self.tavily.search(query=q, max_results=2)
            for r in response['results']:
                content.append(r['content'])
        return {
            "content": content,  # 更新研究内容
            "queries": queries.queries,  # 保存使用的查询
            "lnode": "research_plan",
            "count": 1,
        }
    def generation_node(self, state: AgentState):
        """论文生成节点
        输入：当前状态（包含大纲和研究内容）
        输出：生成的草稿 + 状态更新
        
        - 这里把研究内容拼接成提示词
        - revision_number控制修改次数
        """
        # 将研究内容合并成字符串
        content = "\n\n".join(state['content'] or [])
        # # 构建用户消息（包含主题和大纲）
        user_message = HumanMessage(
            content=f"{state['task']}\n\nHere is my plan:\n\n{state['plan']}")
        messages = [
            SystemMessage(
                content=self.WRITER_PROMPT.format(content=content)
            ),
            user_message
            ]
        # 生成论文草稿
        response = self.model.invoke(messages)
        return {
            "draft": response.content,  # 保存论文草稿
            "revision_number": state.get("revision_number", 1) + 1,  # 修订次数+1（首次生成时从0→1）
            "lnode": "generate",
            "count": 1,
        }
    def reflection_node(self, state: AgentState):
        """批改反馈节点
        输入：当前状态（包含草稿）
        输出：批改意见 + 状态更新
        
        - 这里AI扮演"老师"角色
        - 返回的critique会用于后续修改
        """
        messages = [
            SystemMessage(content=self.REFLECTION_PROMPT), 
            HumanMessage(content=state['draft'])
        ]
        response = self.model.invoke(messages)
        return {"critique": response.content,
                "lnode": "reflect",
                "count": 1,
        }
    def research_critique_node(self, state: AgentState):
        """根据批改反馈修改论文研究内容（content）节点
        输入：当前状态（包含批改意见）
        输出：补充研究内容 + 状态更新
        
        - 根据批改意见生成新的搜索查询
        - 只生成2个查询（避免信息过载）
        - 再用tavily去执行搜索返回搜索结果拼接到content里
        """
        queries = self.model.with_structured_output(Queries).invoke([
            SystemMessage(content=self.RESEARCH_CRITIQUE_PROMPT),
            HumanMessage(content=state['critique'])
        ])
        content = state.get('content', []) 
        for q in queries.queries:
            response = self.tavily.search(query=q, max_results=2)
            for r in response['results']:
                content.append(r['content'])
        return {"content": content,
               "lnode": "research_critique",
                "count": 1,
        }
    def should_continue(self, state):
        """流程判断方法
        决定是否继续修改论文
        
        - revision_number：当前修改次数
        - max_revisions：最大允许修改次数
        - 如果达到上限就结束，否则继续修改
        """
        if state["revision_number"] > state["max_revisions"]:
            return END
        return "reflect"


# 导入 Gradio，用于创建 Web 界面
import gradio as gr
import time  # 导入时间模块

class writer_gui( ):
    """论文写作助手的 GUI 界面类"""

    def __init__(self, graph, share=False):
        """初始化 GUI 界面
        
        Args:
            graph: LangGraph 状态图（相当于论文写作的"大脑"）
            share: 是否分享界面（就像是否允许别人访问你的网页）
        """
        self.graph = graph  # 保存传入的状态图引用
        self.share = share  # 保存分享设置
        self.partial_message = ""  # 用于存储部分消息（就像便签纸，临时记下运行过程）
        self.response = {}  # 用于存储响应（保存self.graph.invoke()返回的结果）
        self.max_iterations = 10  # 最大迭代次数
        self.iterations = []  # 迭代计数列表，记录每个线程执行了几次
        self.threads = []  # 线程 ID 列表（记录所有正在进行的对话）
        self.thread_id = -1  # 当前线程 ID（-1 表示还没有开始任何对话）
        # 创建线程配置（每个对话有唯一的身份证号）
        self.thread = {"configurable": {"thread_id": str(self.thread_id)}}
        # 创建界面（启动GUI）
        self.demo = self.create_interface()

    def run_agent(self, start,topic,stop_after):
        """运行论文写作者代理
        
        Args:
            start: 是否开始新的写作任务（True=新任务，False=继续当前任务）
            topic: 论文主题（用户想写的题目）
            stop_after: 在哪些节点后暂停（设置断点）
            
        Yields:
            更新的界面元素（逐步显示结果，而不是一次性卡住）
        """
        #global partial_message, thread_id,thread
        #global response, max_iterations, iterations, threads
        # 如果是开始新任务
        if start:
            # 添加新的迭代计数（0 表示刚开始）
            self.iterations.append(0)  # 添加新的迭代计数
            # 创建初始配置
            config = {
                'task': topic,  # 论文题目
                "max_revisions": 2,  # 最多修改2次
                "revision_number": 0,  # 当前是第0次修改
                'lnode': "",  # 最后执行的节点（刚开始没有）
                'planner': "no plan",  # 大纲内容
                'draft': "no draft",  # 草稿内容
                'critique': "no critique",  # 批改意见
                'content': ["no content",],  # 研究内容
                'queries': "no queries",  # 搜索问题
                'count': 0  # 计数器
            }
            self.thread_id += 1  # 新的代理，新的线程
            self.threads.append(self.thread_id)  # 添加到线程列表
        else:
            config = None  # 继续当前任务

        # 更新线程配置 
        self.thread = {"configurable": {"thread_id": str(self.thread_id)}}
        
        # 运行最多 max_iterations 次迭代（防止无限循环）
        while self.iterations[self.thread_id] < self.max_iterations:
            # 调用状态图，传入配置和线程
            self.response = self.graph.invoke(config, self.thread)
            # 增加迭代计数（进度+1）
            self.iterations[self.thread_id] += 1  # 增加迭代计数
            # 添加响应到消息（记录结果）
            self.partial_message += str(self.response)  # 添加响应到消息
            self.partial_message += f"\n------------------\n\n"  # 添加分隔符
            
            # 获取当前状态信息（了解现在进行到哪一步）
            lnode,nnode,_,rev,acount = self.get_disp_state()
            # 生成界面更新（把最新状态显示给用户）
            yield self.partial_message,lnode,nnode,self.thread_id,rev,acount

            config = None   # 后续迭代不需要初始配置

            # 如果没有下一个节点，表示流程结束
            if not nnode:  
                #print("Hit the end")
                return
            # 如果当前节点在 stop_after 列表中，暂停执行
            if lnode in stop_after:
                #print(f"stopping due to stop_after {lnode}")
                return
            else:
                #print(f"Not stopping on lnode {lnode}")
                pass
        return
    
    def get_disp_state(self,):
        """获取用于显示的状态信息（就像查看进度条）
        Returns:
            lnode: 最后执行的节点（上一步做了什么）
            nnode: 下一个要执行的节点（下一步要做什么）
            thread_id: 当前线程 ID（当前对话的身份证号）
            rev: 当前修订次数（修改了几次）
            acount: 当前计数（内部计数器）
        """
        # 获取当前状态
        current_state = self.graph.get_state(self.thread)
        # 提取需要的信息
        lnode = current_state.values["lnode"]  # 上一步
        acount = current_state.values["count"]  # 计数器
        rev = current_state.values["revision_number"]  # 修改次数
        nnode = current_state.next  # 下一步
        #print  (lnode,nnode,self.thread_id,rev,acount)
        return lnode,nnode,self.thread_id,rev,acount
    
    def get_state(self,key):
        """获取状态中的特定值
        
        Args:
            key: 状态键（想要查什么内容）
            
        Returns:
            gr.update 对象（告诉界面如何更新）
        """
        # 获取当前状态
        current_values = self.graph.get_state(self.thread)
        # 如果键存在于状态中
        if key in current_values.values:
            # 获取显示状态（了解当前进度）
            lnode,nnode,self.thread_id,rev,acount = self.get_disp_state()
            # 创建新的标签（显示更多信息）
            new_label = f"last_node: {lnode}, thread_id: {self.thread_id}, rev: {rev}, step: {acount}"
            # 返回更新
            return gr.update(label=new_label, value=current_values.values[key])
        else:
            return ""  
    
    def get_content(self,):
        """获取内容状态（获取研究收集的资料）
        
        Returns:
            gr.update 对象（告诉界面如何更新）
        """
        # 获取当前状态
        current_values = self.graph.get_state(self.thread)
        # 如果内容存在于状态中
        if "content" in current_values.values:
            # 获取内容列表
            content = current_values.values["content"]
            # 获取显示状态
            lnode, nnode, thread_id, rev, acount = self.get_disp_state()
            # 创建新的标签
            new_label = f"last_node: {lnode}, thread_id: {self.thread_id}, rev: {rev}, step: {acount}"
            # 将内容连接成字符串并返回更新
            return gr.update(label=new_label, value="\n\n".join(item for item in content) + "\n\n")
        else:
            return ""  
    
    def update_hist_pd(self,):
        """更新历史下拉菜单（显示所有历史状态）
        
        Returns:
            gr.Dropdown 对象（下拉菜单组件）
        """
        hist = []  # 历史记录列表
        # 遍历状态历史（最新的先返回）
        for state in self.graph.get_state_history(self.thread):
            # 跳过早期状态
            if state.metadata['step'] < 1:
                continue
            # 提取状态信息
            # 已过时
            # thread_ts = state.config['configurable']['thread_ts']
            thread_step = state.metadata['step']  # 步骤序号（从0开始递增）
            tid = state.config['configurable']['thread_id']  # 对话ID
            count = state.values['count']  # 计数器
            lnode = state.values['lnode']  # 上一步
            rev = state.values['revision_number']  # 修改次数
            nnode = state.next  # 下一步
            # 创建状态字符串
            st = f"{tid}:{thread_step}:{count}:{lnode}:{nnode}:{rev}"
            hist.append(st)
        # 返回下拉菜单更新
        return gr.Dropdown(label="update_state from: thread:step:count:last_node:next_node:rev", 
                           choices=hist, value=hist[0],interactive=True)
    
    def find_config(self,thread_step):
        """根据步骤找配置
        
        Args:
            thread_step: 步骤号
            
        Returns:
            配置对象或 None
        """
        # 遍历状态历史
        for state in self.graph.get_state_history(self.thread):
            # 如果时间戳匹配
            if state.metadata['step'] == thread_step:
                return state.config
        return(None)
            
    def copy_state(self,hist_str):
        ''' 
        result of selecting an old state from the step pulldown. Note does not change thread. 
        This copies an old state to a new current state. 
        从步骤下拉菜单中选择旧状态的结果。注意：不会更改线程。
        这会将旧状态复制到新的当前状态。
        
        复制旧状态到当前状态（时间旅行功能）
        
        Args:
            hist_str: 历史字符串（格式：thread:step:count:...）
            
        Returns:
            状态信息元组
        '''
        thread_step = hist_str.split(":")[1]
        print(f"copy_state from {thread_step}")
        config = self.find_config(thread_step)
        #print(config)
        state = self.graph.get_state(config)
        self.graph.update_state(self.thread, state.values, as_node=state.values['lnode'])
        new_state = self.graph.get_state(self.thread)  #should now match
        tid = new_state.config['configurable']['thread_id']
        count = new_state.values['count']
        lnode = new_state.values['lnode']
        rev = new_state.values['revision_number']
        nnode = new_state.next
        return lnode,nnode,tid,rev,count
    
    def update_thread_pd(self,threads):
        """更新线程下拉菜单
        
        Returns:
            gr.Dropdown 对象，用于更新界面
        """
        #print("update_thread_pd")
        return gr.Dropdown(label="choose thread", choices=threads, value=self.thread_id,interactive=True)
    
    def switch_thread(self,new_thread_id):
        """切换到新线程
        
        Args:
            new_thread_id: 新线程 ID
        """
        #print(f"switch_thread{new_thread_id}")
        self.thread = {"configurable": {"thread_id": str(new_thread_id)}}
        self.thread_id = new_thread_id
        return 
    
    def modify_state(self,key,asnode,new_state):
        ''' gets the current state, modifes a single value in the state identified by key, and updates state with it.
        note that this will create a new 'current state' node. If you do this multiple times with different keys, it will create
        one for each update. Note also that it doesn't resume after the update

        获取当前状态，修改状态中由键标识的单个值，并使用该值更新状态。
        请注意，这将创建一个新的“当前状态”节点。
        如果您使用不同的键多次执行此操作，则每次更新都会创建一个新节点。另请注意，更新后不会恢复。

        修改状态中的特定值（人工干预流程）
        Args:
            key: 要修改的状态键
            asnode: 作为哪个节点进行修改
            new_state: 新的值
        注意：这会创建一个新的"当前状态"节点
        '''
        # 获取当前状态
        current_values = self.graph.get_state(self.thread)
        # 修改指定的值
        current_values.values[key] = new_state
        # 更新状态（as_node指定在哪个节点后修改）
        self.graph.update_state(self.thread, current_values.values,as_node=asnode)
        return


    def create_interface(self):
        """创建用户界面
        
        Returns:
            Gradio Blocks 对象（界面组件）
        """
        with gr.Blocks(theme=gr.themes.Default(spacing_size='sm',text_size="sm")) as demo:
            
            def updt_disp():
                """通用状态显示更新函数
                - 这个函数在状态变化时被调用，用于更新GUI界面上的各种显示元素
                """
                ''' general update display on state change '''
                current_state = self.graph.get_state(self.thread)
                hist = []
                # curiously, this generator returns the latest first
                # 遍历状态历史
                for state in self.graph.get_state_history(self.thread):
                    if state.metadata['step'] < 1:  #ignore early states
                        continue
                    # thread_ts 记录了状态创建的具体时间点，已启用
                    # s_thread_ts = state.config['configurable']['thread_ts']
                    # 使用 state.metadata['step'] 替代原来的 thread_ts，表示状态在流程中的步骤序号（从0开始递增）
                    s_step = state.metadata['step']
                    s_tid = state.config['configurable']['thread_id']
                    s_count = state.values['count']
                    s_lnode = state.values['lnode']
                    s_rev = state.values['revision_number']
                    s_nnode = state.next
                    st = f"{s_tid}:{s_step}:{s_count}:{s_lnode}:{s_nnode}:{s_rev}"
                    hist.append(st)
                if not current_state.metadata: #handle init call
                    return{}
                else:
                    # 返回需要更新的界面元素
                    return {
                        topic_bx : current_state.values["task"],
                        lnode_bx : current_state.values["lnode"],
                        count_bx : current_state.values["count"],
                        revision_bx : current_state.values["revision_number"],
                        nnode_bx : current_state.next,
                        threadid_bx : self.thread_id,
                        thread_pd : gr.Dropdown(
                            label="choose thread",   # 顶部显示的文字（"choose thread"）
                            choices=self.threads,   #可选项列表（所有线程ID）
                            value=self.thread_id,  # ：默认选中的值（当前线程ID）
                            interactive=True  # 是否可交互（True=可以点击选择）
                        ),
                        step_pd : gr.Dropdown(label="update_state from: thread:step:count:last_node:next_node:rev", 
                               choices=hist, value=hist[0],interactive=True),
                    }
            def get_snapshots():
                """获取状态快照（查看历史记录）
                - 为了显示简洁，只显示部分内容（截断长文本）
                """
                new_label = f"thread_id: {self.thread_id}, Summary of snapshots"
                sstate = ""
                for state in self.graph.get_state_history(self.thread):
                    # 截断长文本，只显示开头部分
                    for key in ['plan', 'draft', 'critique']:
                        if key in state.values:
                            state.values[key] = state.values[key][:80] + "..."
                    if 'content' in state.values:
                        for i in range(len(state.values['content'])):
                            state.values['content'][i] = state.values['content'][i][:20] + '...'
                    if 'writes' in state.metadata:
                        state.metadata['writes'] = "not shown"
                    sstate += str(state) + "\n\n"
                return gr.update(label=new_label, value=sstate)

            def vary_btn(stat):
                """改变按钮样式（视觉反馈）
                - 当按钮被点击时，改变颜色表示"正在处理"
                """
                #print(f"vary_btn{stat}")
                return(gr.update(variant=stat))
            
            # 主界面标签页
            with gr.Tab("Agent"):
                # 第一行：主题输入和操作按钮
                with gr.Row():
                    topic_bx = gr.Textbox(label="Essay Topic", value="Pizza Shop")
                    gen_btn = gr.Button("Generate Essay", scale=0,min_width=80, variant='primary')
                    cont_btn = gr.Button("Continue Essay", scale=0,min_width=80)
                # 第二行：状态显示
                with gr.Row():
                    lnode_bx = gr.Textbox(label="last node", min_width=100)
                    nnode_bx = gr.Textbox(label="next node", min_width=100)
                    threadid_bx = gr.Textbox(label="Thread", scale=0, min_width=80)
                    revision_bx = gr.Textbox(label="Draft Rev", scale=0, min_width=80)
                    count_bx = gr.Textbox(label="count", scale=0, min_width=80)
                # 高级设置（默认折叠）
                with gr.Accordion("Manage Agent", open=False):
                    # 获取所有节点（排除__start__）
                    checks = list(self.graph.nodes.keys())
                    checks.remove('__start__')
                    # 中断设置：在哪些节点后暂停
                    stop_after = gr.CheckboxGroup(checks,label="Interrupt After State", value=checks, scale=0, min_width=400)
                    # 线程和步骤选择
                    with gr.Row():
                        thread_pd = gr.Dropdown(choices=self.threads,interactive=True, label="select thread", min_width=120, scale=0)
                        step_pd = gr.Dropdown(choices=['N/A'],interactive=True, label="select step", min_width=160, scale=1)
                # 实时输出显示
                live = gr.Textbox(label="Live Agent Output", lines=5, max_lines=5)
        
                # 界面交互逻辑
                sdisps =[topic_bx,lnode_bx,nnode_bx,threadid_bx,revision_bx,count_bx,step_pd,thread_pd]
                # 当切换线程时更新界面
                thread_pd.input(self.switch_thread, [thread_pd], None).then(fn=updt_disp, inputs=None, outputs=sdisps)
                # 当选择历史状态时更新界面
                step_pd.input(self.copy_state,[step_pd],None).then(fn=updt_disp, inputs=None, outputs=sdisps)
                # 生成按钮点击事件
                gen_btn.click(vary_btn,gr.Number("secondary", visible=False), gen_btn).then(
                              fn=self.run_agent, inputs=[gr.Number(True, visible=False),topic_bx,stop_after], outputs=[live],show_progress=True).then(
                              fn=updt_disp, inputs=None, outputs=sdisps).then( 
                              vary_btn,gr.Number("primary", visible=False), gen_btn).then(
                              vary_btn,gr.Number("primary", visible=False), cont_btn)
                # 继续按钮点击事件
                cont_btn.click(
                    vary_btn,
                    gr.Number("secondary", visible=False), 
                    cont_btn
                ).then(
                    fn=self.run_agent, 
                    inputs=[gr.Number(False, visible=False),topic_bx,stop_after], 
                    outputs=[live]
                ).then(
                    fn=updt_disp, 
                    inputs=None, 
                    outputs=sdisps
                ).then(
                    vary_btn,gr.Number("primary", visible=False), 
                    cont_btn
                )
            # 计划标签页
            with gr.Tab("Plan"):
                with gr.Row():
                    refresh_btn = gr.Button("Refresh")
                    modify_btn = gr.Button("Modify")
                plan = gr.Textbox(label="Plan", lines=10, interactive=True)
                # 刷新按钮：获取最新计划
                refresh_btn.click(fn=self.get_state, inputs=gr.Number("plan", visible=False), outputs=plan)
                # 修改按钮：更新计划内容
                modify_btn.click(
                    fn=self.modify_state,   # 指定点击后要执行的函数
                    inputs=[
                        gr.Number("plan", visible=False),  # 创建一个隐藏的Number组件，值为"plan"。这不是真正的数字，而是用Number组件传递字符串"plan"作为参数
                        gr.Number("planner", visible=False), 
                        plan  # 这是界面上的plan文本框组件，传递其当前值
                    ],  # 指定传递给self.modify_state函数的参数
                    outputs=None  # 指定该函数的返回值不更新任何界面组件
                ).then(
                    fn=updt_disp, 
                    inputs=None, 
                    outputs=sdisps
                )

            # 研究内容标签页
            with gr.Tab("Research Content"):
                refresh_btn = gr.Button("Refresh")
                content_bx = gr.Textbox(label="content", lines=10)
                refresh_btn.click(fn=self.get_content, inputs=None, outputs=content_bx)
            
            # 草稿标签页
            with gr.Tab("Draft"):
                with gr.Row():
                    refresh_btn = gr.Button("Refresh")
                    modify_btn = gr.Button("Modify")
                draft_bx = gr.Textbox(label="draft", lines=10, interactive=True)
                refresh_btn.click(fn=self.get_state, inputs=gr.Number("draft", visible=False), outputs=draft_bx)
                modify_btn.click(fn=self.modify_state, inputs=[gr.Number("draft", visible=False),
                                                          gr.Number("generate", visible=False), draft_bx], outputs=None).then(
                                fn=updt_disp, inputs=None, outputs=sdisps)
            
            # 批改标签页
            with gr.Tab("Critique"):
                with gr.Row():
                    refresh_btn = gr.Button("Refresh")
                    modify_btn = gr.Button("Modify")
                critique_bx = gr.Textbox(label="Critique", lines=10, interactive=True)
                refresh_btn.click(fn=self.get_state, inputs=gr.Number("critique", visible=False), outputs=critique_bx)
                modify_btn.click(fn=self.modify_state, inputs=[gr.Number("critique", visible=False),
                                                          gr.Number("reflect", visible=False), 
                                                          critique_bx], outputs=None).then(
                                fn=updt_disp, inputs=None, outputs=sdisps)
            
            # 状态快照标签页
            with gr.Tab("StateSnapShots"):
                with gr.Row():
                    refresh_btn = gr.Button("Refresh")
                snapshots = gr.Textbox(label="State Snapshots Summaries")
                refresh_btn.click(fn=get_snapshots, inputs=None, outputs=snapshots)
        return demo

    def launch(self, share=None):
        """启动界面（打开网页）
        
        Args:
            share: 是否分享（覆盖初始化设置）
        """
        # 如果设置了PORT1环境变量，使用该端口
        if port := os.getenv("PORT1"):
            self.demo.launch(share=True, server_port=int(port), server_name="0.0.0.0")
        else:
            self.demo.launch(share=self.share)
