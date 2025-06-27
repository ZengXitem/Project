# 🌐 Flask Web SSH 客户端

一个功能完整的基于Flask的纯Web SSH客户端，让你可以在浏览器中轻松连接和操作远程Linux/Ubuntu系统。

![项目状态](https://img.shields.io/badge/状态-稳定运行-brightgreen)
![Python版本](https://img.shields.io/badge/Python-3.13+-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## ✨ 功能特性

- 🌐 **纯Web界面**：基于Flask，无需前端构建，开箱即用
- 🔐 **安全连接**：支持密码和私钥两种认证方式
- 💾 **连接管理**：保存和管理多个SSH连接配置，支持加密存储
- 🎨 **现代界面**：响应式设计，支持桌面和移动端访问
- ⚡ **实时终端**：基于Xterm.js和WebSocket的全功能终端
- 🔒 **数据安全**：密码和私钥采用AES加密存储
- 🚀 **一键启动**：智能依赖管理，解决版本兼容性问题
- 🛠️ **故障诊断**：详细的错误信息和解决建议

## 技术栈

- **后端**: Python + Flask + Flask-SocketIO + Paramiko + SQLAlchemy
- **前端**: 纯HTML/CSS/JavaScript + Xterm.js + Socket.IO
- **数据库**: SQLite（加密存储）
- **通信**: WebSocket实现实时交互

## 🚀 快速启动

### 方法一：一键启动（强烈推荐）
```bash
# 克隆项目
git clone <your-repo-url>
cd Project

# 一键启动
python3 flask-start.py
```

**🎯 一键启动的优势：**
- ✅ 自动安装所有兼容版本的依赖
- ✅ 解决Python 3.13版本兼容性问题
- ✅ 智能端口检测，自动使用可用端口
- ✅ 自动启动Flask服务器
- ✅ 自动打开浏览器访问应用
- ✅ 完整的错误处理和故障排除

### 方法二：手动启动

#### 1. 安装依赖
```bash
pip install -r requirements.txt
```

#### 2. 启动服务
```bash
cd backend
python3 app.py
```

#### 3. 访问应用
打开浏览器访问: http://localhost:5555

> 💡 **提示**: 默认端口已从5000改为5555，避免与macOS AirPlay服务冲突

## 📖 使用说明

### 1. 🔗 创建SSH连接
- **连接名称**: 为连接起一个便于识别的名称
- **主机地址**: 输入服务器IP地址或域名
- **端口**: SSH端口（默认22）
- **用户名**: SSH登录用户名
- **认证方式**: 选择密码认证或私钥认证
- **操作**: 点击"保存连接"保存配置，或"直接连接"立即连接

### 2. 📋 管理连接
- **查看列表**: 所有已保存的连接都会显示在连接列表中
- **快速连接**: 点击"连接"按钮一键建立SSH会话
- **删除连接**: 点击"删除"按钮移除不需要的连接
- **连接状态**: 实时显示连接状态和错误信息

### 3. 💻 终端操作
- **命令执行**: 在终端中输入任何Linux/Unix命令
- **实时输出**: 命令输出实时显示，支持颜色和格式
- **键盘支持**: 支持所有标准终端快捷键
- **会话保持**: 连接保持活跃，支持长时间操作

### 4. 🔧 故障排除
当连接失败时，系统会自动显示：
- **详细错误信息**: 具体的失败原因
- **解决建议**: 针对性的故障排除步骤
- **常见问题**: 认证失败、网络问题等解决方案

## 📁 项目结构

```
Project/
├── backend/
│   ├── app.py              # Flask主应用（包含前端HTML）
│   ├── config.py           # 配置文件
│   └── instance/
│       └── ssh_connections.db  # SQLite数据库（加密存储）
├── requirements.txt        # Python依赖（兼容版本）
├── flask-start.py         # 一键启动脚本
├── LICENSE                # MIT许可证
└── README.md              # 项目文档
```

### 核心文件说明
- **`backend/app.py`**: 主应用文件，包含Flask后端和HTML前端
- **`flask-start.py`**: 智能启动脚本，自动处理依赖和兼容性
- **`requirements.txt`**: 精心调试的兼容版本依赖列表
- **`ssh_connections.db`**: 加密的连接配置数据库

## 版本兼容性

本项目已解决Python 3.13版本兼容性问题：
- SQLAlchemy: 1.4.53（兼容版本）
- Flask-SQLAlchemy: 3.0.5（兼容版本）
- Eventlet: 0.33.3（兼容版本）

## API接口

- `GET /` - 主页面
- `GET /api/connections` - 获取连接列表
- `POST /api/connections` - 创建新连接
- `DELETE /api/connections/:id` - 删除连接

## WebSocket事件

- `ssh_connect` - 直接连接SSH
- `ssh_connect_saved` - 使用保存的连接
- `ssh_command` - 发送命令
- `ssh_disconnect` - 断开连接
- `ssh_output` - 接收输出
- `ssh_error` - 错误信息

## 安全说明

- 密码和私钥使用AES加密存储
- 建议只在受信任的环境中使用
- 生产环境下请修改默认的加密密钥
- 建议使用HTTPS协议部署

## 🔧 故障排除

### 常见问题解决方案

#### 问题1：SQLAlchemy版本兼容性错误
```
AssertionError: Class <class 'sqlalchemy.sql.elements.SQLCoreOperations'> directly inherits TypingOnly
```
**✅ 解决方案**: 使用 `flask-start.py` 自动安装兼容版本

#### 问题2：端口被占用
```
Address already in use / Port 5555 is in use
```
**✅ 解决方案**: 
```bash
# 查找占用进程
lsof -i :5555
# 杀死进程
kill -9 <PID>
# 或者修改app.py中的端口号
```

#### 问题3：SSH认证失败
```
Authentication failed / 认证失败
```
**✅ 解决方案**:
1. 检查用户名和密码是否正确
2. 确认服务器允许密码认证
3. 尝试使用普通用户而不是root用户
4. 检查服务器SSH配置 `/etc/ssh/sshd_config`
5. 如果服务器只允许密钥认证，请使用私钥方式

#### 问题4：依赖安装失败
```
Could not find a version that satisfies the requirement
```
**✅ 解决方案**:
```bash
# 使用信任的源
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
# 或者使用一键启动脚本
python3 flask-start.py
```

#### 问题5：Xterm.js终端无法显示
```
Terminal is not defined
```
**✅ 解决方案**: 已修复CDN链接，使用更可靠的unpkg源

## 🧪 测试连接

### 创建测试连接示例：
```
连接名称: 我的云服务器
主机地址: 192.168.1.100
端口: 22
用户名: ubuntu
认证方式: 密码认证
密码: your_password
```

### 支持的系统：
- ✅ Ubuntu/Debian
- ✅ CentOS/RHEL
- ✅ Alpine Linux
- ✅ macOS
- ✅ 其他Unix-like系统

## 🚀 部署说明

### 开发环境
```bash
# 直接运行
python3 flask-start.py
```

### 生产环境部署
```bash
# 安装gunicorn
pip install gunicorn

# 使用gunicorn部署
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5555 backend.app:app

# 或者使用systemd服务
sudo systemctl enable web-ssh
sudo systemctl start web-ssh
```

### Docker部署（可选）
```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 5555
CMD ["python3", "backend/app.py"]
```

## 🌟 项目亮点

- 🎯 **零配置启动**：一键运行，无需复杂配置
- 🔧 **智能故障排除**：自动诊断并提供解决方案
- 🛡️ **安全第一**：AES加密存储，安全可靠
- 📱 **跨平台支持**：支持桌面和移动端访问
- ⚡ **高性能**：基于WebSocket的实时通信
- 🎨 **用户友好**：现代化界面，操作简单直观

## 🎉 成功案例

✅ **已测试并成功运行在：**
- macOS (Python 3.13)
- Ubuntu 20.04/22.04
- CentOS 7/8
- 各种云服务器环境

现在你可以在浏览器中愉快地管理你的Linux/Ubuntu服务器了！🚀

## 许可证

MIT License