# 执行说明，先打开terminal，然后执行以下命令
# 1. 安装20版本nodejs: nvm install 20.19.5
# 2. 切换NODEJS: nvm use 20.19.5
# 3. 安装MCP服务器Airbnb插件: npm install -g @openbnb/mcp-server-airbnb
#   可以先执行这个命令设置镜像，再安装：npm config set registry https://registry.npmmirror.com
# 4. 运行本脚本: python .\11-agentic-protocols\11-mcp.py

# Import cell - Updated imports
# 导入必要的库 - 就像做饭前准备好所有食材
import json  # 用于处理JSON数据格式
import os    # 用于操作系统相关功能，如读取环境变量
import asyncio  # 用于异步编程，让程序能同时做多件事
import subprocess  # 用于运行外部命令（如npx）
import sys  # 提供对Python解释器的访问

# 从dotenv导入load_dotenv，用于加载.env文件中的环境变量
from dotenv import load_dotenv
# 用于在Jupyter Notebook中显示HTML内容
from IPython.display import display, HTML
# 用于给函数参数添加描述信息
from typing import Annotated


from openai import AsyncOpenAI

from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion  # OpenAI连接器
# 从semantic_kernel导入关键组件
from semantic_kernel.agents import (  # Agent相关组件
    ChatCompletionAgent,     # 基于聊天完成的Agent
    ChatHistoryAgentThread   # 用于维护对话历史的线程
)
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion  # Azure OpenAI连接器
from semantic_kernel.connectors.mcp import MCPStdioPlugin  # MCP协议插件
from semantic_kernel.contents import (  # 不同类型的内容对象
    FunctionCallContent,     # 表示函数调用的内容
    FunctionResultContent,   # 表示函数调用结果的内容
    StreamingTextContent     # 表示流式文本响应的内容
)

load_dotenv()

user_inputs = [
    "Find Airbnb in Stockholm for 2 adults 1 kid",
]

