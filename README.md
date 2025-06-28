# Web SSH 客户端 v2.0 🚀

一个现代化的基于Web的SSH客户端，支持多用户认证、连接管理和实时终端交互。

## ✨ 主要特性

- 🔐 **用户注册登录系统** - 完整的用户认证功能
- 👤 **多用户支持** - 每个用户管理自己的SSH连接
- 🔒 **数据安全** - 密码和私钥加密存储
- 🖥️ **实时终端** - 基于WebSocket的SSH终端交互
- 📱 **响应式设计** - 支持移动设备访问

## 🚀 快速开始

### 方式一：Python 本地启动（推荐）

使用自动化脚本一键启动：

```bash
python flask-start.py
```

脚本会自动：
1. 安装Python依赖包
2. 初始化数据库
3. 启动Web服务
4. 打开浏览器

### 方式二：Docker 启动

如果遇到Python环境问题，使用Docker：

```bash
cd docker
docker-compose up -d
```

## 🖥️ 访问应用

启动完成后，自动打开浏览器访问：http://localhost:5555

### 🔑 首次使用

- **默认管理员账户：** `admin` / `admin123`
- **注册新用户：** 点击登录界面的"注册"按钮

> ⚠️ **安全提醒：** 首次登录后请立即修改默认密码

## 📚 使用指南

| 文档 | 描述 |
|------|------|
| [🏁 快速开始](docs/QUICK_START.md) | 详细的安装和使用指南 |
| [👤 用户认证指南](docs/USER_AUTH_GUIDE.md) | 用户管理功能说明 |

## 🌟 主要功能

### 👥 用户管理
- **用户注册：** 邮箱验证、密码强度检查
- **用户登录：** 支持用户名或邮箱登录
- **密码安全：** SHA256+盐值哈希存储
- **数据隔离：** 每个用户只能访问自己的SSH连接

### 🔐 SSH连接管理
- **连接配置：** 支持密码和私钥认证
- **加密存储：** SSH凭据使用Fernet加密
- **连接测试：** 创建前验证连接可用性
- **实时终端：** WebSocket基础的终端交互

## 🔧 技术栈

- **后端：** Flask + SocketIO + SQLAlchemy
- **前端：** HTML5 + CSS3 + JavaScript
- **终端：** Xterm.js + WebSocket
- **安全：** Fernet加密 + SHA256哈希
- **数据库：** SQLite

## 📝 常见问题

### Python启动问题
如果`flask-start.py`执行失败：
```bash
# 手动安装依赖
pip install -r requirements.txt

# 初始化数据库
cd backend && python init_db.py

# 启动应用
python app.py
```

### Docker启动问题
如果Docker启动失败：
```bash
# 重新构建
docker-compose build --no-cache

# 查看日志
docker-compose logs
```

### 端口占用
如果端口5555被占用，修改`backend/app.py`中的端口号

---

## 📄 许可证

本项目基于 MIT 许可证开源 - 查看 [LICENSE](LICENSE) 文件了解详情