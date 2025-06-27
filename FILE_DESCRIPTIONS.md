# 📁 项目文件说明

> 详细介绍每个文件的作用和使用方法，帮助开发者快速理解项目结构。

## 🗂️ 文件目录结构

```
web-ssh-terminal/
├── 📁 backend/                    # 后端核心代码
│   ├── 🐍 app.py                  # Flask主应用 [核心]
│   ├── 📁 templates/
│   │   └── 🌐 index.html          # HTML模板 [界面]
│   ├── 📁 static/
│   │   ├── 🎨 style.css           # CSS样式 [界面美化]
│   │   └── ⚡ script.js           # JavaScript逻辑 [前端交互]
│   ├── 🔧 reset_db.py             # 数据库重置工具 [维护]
│   └── 📁 instance/               # 数据存储目录
│       ├── 🗄️ ssh_connections.db  # SQLite数据库 [自动生成]
│       └── 🔐 encryption.key      # 加密密钥 [自动生成]
├── 🚀 flask-start.py             # 一键启动脚本 [推荐入口]
├── 📋 requirements.txt           # Python依赖列表 [环境配置]
├── 🐳 Docker相关文件/
│   ├── 📦 Dockerfile             # 本地Docker构建 [容器化]
│   ├── 📦 Dockerfile.github      # GitHub Docker构建 [远程部署]
│   ├── 🔧 docker-run.sh          # Docker部署脚本 [本地容器]
│   ├── 🔧 docker-github.sh       # GitHub Docker脚本 [远程容器]
│   ├── 🔧 docker-github-fixed.sh # 修复版GitHub脚本 [问题修复]
│   ├── 🐙 docker-compose.yml     # Docker Compose配置 [编排]
│   ├── 🌐 nginx.conf             # Nginx配置 [反向代理]
│   └── 🚫 .dockerignore          # Docker忽略文件 [构建优化]
├── 📚 文档文件/
│   ├── 📖 README.md              # 项目主文档 [入门必读]
│   ├── 📝 PROJECT_SUMMARY.md     # 项目总结 [详细介绍]
│   ├── 🐳 DOCKER_DEPLOY.md       # Docker部署指南 [容器部署]
│   ├── 🎉 DEPLOYMENT_SUCCESS.md  # 部署成功总结 [状态报告]
│   └── 📁 FILE_DESCRIPTIONS.md   # 本文件 [文件说明]
└── ⚖️ LICENSE                    # MIT许可证 [法律文件]
```

---

## 🔥 核心文件详解

### 🐍 `backend/app.py` - Flask主应用
**作用**：项目的核心文件，包含所有后端逻辑
**重要性**：⭐⭐⭐⭐⭐ (必需)
**内容**：
- Flask应用配置和路由
- SSH连接管理API
- WebSocket事件处理
- 数据库模型定义
- 加密存储逻辑

**快速定位**：
```bash
# 查看应用入口
head -50 backend/app.py

# 查看API路由
grep -n "@app.route" backend/app.py
```

### 🚀 `flask-start.py` - 一键启动脚本
**作用**：智能启动脚本，自动处理依赖和兼容性问题
**重要性**：⭐⭐⭐⭐⭐ (推荐入口)
**功能**：
- 自动检测Python版本
- 自动安装兼容版本依赖
- 智能端口检测
- 自动打开浏览器
- 完整错误处理

**使用方法**：
```bash
# 直接运行（推荐）
python3 flask-start.py

# 查看脚本内容
cat flask-start.py
```

### 🌐 `backend/templates/index.html` - HTML模板
**作用**：Web界面的HTML结构
**重要性**：⭐⭐⭐⭐ (界面核心)
**特性**：
- 响应式设计
- 现代化UI组件
- 左侧连接列表 + 右侧终端布局
- 模态框表单设计

**自定义界面**：
```bash
# 编辑HTML模板
nano backend/templates/index.html

# 重启应用查看效果
python3 flask-start.py
```

---

## 🐳 Docker文件详解

### 📦 `Dockerfile` vs `Dockerfile.github`
| 文件 | 用途 | 代码来源 | 推荐场景 |
|------|------|----------|----------|
| `Dockerfile` | 本地构建 | 本地代码 | 开发、测试 ⭐⭐⭐⭐⭐ |
| `Dockerfile.github` | 远程构建 | GitHub仓库 | 生产部署 ⭐⭐⭐ |

