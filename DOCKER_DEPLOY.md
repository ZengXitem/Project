# 🐳 Docker 部署指南

Web SSH Terminal 提供了两种Docker部署方式，满足不同的使用场景。

## 🚀 快速开始

### 方式一：从GitHub仓库直接部署 ⭐ **推荐**

如果你想直接使用最新版本，无需下载代码：

```bash
# 下载GitHub版本部署脚本
curl -O https://raw.githubusercontent.com/ZengXitem/web-ssh-terminal/main/docker-github.sh
chmod +x docker-github.sh

# 一键部署
./docker-github.sh run
```

### 方式二：本地代码部署

如果你已经克隆了代码仓库：

```bash
# 克隆仓库
git clone https://github.com/ZengXitem/web-ssh-terminal.git
cd web-ssh-terminal

# 一键部署
./docker-run.sh run
```

## 📋 部署方式对比

| 特性 | GitHub版本 | 本地版本 |
|------|------------|----------|
| **适用场景** | 快速体验，生产部署 | 开发调试，定制修改 |
| **代码来源** | ✅ 直接从GitHub拉取最新代码 | ❌ 使用本地代码 |
| **更新方式** | `./docker-github.sh update` | 需要手动拉取代码 |
| **网络要求** | 需要访问GitHub | 仅需要拉取Docker镜像 |
| **镜像大小** | ~200MB | ~200MB |
| **启动速度** | 首次较慢（需下载代码） | 较快 |

## 🎯 GitHub版本详细使用

### 安装和运行

```bash
# 方法1: 直接下载脚本
curl -O https://raw.githubusercontent.com/ZengXitem/web-ssh-terminal/main/docker-github.sh
chmod +x docker-github.sh

# 方法2: 或者克隆仓库
git clone https://github.com/ZengXitem/web-ssh-terminal.git
cd web-ssh-terminal
```

### 常用命令

```bash
# 构建并运行（默认）
./docker-github.sh run

# 仅构建镜像
./docker-github.sh build

# 查看运行状态
./docker-github.sh status

# 查看实时日志
./docker-github.sh logs

# 更新到最新版本
./docker-github.sh update

# 停止服务
./docker-github.sh stop

# 重启服务
./docker-github.sh restart

# 进入容器调试
./docker-github.sh shell

# 完全清理（包括数据）
./docker-github.sh clean

# 查看帮助
./docker-github.sh help
```

## 🏠 本地版本详细使用

### 安装和运行

```bash
# 克隆仓库
git clone https://github.com/ZengXitem/web-ssh-terminal.git
cd web-ssh-terminal

# 构建并运行
./docker-run.sh run
```

### 常用命令

```bash
# 构建并运行（默认）
./docker-run.sh run

# 仅构建镜像
./docker-run.sh build

# 查看运行状态
./docker-run.sh status

# 查看实时日志
./docker-run.sh logs

# 停止服务
./docker-run.sh stop

# 重启服务
./docker-run.sh restart

# 进入容器调试
./docker-run.sh shell

# 完全清理（包括数据）
./docker-run.sh clean
```

## 🔧 Docker Compose 部署

### 基础部署

```bash
# 使用docker-compose
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 带Nginx反向代理部署

```bash
# 启用Nginx代理（80端口访问）
docker-compose --profile with-nginx up -d

# 访问地址变为: http://localhost
```

## 🌐 访问应用

部署成功后，访问以下地址：

- **直接访问**: http://localhost:5555
- **Nginx代理**: http://localhost （需启用nginx profile）

## 📊 资源使用

### 系统要求

- **内存**: 最少512MB，推荐1GB+
- **存储**: 最少1GB可用空间
- **CPU**: 1核心以上
- **网络**: 需要访问目标SSH服务器

### 容器资源

```bash
# 查看容器资源使用情况
docker stats web-ssh-terminal

# 或者GitHub版本
docker stats web-ssh-terminal-github
```

## 🔒 安全配置

### 生产环境建议

1. **使用HTTPS**:
   ```bash
   # 修改nginx.conf启用SSL配置
   # 添加SSL证书到./ssl/目录
   ```

2. **限制访问**:
   ```bash
   # 仅允许本地访问
   docker run -p 127.0.0.1:5555:5555 ...
   
   # 或使用防火墙限制端口访问
   ```

3. **数据备份**:
   ```bash
   # 备份SSH连接配置
   docker run --rm -v ssh_data:/data -v $(pwd):/backup alpine \
     tar czf /backup/ssh_backup.tar.gz -C /data .
   ```

## 🐛 故障排除

### 常见问题

#### 1. 端口被占用
```bash
# 查看端口占用
lsof -i :5555

# 修改端口
export PORT=8080
./docker-github.sh run
```

#### 2. 构建失败
```bash
# 清理Docker缓存
docker system prune -a

# 重新构建
./docker-github.sh clean
./docker-github.sh run
```

#### 3. 无法访问GitHub
```bash
# 使用本地版本
git clone https://github.com/ZengXitem/web-ssh-terminal.git
cd web-ssh-terminal
./docker-run.sh run
```

#### 4. 容器启动失败
```bash
# 查看详细日志
./docker-github.sh logs

# 检查容器状态
./docker-github.sh status

# 进入容器调试
./docker-github.sh shell
```

## 📈 性能优化

### 镜像优化

```dockerfile
# 多阶段构建（已实现）
FROM python:3.13-slim as base
# ... 构建阶段

FROM python:3.13-slim as runtime
# ... 运行阶段
```

### 容器优化

```bash
# 限制容器资源
docker run --memory=512m --cpus=1.0 ...

# 使用生产级WSGI服务器
# 已集成eventlet支持
```

## 🔄 更新和维护

### 自动更新

```bash
# GitHub版本自动更新
./docker-github.sh update

# 本地版本手动更新
git pull
./docker-run.sh clean
./docker-run.sh run
```

### 数据迁移

```bash
# 导出数据
docker run --rm -v ssh_data:/data -v $(pwd):/backup alpine \
  tar czf /backup/ssh_backup.tar.gz -C /data .

# 导入数据
docker run --rm -v ssh_data:/data -v $(pwd):/backup alpine \
  tar xzf /backup/ssh_backup.tar.gz -C /data
```

## 📞 技术支持

如果遇到问题，请：

1. 查看 [GitHub Issues](https://github.com/ZengXitem/web-ssh-terminal/issues)
2. 提交新的Issue描述问题
3. 包含以下信息：
   - 操作系统版本
   - Docker版本
   - 错误日志
   - 复现步骤

---

🎉 **享受你的Web SSH Terminal体验！** 