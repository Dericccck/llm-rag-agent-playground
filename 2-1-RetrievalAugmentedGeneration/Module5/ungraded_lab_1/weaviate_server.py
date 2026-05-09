import weaviate  # 导入 Weaviate 客户端库，用于操作向量数据库
import subprocess  # 导入子进程模块，用于管理外部进程
from contextlib import contextmanager  # 导入上下文管理器工具

@contextmanager
def suppress_subprocess_output():
    """
    上下文管理器：用于在执行块内抑制所有 subprocess.Popen 调用产生的标准输出和错误。
    这在启动嵌入式 Weaviate 时非常有用，因为它可以防止底层服务的启动日志刷屏。
    """
    # 1. 备份原生的 Popen 方法，以便后续还原
    original_popen = subprocess.Popen

    def patched_popen(*args, **kwargs):
        # 2. 修改参数：强制将 stdout（标准输出）和 stderr（错误输出）导向“空设备”(DEVNULL)
        kwargs['stdout'] = subprocess.DEVNULL
        kwargs['stderr'] = subprocess.DEVNULL
        # 使用修改后的参数调用原始的 Popen
        return original_popen(*args, **kwargs)

    try:
        # 3. 应用补丁：用我们自定义的函数替换掉全局的 subprocess.Popen
        subprocess.Popen = patched_popen
        # 将控制权交回给 with 语句块
        yield
    finally:
        # 4. 还原现场：无论代码是否报错，最后都要将 Popen 还原回原始方法
        subprocess.Popen = original_popen

# 使用自定义的上下文管理器来启动并连接 Weaviate
with suppress_subprocess_output():
    # 启动嵌入式 Weaviate 实例（无需单独启动 Docker 镜像，直接在当前进程运行）
    client = weaviate.connect_to_embedded(
        # 指定数据持久化路径，所有的索引和文档都会保存在当前目录下的 .collections 文件夹
        persistence_data_path="./.collections",
        
        # 环境变量配置：用于定义 Weaviate 的模块行为
        environment_variables={
            # 开启基于 API 的外部模块支持
            "ENABLE_API_BASED_MODULES": "true",
            # 启用文本转向量的 transformers 模块
            "ENABLE_MODULES": 'text2vec-transformers',
            # 关键配置：将向量化推理的 API 地址指向本地 5000 端口
            # 这里的 5000 端口正是你之前代码中 Flask 启动的向量化微服务地址
            "TRANSFORMERS_INFERENCE_API": "http://127.0.0.1:5000/"
        }
    )