# 主函数：运行MCP启用的代理，使用Azure OpenAI与OpenBnB服务器通信
async def main():
    """Main function to run the MCP-enabled agent with real OpenBnB server using Azure OpenAI"""

    try:
        print("🚀 Starting with Azure OpenAI...")
        
        # Verify environment variables
        print("🔍 Checking Azure environment variables...")
        # 必需的环境变量列表
        required_vars = [
            "AZURE_OPENAI_CHAT_DEPLOYMENT_NAME",  # 部署名称
            "AZURE_OPENAI_ENDPOINT",             # Azure服务端点
            "AZURE_OPENAI_API_KEY"               # API密钥
        ]
        
        # 检查每个环境变量是否存在
        for var in required_vars:
            if os.getenv(var):
                print(f"✅ {var} is set")
            else:
                print(f"❌ {var} is NOT set")
        
        # 开始创建MCP插件连接
        print("\n🔧 Creating MCP Plugin...")
        
        # Create MCP plugin connection to real OpenBnB server
        # Based on the GitHub repo, the server doesn't need special env vars
        # 使用async with确保资源正确清理
        # MCPStdioPlugin通过标准输入输出与MCP服务器通信
        async with MCPStdioPlugin(
            name="AirbnbSearch",  # 插件名称
            description="Search for Airbnb accommodations using OpenBnB MCP server",  # 插件描述
            command=r"mcp-server-airbnb",
            # command="npx",  # 要运行的命令
            # args=["-y", "@openbnb/mcp-server-airbnb"],  # 命令参数：下载并运行Airbnb MCP服务器
        ) as airbnb_plugin:  # 将插件命名为airbnb_plugin

            # MCP插件已创建并连接
            print("✅ MCP Plugin created and connected")
            # Wait a moment for the server to fully initialize
            # 等待服务器初始化（给服务器一点时间启动）
            await asyncio.sleep(2)

            try:
                # 尝试获取工具列表来验证连接
                tools_response = await airbnb_plugin.session.list_tools()
                print(f"✅ MCP服务就绪！发现 {len(tools_response.tools)} 个工具: {[t.name for t in tools_response.tools]}")
            except Exception as e:
                print(f"❌ MCP服务连接失败！错误: {str(e)}")
                print("请检查：")
                print("1. 是否已全局安装：npm install -g @openbnb/mcp-server-airbnb")
                print("2. 是否在新终端运行：mcp-server-airbnb")
                print("3. 是否刷新了环境变量")
                raise ConnectionError("MCP服务未就绪") from e
            # airbnb_plugin.load_tools()  # 加载插件工具
            # Try to list available tools
            # 尝试列出可用工具（查看MCP服务器提供哪些功能）
            # try:
            #     tools = await airbnb_plugin.load_tools()
            #     print(f"🔧 Available tools: {[tool.name for tool in tools]}")
            # except Exception as e:
            #     print(f"⚠️ Could not list tools: {str(e)}")

            # 创建Azure OpenAI服务连接
            # Create the Azure OpenAI service with proper configuration
            print("\n🤖 Creating Azure OpenAI service...")
            # service = AzureChatCompletion(
            #     deployment_name=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"),
            #     endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            #     api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            # )

            # 使用AsyncOpenAI客户端创建服务实例
            client = AsyncOpenAI(
                api_key=os.environ["GITHUB_TOKEN"],
                base_url="https://models.inference.ai.azure.com/"
            )
            service = OpenAIChatCompletion(
                # 指定要使用的模型ID（这里是通义千问的qwen-max）
                ai_model_id="gpt-4o",
                # 传入之前创建的AsyncOpenAI客户端
                async_client=client,
            )

            
            # Create agent with the service instance
            # 创建AI代理
            # 指令翻译如下：
            # 你是一个Airbnb搜索助手。使用可用功能搜索房源。
            # 将结果格式化为清晰的HTML表格，包含房源名称、价格、评分和链接。
            agent = ChatCompletionAgent(
                # kernel=airbnb_plugin.kernel,  # 使用插件的kernel
                service=service,  # 使用上面创建的Azure服务
                name="AirbnbAgent",  # 代理名称
                # 代理指令 - 告诉AI如何行为
                instructions="""You are an Airbnb search assistant. Use the available functions to search for properties. 
                "Format valid results as a markdown table with columns: property name, price, rating, link. "
                "Output plain text table."
                """,
                plugins=[airbnb_plugin],
            )

            print("✅ Agent created with Azure OpenAI")

            # Process each user input
            # 创建线程来保存对话历史
            thread: ChatHistoryAgentThread | None = None

            # 依次处理每个用户输入
            for user_input in user_inputs:
                print(f"\n🔍 User: {user_input}")
                
                try:
                    # Use the simpler get_response method
                    # 让代理处理用户输入
                    response = await agent.get_response(messages=user_input, thread=thread)
                    thread = response.thread  # 更新对话线程
                    
                    # 获取响应文本
                    response_text = str(response)
                    
                    # 打印响应摘要
                    print(f"🤖 {response.name}: {response_text[:200]}..." if len(response_text) > 200 else response_text)
                    
                    if "<IPython.core.display.HTML object>" in response_text:
                        # 尝试提取实际HTML内容或转换为纯文本
                        # 这里需要根据实际返回结构调整
                        clean_response = response_text.replace("<IPython.core.display.HTML object>", "HTML content not renderable in terminal")
                        print(clean_response)
                    else:
                        print(response_text)
                        
                except Exception as e:
                    print(f"❌ Error processing user input: {str(e)}")
                    import traceback
                    traceback.print_exc()
                
            # Cleanup
            # 清理对话线程
            if thread:
                await thread.delete()
                print("🧹 Thread cleaned up")
                
    except Exception as e:
        print(f"❌ Main error: {str(e)}")
        import traceback
        traceback.print_exc()

# Run the main function
print("🚀 Starting MCP Agent...")
asyncio.run(main())
print("✅ Done!")