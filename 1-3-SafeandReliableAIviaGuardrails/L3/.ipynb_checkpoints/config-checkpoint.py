import os
from openai import OpenAI
from dotenv import find_dotenv, load_dotenv
from typing import Any, Dict

from guardrails import Guard, Validator, register_validator, FailResult, PassResult

_ = load_dotenv(find_dotenv())

qwen_client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),  # 从环境变量读取
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

# 封装一个可调用的函数，Guardrails 会使用这个函数与大模型交互
def qwen_llm_callable(*args, **kwargs):
    response = qwen_client.chat.completions.create(
        model=kwargs.get("model", "qwen-max"),
        messages=kwargs.get("messages", args[0] if args else []),
        temperature=kwargs.get("temperature", 0.0),
        top_p=kwargs.get("top_p", 0.8),
    )
    return response

# Register the custom validator
@register_validator(name="detect_colosseum", data_type="string")
class ColosseumDetector(Validator):
    def _validate(
        self,
        value: Any,
        metadata: Dict[str, Any] = {}
    ) -> ValidationResult:
        if "colosseum" in value.lower():
            return FailResult(
                error_message="Colosseum detected",
                fix_value="I'm sorry, I can't answer questions about Project Colosseum."
            )
        return PassResult()

guard = Guard(llm_api=qwen_llm_callable)
guard.name = 'qwen_colosseum_guard'

print("GUARD PARAMETERS UNFILLED! UPDATE THIS FILE!")  # TODO: Remove this when parameters are filled.

guard.use(validator="detect_colosseum", on_fail="fix")
