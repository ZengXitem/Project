# Web SSH 客户端 - 快速开始指南

## 项目简介

Web SSH 客户端是一个基于Web的SSH终端管理工具，支持用户认证、连接管理和实时终端交互。

## 系统要求

- Python 3.8+ 或 Docker
- 现代浏览器（Chrome、Firefox、Safari、Edge）

## 启动方式

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

## 首次使用

1. **访问地址**：http://localhost:5555

2. **默认管理员账户**：
   - 用户名：`admin`
   - 密码：`admin123`

3. **注册新用户**：点击"注册"按钮创建新账户

## 主要功能

### 用户管理
- 用户注册和登录
- 密码安全加密存储
- 多用户数据隔离

### SSH连接
- 创建和管理SSH连接配置
- 支持密码和私钥认证
- 连接测试功能
- 实时终端交互

## 常见问题

### Python启动问题
如果`flask-start.py`执行失败：
```bash
# 手动安装依赖
pip install -r requirements.txt

# 初始化数据库
cd backend
python init_db.py

# 启动应用
python app.py
```

### Docker启动问题
如果Docker启动失败：
```bash
# 检查Docker服务
docker info

# 重新构建
docker-compose build --no-cache

# 查看日志
docker-compose logs
```

### 端口占用
如果端口5555被占用：
- 修改`backend/app.py`中的端口号
- 或停止占用端口的程序

## 管理命令

### Python 环境
```bash
# 停止服务：Ctrl+C

# 重启服务
cd backend && python app.py
```

### Docker 环境
```bash
# 停止服务
docker-compose down

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 重启服务
docker-compose restart
```

## 数据备份

### Python 环境
```bash
cp -r backend/instance backup/
```

### Docker 环境
```bash
docker cp $(docker-compose ps -q):/app/backend/instance ./backup/
```

## 安全建议

1. 修改默认管理员密码
2. 仅在受信任的网络环境中使用
3. 定期备份用户数据
4. 生产环境建议使用HTTPS

---

## 技术支持

如遇问题请查看：
1. 本文档的常见问题部分
2. 控制台错误日志
3. [用户认证指南](USER_AUTH_GUIDE.md) 