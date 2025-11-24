# Ollama 内网 LLM 部署方案

使用 Docker 部署 Ollama，支持内网设备访问的离线 LLM 解决方案。

## 📋 目录结构

```
MIAT_offline_llm/
├── docker-compose.yml      # Docker 编排配置
├── api_examples.py         # API 调用示例代码
└── README.md              # 部署说明文档
```

## 🚀 快速开始

### 前置要求

1. **Docker & Docker Compose** 已安装
   - Windows: [Docker Desktop](https://www.docker.com/products/docker-desktop/)
   - Linux: `sudo apt-get install docker.io docker-compose`

2. **NVIDIA GPU 驱动**（可选，使用 GPU 加速）
   - 安装 NVIDIA Docker Runtime: [nvidia-docker](https://github.com/NVIDIA/nvidia-docker)

### 步骤 1: 启动服务

```bash
# 启动 Ollama 服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 步骤 2: 下载 gpt-oss:20b 模型

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

### 步骤 3: 获取内网 IP 地址

```bash
# Windows
ipconfig

# Linux/Mac
ifconfig
# 或
ip addr show
```

找到你的内网 IP 地址，通常是 `192.168.x.x` 或 `10.x.x.x` 格式。

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
```

示例代码会自动显示你的内网 IP 和访问地址。

### 手动调用示例

**本地调用**:
```python
import requests

response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "gpt-oss:20b",
        "prompt": "什么是人工智能？",
        "stream": False
    }
)

print(response.json()['response'])
```

**从其他内网设备调用**（替换 `192.168.1.100` 为实际服务器 IP）:
```python
import requests

response = requests.post(
    "http://192.168.1.100:11434/api/generate",
    json={
        "model": "gpt-oss:20b",
        "prompt": "什么是人工智能？",
        "stream": False
    }
)

print(response.json()['response'])
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

**3. 内网调用（替换为实际服务器 IP）**
```bash
curl http://192.168.1.100:11434/api/generate -d '{
  "model": "gpt-oss:20b",
  "prompt": "Hello from intranet!",
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

## 🌐 内网访问配置

### 从其他设备访问 LLM

1. **确认服务器内网 IP**
   - 假设服务器 IP 是 `192.168.1.100`

2. **确保防火墙开放端口**

   **Windows 防火墙**:
   ```powershell
   # PowerShell（管理员权限）
   New-NetFirewallRule -DisplayName "Ollama API" -Direction Inbound -LocalPort 11434 -Protocol TCP -Action Allow
   ```

   **Linux 防火墙**:
   ```bash
   # ufw
   sudo ufw allow 11434/tcp

   # firewalld
   sudo firewall-cmd --permanent --add-port=11434/tcp
   sudo firewall-cmd --reload
   ```

3. **从其他设备测试连接**
   ```bash
   # 测试连接
   curl http://192.168.1.100:11434/api/tags
   ```

### 内网设备配置示例

**从手机/平板访问**:
- 确保设备连接到同一个内网（同一个 Wi-Fi）
- 使用浏览器访问: `http://192.168.1.100:11434/api/tags`

**从其他电脑访问**:
```python
import requests

SERVER_IP = "192.168.1.100"
API_URL = f"http://{SERVER_IP}:11434"

# 测试连接
response = requests.get(f"{API_URL}/api/tags")
print(response.json())
```

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

数据保存在 Docker volume 中：
- `ollama_data`: 存储模型文件

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

### 问题 2: 内网设备无法访问

**可能原因**: 防火墙阻止或网络配置问题

**解决方案**:
```bash
# 1. 检查服务是否运行
docker-compose ps

# 2. 检查端口是否开放
netstat -an | grep 11434

# 3. 在服务器上测试本地访问
curl http://localhost:11434/api/tags

# 4. 检查防火墙
# Windows: 控制面板 -> Windows Defender 防火墙 -> 高级设置
# Linux: sudo ufw status
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

**优化内网访问速度**:
- 使用有线连接而非 Wi-Fi
- 确保路由器性能足够
- 考虑使用千兆网络交换机

## 🔐 安全建议

1. **内网访问控制**
   - 只在受信任的内网中开放服务
   - 不要将端口暴露到公网

2. **添加认证**（可选）
   - 考虑在 API 前添加认证层（nginx + basic auth）
   - 或使用 VPN 访问内网

3. **监控使用量**
   - 定期检查 Ollama 日志
   - 监控异常请求

4. **防火墙配置**
   - 只开放必要的端口（11434）
   - 限制访问来源 IP 范围

## 📱 移动设备访问示例

### Android/iOS 应用示例

可以使用任何支持 HTTP 请求的应用或自己开发：

```javascript
// JavaScript/React Native 示例
const SERVER_IP = "192.168.1.100";

fetch(`http://${SERVER_IP}:11434/api/generate`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    model: 'gpt-oss:20b',
    prompt: '你好',
    stream: false
  })
})
.then(response => response.json())
.then(data => console.log(data.response));
```

## 📚 相关资源

- [Ollama 官方文档](https://github.com/ollama/ollama)
- [Ollama API 文档](https://github.com/ollama/ollama/blob/main/docs/api.md)
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
