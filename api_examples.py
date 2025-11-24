"""
Ollama API 调用示例
支持本地和内网调用
"""

import requests
import json
import socket

# ===========================
# 配置区域
# ===========================

# 本地 Ollama API 地址
LOCAL_API_URL = "http://localhost:11435"

# 内网 Ollama API 地址（需要替换为实际的服务器内网 IP）
# 示例: "http://192.168.1.100:11435"
INTRANET_API_URL = "http://YOUR_SERVER_IP:11435"

# 使用的模型名称
MODEL_NAME = "gpt-oss:20b"


def get_local_ip():
    """获取本机内网 IP 地址"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "无法获取"


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


def example_intranet_call():
    """示例 2: 内网调用（从其他设备访问）"""
    print("\n" + "=" * 50)
    print("示例 2: 内网 API 调用")
    print("=" * 50 + "\n")

    if INTRANET_API_URL == "http://YOUR_SERVER_IP:11434":
        print("⚠️  请先设置 INTRANET_API_URL")
        print(f"提示: 本机内网 IP 是 {get_local_ip()}")
        print(f"在其他设备上，使用 http://{get_local_ip()}:11434 访问")
        return

    # 列出模型
    list_models(INTRANET_API_URL)

    # Generate API 调用
    call_ollama_generate(
        api_url=INTRANET_API_URL,
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

    local_ip = get_local_ip()

    print(f"4. 从其他内网设备调用（替换 {local_ip} 为实际服务器 IP）:")
    print(f'''curl http://{local_ip}:11435/api/generate -d '{{
  "model": "{MODEL_NAME}",
  "prompt": "Hello from intranet!",
  "stream": false
}}' ''')
    print()


def print_network_info():
    """打印网络配置信息"""
    print("\n" + "=" * 50)
    print("网络配置信息")
    print("=" * 50 + "\n")

    local_ip = get_local_ip()

    print(f"📍 本机内网 IP: {local_ip}")
    print(f"🔌 Ollama 服务端口: 11435")
    print(f"\n📱 从其他设备访问:")
    print(f"   API 地址: http://{local_ip}:11435")
    print(f"   示例调用: http://{local_ip}:11435/api/tags")
    print(f"\n⚠️  确保防火墙已开放 11435 端口")
    print("-" * 50)


# ===========================
# 主程序
# ===========================

if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════════╗
    ║     Ollama API 调用示例程序                ║
    ║     支持本地和内网调用                     ║
    ╚════════════════════════════════════════════╝
    """)

    # 显示网络信息
    print_network_info()

    # 运行示例
    example_local_call()
    # example_intranet_call()  # 取消注释以测试内网调用
    # example_stream_call()  # 取消注释以测试流式输出

    # 打印 cURL 示例
    print_curl_examples()

    print("\n✅ 示例执行完成！")
    print(f"💡 提示: 其他设备可使用 http://{get_local_ip()}:11435 访问")
