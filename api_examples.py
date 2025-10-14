"""
Ollama API 调用示例
支持本地调用和通过 ngrok 外网调用
"""

import requests
import json

# ===========================
# 配置区域
# ===========================

# 本地 Ollama API 地址
LOCAL_API_URL = "http://localhost:11436"

# Ngrok 外网地址（启动服务后从 http://localhost:4040 获取）
# 示例: "https://xxxx-xx-xx-xxx-xxx.ngrok-free.app"
NGROK_API_URL = "YOUR_NGROK_URL_HERE"

# 使用的模型名称
MODEL_NAME = "gpt-oss:20b"


# ===========================
# API 调用函数
# ===========================

def call_ollama_generate(api_url, model, prompt, stream=False):
    """
    调用 Ollama Generate API

    参数:
        api_url: API 基础地址
        model: 模型名称
        prompt: 提示词
        stream: 是否使用流式输出

    返回:
        响应内容
    """
    endpoint = f"{api_url}/api/generate"

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": stream
    }

    try:
        print(f"🚀 正在调用 API: {endpoint}")
        print(f"📝 提示词: {prompt}")
        print("-" * 50)

        response = requests.post(
            endpoint,
            json=payload,
            timeout=300  # 5分钟超时
        )

        response.raise_for_status()

        if stream:
            # 流式输出
            print("📡 流式响应:")
            full_response = ""
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    if 'response' in data:
                        chunk = data['response']
                        print(chunk, end='', flush=True)
                        full_response += chunk
            print("\n" + "-" * 50)
            return full_response
        else:
            # 非流式输出
            result = response.json()
            print("✅ 响应成功:")
            print(result.get('response', ''))
            print("-" * 50)
            return result

    except requests.exceptions.Timeout:
        print("❌ 请求超时，请检查模型是否已加载")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {e}")
        return None


def call_ollama_chat(api_url, model, messages):
    """
    调用 Ollama Chat API（对话接口）

    参数:
        api_url: API 基础地址
        model: 模型名称
        messages: 对话消息列表

    返回:
        响应内容
    """
    endpoint = f"{api_url}/api/chat"

    payload = {
        "model": model,
        "messages": messages,
        "stream": False
    }

    try:
        print(f"🚀 正在调用 Chat API: {endpoint}")
        print(f"💬 对话消息: {json.dumps(messages, ensure_ascii=False, indent=2)}")
        print("-" * 50)

        response = requests.post(
            endpoint,
            json=payload,
            timeout=300
        )

        response.raise_for_status()
        result = response.json()

        print("✅ 响应成功:")
        print(result.get('message', {}).get('content', ''))
        print("-" * 50)
        return result

    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {e}")
        return None


def list_models(api_url):
    """
    列出所有可用的模型

    参数:
        api_url: API 基础地址

    返回:
        模型列表
    """
    endpoint = f"{api_url}/api/tags"

    try:
        print(f"🔍 查询可用模型: {endpoint}")
        response = requests.get(endpoint, timeout=10)
        response.raise_for_status()

        result = response.json()
        models = result.get('models', [])

        print("📚 可用模型列表:")
        for model in models:
            print(f"  - {model.get('name')} (大小: {model.get('size', 0) / 1e9:.2f} GB)")
        print("-" * 50)

        return models

    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {e}")
        return None


# ===========================
# 使用示例
# ===========================

def example_local_call():
    """示例 1: 本地调用"""
    print("\n" + "=" * 50)
    print("示例 1: 本地 API 调用")
    print("=" * 50 + "\n")

    # 列出模型
    list_models(LOCAL_API_URL)

    # Generate API 调用
    call_ollama_generate(
        api_url=LOCAL_API_URL,
        model=MODEL_NAME,
        prompt="什么是人工智能？请用100字以内回答。",
        stream=False
    )

    # Chat API 调用
    messages = [
        {"role": "system", "content": "你是一个友好的 AI 助手。"},
        {"role": "user", "content": "介绍一下 Docker 的优势。"}
    ]
    call_ollama_chat(LOCAL_API_URL, MODEL_NAME, messages)


def example_ngrok_call():
    """示例 2: 通过 ngrok 外网调用"""
    print("\n" + "=" * 50)
    print("示例 2: Ngrok 外网 API 调用")
    print("=" * 50 + "\n")

    if NGROK_API_URL == "YOUR_NGROK_URL_HERE":
        print("⚠️  请先设置 NGROK_API_URL")
        print("访问 http://localhost:4040 获取 ngrok 公网地址")
        return

    # 列出模型
    list_models(NGROK_API_URL)

    # Generate API 调用
    call_ollama_generate(
        api_url=NGROK_API_URL,
        model=MODEL_NAME,
        prompt="解释一下什么是 LLM。",
        stream=False
    )


def example_stream_call():
    """示例 3: 流式输出调用"""
    print("\n" + "=" * 50)
    print("示例 3: 流式输出调用")
    print("=" * 50 + "\n")

    call_ollama_generate(
        api_url=LOCAL_API_URL,
        model=MODEL_NAME,
        prompt="写一首关于春天的短诗。",
        stream=True
    )


# ===========================
# cURL 命令示例
# ===========================

def print_curl_examples():
    """打印 cURL 命令示例"""
    print("\n" + "=" * 50)
    print("cURL 命令示例")
    print("=" * 50 + "\n")

    print("1. 列出所有模型:")
    print(f'curl {LOCAL_API_URL}/api/tags')
    print()

    print("2. Generate API 调用:")
    print(f'''curl {LOCAL_API_URL}/api/generate -d '{{
  "model": "{MODEL_NAME}",
  "prompt": "Why is the sky blue?",
  "stream": false
}}' ''')
    print()

    print("3. Chat API 调用:")
    print(f'''curl {LOCAL_API_URL}/api/chat -d '{{
  "model": "{MODEL_NAME}",
  "messages": [
    {{"role": "user", "content": "你好，请介绍一下自己。"}}
  ],
  "stream": false
}}' ''')
    print()

    print("4. 通过 Ngrok 外网调用（替换 YOUR_NGROK_URL）:")
    print(f'''curl https://YOUR_NGROK_URL/api/generate -d '{{
  "model": "{MODEL_NAME}",
  "prompt": "Hello from the internet!",
  "stream": false
}}' ''')
    print()


# ===========================
# 主程序
# ===========================

if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════════╗
    ║     Ollama API 调用示例程序                ║
    ║     支持本地和 Ngrok 外网调用              ║
    ╚════════════════════════════════════════════╝
    """)

    # 运行示例
    example_local_call()
    # example_ngrok_call()  # 取消注释以测试外网调用
    # example_stream_call()  # 取消注释以测试流式输出

    # 打印 cURL 示例
    print_curl_examples()

    print("\n✅ 示例执行完成！")
    print("💡 提示: 修改代码中的 NGROK_API_URL 后可测试外网调用")