### 🔧 Docker脚本对比
| 脚本 | 功能 | 状态 | 使用场景 |
|------|------|------|----------|
| `docker-run.sh` | 本地Docker部署 | ✅ 稳定 | **推荐使用** |
| `docker-github.sh` | GitHub Docker部署 | ⚠️ 凭据问题 | 需要修复 |
| `docker-github-fixed.sh` | 修复版GitHub部署 | 🔧 实验性 | 问题调试 |

**使用建议**：
```bash
# 推荐：使用本地版本
./docker-run.sh run

# 查看所有可用命令
./docker-run.sh help
```

---

## 📚 文档文件导航

### 📖 主要文档
| 文档 | 适合人群 | 内容重点 | 阅读时间 |
|------|----------|----------|----------|
| `README.md` | 所有用户 | 快速入门、功能介绍 | 5分钟 ⭐⭐⭐⭐⭐ |
| `PROJECT_SUMMARY.md` | 开发者 | 技术架构、实现细节 | 10分钟 ⭐⭐⭐⭐ |
| `DOCKER_DEPLOY.md` | 运维人员 | Docker部署方案 | 8分钟 ⭐⭐⭐⭐ |
| `DEPLOYMENT_SUCCESS.md` | 用户 | 部署状态报告 | 3分钟 ⭐⭐⭐ |

### 📋 文档阅读路线

**🔰 新手用户**：
1. [README.md](README.md) - 了解项目和快速开始
2. 运行 `python3 flask-start.py` - 体验功能
3. [故障排除](#-故障排除) - 解决问题

**🐳 Docker用户**：
1. [DOCKER_DEPLOY.md](DOCKER_DEPLOY.md) - Docker部署指南
2. 运行 `./docker-run.sh run` - 容器部署
3. [DEPLOYMENT_SUCCESS.md](DEPLOYMENT_SUCCESS.md) - 确认状态

**👨‍💻 开发者**：
1. [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - 技术架构
2. [FILE_DESCRIPTIONS.md](FILE_DESCRIPTIONS.md) - 文件结构
3. `backend/app.py` - 核心代码

---

## 🔧 维护和自定义

### 🛠️ 常用维护文件
| 文件 | 作用 | 使用场景 |
|------|------|----------|
| `backend/reset_db.py` | 重置数据库 | 清理连接配置 |
| `requirements.txt` | 依赖管理 | 环境配置 |
| `.dockerignore` | Docker优化 | 减小镜像体积 |

### 🎨 自定义指南

**修改界面样式**：
```bash
# 编辑CSS样式
nano backend/static/style.css

# 编辑JavaScript逻辑
nano backend/static/script.js
```

**修改后端逻辑**：
```bash
# 编辑Flask应用
nano backend/app.py

# 重启应用
python3 flask-start.py
```

**重置数据**：
```bash
# 重置数据库
cd backend
python3 reset_db.py
```

---

## 🚀 快速操作指南

### 常用命令速查

**启动应用**：
```bash
python3 flask-start.py          # 一键启动（推荐）
./docker-run.sh run            # Docker启动
docker-compose up -d           # Compose启动
```

**查看状态**：
```bash
./docker-run.sh status         # Docker状态
curl http://localhost:5555     # 应用状态
lsof -i :5555                  # 端口状态
```

**故障排除**：
```bash
./docker-run.sh logs           # 查看日志
./docker-run.sh clean          # 清理重建
python3 backend/reset_db.py    # 重置数据
```

### 🔗 重要链接

- **🌐 本地访问**：http://localhost:5555
- **📖 主文档**：[README.md](README.md)
- **🐳 Docker指南**：[DOCKER_DEPLOY.md](DOCKER_DEPLOY.md)
- **💻 GitHub仓库**：https://github.com/ZengXitem/web-ssh-terminal
- **⚖️ 许可证**：[LICENSE](LICENSE)

---

**💡 提示**：如果你是第一次使用，建议从 [README.md](README.md) 开始阅读，然后运行 `python3 flask-start.py` 快速体验！ 