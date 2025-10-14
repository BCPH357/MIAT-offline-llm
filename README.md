# Ollama + Ngrok 离线 LLM 部署方案

使用 Docker 部署 Ollama，并通过 Ngrok 实现外网访问的完整解决方案。

## 📋 目录结构

```
MIAT_offline_llm/
├── docker-compose.yml      # Docker 编排配置
├── .env.example           # 环境变量模板
├── api_examples.py        # API 调用示例代码
└── README.md             # 部署说明文档
```

## 🚀 快速开始

### 前置要求

1. **Docker & Docker Compose** 已安装
   - Windows: [Docker Desktop](https://www.docker.com/products/docker-desktop/)
   - Linux: `sudo apt-get install docker.io docker-compose`

2. **NVIDIA GPU 驱动** (如果使用 GPU)
   - 安装 NVIDIA Docker Runtime: [nvidia-docker](https://github.com/NVIDIA/nvidia-docker)

3. **Ngrok 账号**
   - 注册地址: https://dashboard.ngrok.com/signup
   - 获取 authtoken: https://dashboard.ngrok.com/get-started/your-authtoken

### 步骤 1: 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入你的 ngrok token
# NGROK_AUTHTOKEN=your_actual_token_here
```

### 步骤 2: 启动服务

```bash
# 启动 Ollama 和 Ngrok 服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 步骤 3: 下载 gpt-oss:20b 模型

服务启动后，需要进入 Ollama 容器下载模型：

```bash
# 进入 Ollama 容器
docker exec -it ollama_service bash

# 下载 gpt-oss:20b 模型（这可能需要一些时间）
ollama pull gpt-oss:20b

# 验证模型是否下载成功
ollama list

# 退出容器
exit
```

> ⚠️ **注意**: `gpt-oss:20b` 模型大小约 12-15GB，请确保有足够的磁盘空间和网络带宽。

### 步骤 4: 获取 Ngrok 公网地址

```bash
# 方法 1: 访问 Ngrok Web 界面
# 浏览器打开: http://localhost:4040

# 方法 2: 查看日志获取 URL
docker-compose logs ngrok | grep "url="
```

你会看到类似这样的输出：
```
url=https://xxxx-xx-xx-xxx-xxx.ngrok-free.app
```

这就是你的公网访问地址！

## 🔧 API 调用示例

### Python 调用示例

安装依赖：
```bash
pip install requests
```

运行示例代码：
```bash
# 本地调用测试
python api_examples.py

# 修改 api_examples.py 中的 NGROK_API_URL 后测试外网调用
```

### cURL 命令示例

**1. 本地调用 - Generate API**
```bash
curl http://localhost:11434/api/generate -d '{
  "model": "gpt-oss:20b",
  "prompt": "什么是人工智能？",
  "stream": false
}'
```

**2. 本地调用 - Chat API**
```bash
curl http://localhost:11434/api/chat -d '{
  "model": "gpt-oss:20b",
  "messages": [
    {"role": "user", "content": "你好，请介绍一下自己。"}
  ],
  "stream": false
}'
```

**3. 外网调用（替换为你的 ngrok URL）**
```bash
curl https://your-ngrok-url.ngrok-free.app/api/generate -d '{
  "model": "gpt-oss:20b",
  "prompt": "Hello from the internet!",
  "stream": false
}'
```

**4. 列出所有模型**
```bash
curl http://localhost:11434/api/tags
```

## 📡 API 端点说明

| 端点 | 说明 | 方法 |
|------|------|------|
| `/api/generate` | 文本生成接口 | POST |
| `/api/chat` | 对话接口 | POST |
| `/api/tags` | 列出所有模型 | GET |
| `/api/show` | 显示模型信息 | POST |
| `/api/pull` | 下载模型 | POST |

完整 API 文档: https://github.com/ollama/ollama/blob/main/docs/api.md

## 🌐 外网访问配置

### 从其他电脑调用 LLM

1. **获取 Ngrok URL**
   - 访问 `http://localhost:4040` 获取公网地址
   - 或查看日志: `docker-compose logs ngrok`

2. **使用公网地址调用**
   ```python
   import requests

   NGROK_URL = "https://your-url.ngrok-free.app"

   response = requests.post(
       f"{NGROK_URL}/api/generate",
       json={
           "model": "gpt-oss:20b",
           "prompt": "Hello from internet!",
           "stream": False
       }
   )

   print(response.json()['response'])
   ```

3. **在其他设备测试**
   - 使用相同的 ngrok URL 即可从任何联网设备访问

### Ngrok 免费版限制

- ✅ HTTP/HTTPS 隧道
- ✅ 随机子域名
- ⚠️ 连接限制: 40 连接/分钟
- ⚠️ 隧道会话时间: 8小时后需重启

如需更稳定的服务，建议升级 Ngrok 付费计划或使用其他内网穿透方案。

## 🛠️ 常用命令

### 服务管理

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 查看日志
docker-compose logs -f ollama
docker-compose logs -f ngrok

# 查看资源使用
docker stats
```

### 模型管理

```bash
# 进入容器
docker exec -it ollama_service bash

# 列出已安装模型
ollama list

# 下载新模型
ollama pull <model-name>

# 删除模型
ollama rm <model-name>

# 运行模型（交互式）
ollama run gpt-oss:20b
```

### 数据持久化

数据保存在 Docker volumes 中：
- `ollama_data`: 存储模型文件
- `ngrok_data`: 存储 ngrok 配置

```bash
# 查看 volumes
docker volume ls

# 备份 volume
docker run --rm -v ollama_data:/data -v $(pwd):/backup ubuntu tar czf /backup/ollama_backup.tar.gz /data

# 清理未使用的 volumes
docker volume prune
```

## 🔍 故障排除

### 问题 1: Ollama 服务无法启动

**可能原因**: GPU 驱动未安装

**解决方案**:
```bash
# 检查 NVIDIA 驱动
nvidia-smi

# 如果无 GPU，修改 docker-compose.yml，移除 GPU 配置
# 注释掉以下部分:
# deploy:
#   resources:
#     reservations:
#       devices:
#         - driver: nvidia
#           count: all
#           capabilities: [gpu]
```

### 问题 2: Ngrok 无法连接

**可能原因**: Token 未正确配置

**解决方案**:
```bash
# 检查 .env 文件
cat .env

# 确保 NGROK_AUTHTOKEN 已设置
# 重启服务
docker-compose restart ngrok
```

### 问题 3: 模型响应缓慢

**可能原因**:
- 模型太大，内存不足
- CPU 模式运行（未使用 GPU）

**解决方案**:
```bash
# 检查资源使用
docker stats

# 使用更小的模型
ollama pull gpt-oss:7b  # 更小的版本

# 确认 GPU 是否被使用
docker exec -it ollama_service nvidia-smi
```

### 问题 4: API 调用超时

**可能原因**: 首次调用需要加载模型到内存

**解决方案**:
- 增加请求超时时间（建议 300 秒）
- 预热模型: `docker exec -it ollama_service ollama run gpt-oss:20b "test"`

### 问题 5: Ngrok 连接断开

**原因**: 免费版 ngrok 隧道会话限制（8小时）

**解决方案**:
```bash
# 重启 ngrok 服务
docker-compose restart ngrok

# 获取新的 URL
docker-compose logs ngrok | grep "url="
```

## 📊 性能优化建议

### 1. GPU 加速

确保使用 NVIDIA GPU 运行：
```bash
# 验证 GPU 可用
docker exec -it ollama_service nvidia-smi

# 查看 GPU 使用情况
watch -n 1 nvidia-smi
```

### 2. 内存优化

如果内存不足，可以配置 Ollama 参数：
```yaml
# 在 docker-compose.yml 中添加环境变量
environment:
  - OLLAMA_NUM_PARALLEL=1
  - OLLAMA_MAX_LOADED_MODELS=1
```

### 3. 网络优化

使用 Ngrok 时可能遇到延迟，优化建议：
- 选择离你最近的 Ngrok 服务器区域
- 考虑升级 Ngrok 付费计划
- 或使用其他内网穿透工具（frp, cloudflare tunnel）

## 🔐 安全建议

1. **不要公开分享 Ngrok URL**
   - URL 暴露后任何人都可以访问你的 LLM

2. **添加认证**
   - 考虑在 API 前添加认证层（nginx + basic auth）

3. **监控使用量**
   - 定期检查 Ollama 日志
   - 设置 ngrok 访问限制

4. **环境变量安全**
   - 不要提交 `.env` 到 git
   - `.env` 已包含在 `.gitignore` 中

## 📚 相关资源

- [Ollama 官方文档](https://github.com/ollama/ollama)
- [Ollama API 文档](https://github.com/ollama/ollama/blob/main/docs/api.md)
- [Ngrok 文档](https://ngrok.com/docs)
- [Docker Compose 文档](https://docs.docker.com/compose/)

## 🆘 获取帮助

遇到问题？
1. 查看日志: `docker-compose logs`
2. 检查服务状态: `docker-compose ps`
3. 访问 Ollama GitHub Issues: https://github.com/ollama/ollama/issues

## 📝 许可证

本项目仅供学习和个人使用。

---

**祝你部署顺利！🎉**
