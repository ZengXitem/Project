# Web SSH 客户端 - 用户认证功能指南

## 功能概述

Web SSH 客户端现在已经集成了完整的用户认证系统，提供以下功能：

- 🔐 用户注册和登录
- 👤 基于用户的SSH连接管理
- 🔒 密码安全加密存储
- 🚪 会话管理和登出功能
- 🛡️ 数据隔离（用户只能访问自己的连接）

## 快速开始

### 1. 初始化系统

首次运行时，系统会自动创建数据库并生成默认管理员账户：

```bash
python flask-start.py
```

### 2. 默认管理员账户

- **用户名**: `admin`
- **密码**: `admin123`

⚠️ **建议**: 首次登录后立即修改密码（功能待实现）

### 3. 注册新账户

1. 访问 http://localhost:5555
2. 点击"注册"按钮
3. 填写注册信息：
   - 用户名（至少3个字符）
   - 邮箱地址
   - 密码（至少6个字符）
   - 确认密码

## 主要功能

### 用户管理

#### 注册
- 用户名唯一性检查
- 邮箱格式验证
- 密码强度要求
- 自动登录

#### 登录
- 支持用户名或邮箱登录
- 密码安全验证
- 会话管理
- 登录状态保持

#### 登出
- 安全清除会话
- 自动断开SSH连接
- 返回登录界面

### SSH连接管理

#### 连接隔离
- 每个用户只能看到和管理自己的SSH连接
- 无法访问其他用户的连接配置
- 数据完全隔离

#### 连接操作
- 创建新连接（需要登录）
- 连接到已保存的服务器
- 删除连接
- 测试连接

## 安全特性

### 密码安全
- 使用SHA256 + 盐值哈希存储用户密码
- SSH连接密码和私钥使用Fernet加密
- 敏感信息不以明文存储

### 会话管理
- 基于Flask Session的认证
- 自动过期机制
- 安全的登出流程

### 数据隔离
- 用户级别的数据访问控制
- API层面的权限验证
- WebSocket连接权限检查

## API端点

### 认证相关
- `POST /api/register` - 用户注册
- `POST /api/login` - 用户登录
- `POST /api/logout` - 用户登出
- `GET /api/auth/check` - 检查登录状态
- `GET /api/user/profile` - 获取用户资料

### SSH连接相关（需要登录）
- `GET /api/connections` - 获取用户的SSH连接列表
- `POST /api/connections` - 创建新的SSH连接
- `DELETE /api/connections/{id}` - 删除指定连接
- `POST /api/connections/test` - 测试连接

## 数据库结构

### User 表
```sql
CREATE TABLE user (
    id INTEGER PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(200) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
);
```

### SSHConnection 表（已修改）
```sql
CREATE TABLE ssh_connection (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    host VARCHAR(100) NOT NULL,
    port INTEGER DEFAULT 22,
    username VARCHAR(100) NOT NULL,
    password TEXT,  -- 加密存储
    private_key TEXT,  -- 加密存储
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER NOT NULL,  -- 新增：用户关联
    FOREIGN KEY (user_id) REFERENCES user (id)
);
```

## 迁移现有数据

如果您之前已经有SSH连接数据，初始化脚本会：

1. 自动创建默认管理员用户
2. 将所有孤立的SSH连接分配给管理员用户
3. 保持现有连接的完整性

## 故障排除

### 常见问题

#### 1. 登录失败
- 检查用户名/邮箱是否正确
- 确认密码是否正确
- 确保账户未被禁用

#### 2. 注册失败
- 用户名可能已存在
- 邮箱可能已被注册
- 密码不符合要求

#### 3. 连接权限错误
- 确保已登录
- 只能访问自己创建的连接
- 会话可能已过期，请重新登录

#### 4. 数据库初始化失败
```bash
cd backend
python init_db.py
```

### 重置数据库
⚠️ **警告**: 这将删除所有用户和连接数据

```bash
cd backend
rm instance/ssh_connections.db
python init_db.py
```

## 技术实现细节

### 前端
- 基于原有的Web界面增强
- 动态显示登录/登出状态
- 响应式的认证界面
- 实时的用户状态管理

### 后端
- Flask-SQLAlchemy ORM
- 基于装饰器的权限控制
- 加密的密码存储
- 安全的会话管理

### 数据加密
- 用户密码：SHA256 + 随机盐值
- SSH密码/私钥：Fernet对称加密
- 会话数据：Flask Session加密

## 未来计划

- [ ] 用户资料编辑
- [ ] 密码修改功能
- [ ] 用户头像上传
- [ ] 更详细的用户权限管理
- [ ] 登录日志记录
- [ ] 两步验证支持

## 支持

如果您遇到问题或有建议，请：

1. 检查本文档的故障排除部分
2. 查看控制台日志输出
3. 提交Issue报告

---

## 更新日志

### v2.0.0 (当前版本)
- ✅ 添加用户注册登录功能
- ✅ 实现基于用户的SSH连接管理
- ✅ 数据安全加密存储
- ✅ 会话管理和权限控制
- ✅ 数据库迁移支持 