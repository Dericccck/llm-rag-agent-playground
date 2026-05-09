from guardrails import Guard
from guardrails.hub import RestrictToTopic
import os
import json # 确保导入
from openai import OpenAI
from dotenv import find_dotenv, load_dotenv

_ = load_dotenv(find_dotenv())

# 确保 DASHSCOPE_API_KEY 是你用于 Qwen/Dashscope 的密钥
client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

# 修正：移除 self，并添加 *args, **kwargs 应对潜在 Bug
def qwen_callable(text: str, topics: list, *args, **kwargs):
    print(f"text={text}")
    print(f"topics={topics}")
    
    # 修正：构建 LLM Prompt
    topics_str = json.dumps(topics, ensure_ascii=False)
    
    prompt = (
        f"你是一个严格的主题分类器。请从【主题列表】中选出最匹配【待审核文本】的主题，并用逗号分隔，不要有额外文字。\n"
        f"如果文本不匹配任何主题，请严格返回：'None'\n"
        f"【主题列表】: {topics_str}\n"
        f"【待审核文本】: {text}"
    )

    response = client.chat.completions.create(
        model="qwen-max",
        messages=[{"role": "user", "content": prompt}], # 使用构建好的 prompt
        seed=42,
        temperature=0.0
    )
    
    return response.choices[0].message.content

# 初始化 Guard
guard = Guard()
guard.name = 'topic_guard'

# 使用修正后的 llm_callable
guard.use(
    RestrictToTopic(
        llm_callable=qwen_callable,
        valid_topics=["pizza", "food", "restaurant", "order", "menu"],
        invalid_topics=["politics", "automobiles"],
        on_fail="exception"
    )
)