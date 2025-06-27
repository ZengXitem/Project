# ⚡ 快速入门指南

> **3分钟快速部署Web SSH Terminal，立即开始使用！**

## 🎯 我只想要...

### 💨 最快速度开始使用
```bash
# 1. 克隆项目（30秒）
git clone https://github.com/ZengXitem/web-ssh-terminal.git
cd web-ssh-terminal

# 2. 一键启动（60秒）
python3 flask-start.py

# 3. 打开浏览器（自动）
# http://localhost:5555
```
**✅ 完成！总共90秒**

### 🐳 Docker一键部署
```bash
# 1. 克隆项目
git clone https://github.com/ZengXitem/web-ssh-terminal.git
cd web-ssh-terminal

# 2. Docker部署
./docker-run.sh run

# 3. 访问应用
# http://localhost:5555
```
**✅ 完成！容器化部署**

---

## 🔧 首次使用步骤

### 第1步：创建SSH连接
1. 打开 http://localhost:5555
2. 点击 **"新建连接"** 按钮
3. 填写连接信息：
   ```
   连接名称: 我的服务器
   主机地址: 你的服务器IP
   端口: 22
   用户名: root 或其他用户
   认证方式: 密码认证
   密码: 你的密码
   ```
4. 点击 **"测试连接"** 验证
5. 点击 **"保存"** 保存配置

### 第2步：连接SSH
1. 在左侧连接列表中找到刚创建的连接
2. 点击连接名称
3. 等待连接建立
4. 开始在右侧终端中操作！

---

## 🚨 遇到问题？

### 问题1：端口被占用
```bash
# 查看占用进程
lsof -i :5555

# 杀死进程
kill -9 <进程ID>

# 重新启动
python3 flask-start.py
```

### 问题2：Python版本问题
```bash
# 检查Python版本
python3 --version

# 如果版本太低，安装Python 3.8+
# 或使用Docker部署：
./docker-run.sh run
```

### 问题3：依赖安装失败
```bash
# 使用信任源安装
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

# 或使用一键启动脚本（推荐）
python3 flask-start.py
```

### 问题4：SSH连接失败
1. **检查网络**：确保能ping通目标服务器
2. **检查端口**：确认SSH端口（通常是22）
3. **检查认证**：用户名和密码是否正确
4. **使用测试功能**：点击"测试连接"查看详细错误

---

## 📋 快速命令参考

### 应用控制
```bash
python3 flask-start.py      # 启动应用
Ctrl+C                      # 停止应用
```

### Docker控制
```bash
./docker-run.sh run         # 启动容器
./docker-run.sh stop        # 停止容器
./docker-run.sh logs        # 查看日志
./docker-run.sh status      # 查看状态
```

### 数据管理
```bash
cd backend
python3 reset_db.py         # 重置数据库（清空所有连接）
```

---

## 🌟 使用技巧

### 💡 连接管理技巧
- **批量管理**：可以保存多个服务器连接
- **快速连接**：左键单击连接名称即可连接
- **删除连接**：右键单击连接名称选择删除
- **连接测试**：保存前先测试连接确保配置正确

### 💡 终端使用技巧
- **复制粘贴**：支持标准的Ctrl+C/Ctrl+V
- **清屏**：输入`clear`或按Ctrl+L
- **历史命令**：使用上下箭头键浏览命令历史
- **多行编辑**：支持vim、nano等编辑器

### 💡 安全建议
- **密码安全**：密码使用AES加密存储
- **网络安全**：建议在内网环境使用
- **访问控制**：生产环境建议配置防火墙
- **定期备份**：重要配置建议定期备份

---

## 🔗 更多资源

- **📖 完整文档**：[README.md](README.md)
- **🐳 Docker指南**：[DOCKER_DEPLOY.md](DOCKER_DEPLOY.md)
- **📁 文件说明**：[FILE_DESCRIPTIONS.md](FILE_DESCRIPTIONS.md)
- **💻 GitHub仓库**：https://github.com/ZengXitem/web-ssh-terminal
- **🐛 问题反馈**：https://github.com/ZengXitem/web-ssh-terminal/issues

---

## 🎉 恭喜！

如果你已经成功启动应用并创建了第一个SSH连接，那么你已经掌握了Web SSH Terminal的基本使用方法！

**下一步可以**：
- 🌐 添加更多服务器连接
- 🛠️ 在终端中执行Linux命令
- 📚 阅读完整文档了解高级功能
- 🐳 尝试Docker部署获得更好的体验

**享受你的Web SSH Terminal之旅！** 🚀 