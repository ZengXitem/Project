#!/usr/bin/env python3
"""
数据库初始化脚本
为现有的SSH连接项目添加用户认证功能
"""

import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# 添加后端目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, SSHConnection, hash_password

def migrate_database():
    """迁移数据库结构"""
    try:
        # 检查ssh_connection表是否存在user_id字段
        with db.engine.connect() as conn:
            result = conn.execute(db.text("PRAGMA table_info(ssh_connection)"))
            columns = [row[1] for row in result]
        
        if 'user_id' not in columns:
            print("🔄 检测到旧版本数据库，正在升级...")
            
            # 添加user_id字段
            with db.engine.connect() as conn:
                conn.execute(db.text("ALTER TABLE ssh_connection ADD COLUMN user_id INTEGER"))
                conn.execute(db.text("ALTER TABLE ssh_connection ADD COLUMN updated_at TIMESTAMP"))
                conn.commit()
            print("✅ 已添加user_id和updated_at字段")
            
            # 创建默认管理员用户
            admin_user = User(
                username='admin',
                email='admin@localhost',
                password_hash=hash_password('admin123'),
                is_active=True
            )
            db.session.add(admin_user)
            db.session.commit()
            print("✅ 创建默认管理员用户: admin / admin123")
            
            # 将所有现有连接关联到管理员用户
            with db.engine.connect() as conn:
                conn.execute(db.text(f"UPDATE ssh_connection SET user_id = :user_id WHERE user_id IS NULL"), 
                           {'user_id': admin_user.id})
                conn.commit()
            print("✅ 已将现有SSH连接关联到管理员用户")
            
            return True
        
        return False
        
    except Exception as e:
        # 如果表不存在或其他错误，继续正常流程
        print(f"⚠️  数据库迁移检查: {e}")
        return False

def init_database():
    """初始化数据库"""
    print("🔧 正在初始化数据库...")
    
    with app.app_context():
        try:
            # 检查数据库是否需要迁移
            if migrate_database():
                print("✅ 数据库迁移完成")
            
            # 创建所有表
            db.create_all()
            print("✅ 数据库表创建成功")
            
            # 确保存在默认管理员用户
            admin_user = User.query.filter_by(username='admin').first()
            if not admin_user:
                admin_user = User(
                    username='admin',
                    email='admin@localhost',
                    password_hash=hash_password('admin123'),
                    is_active=True
                )
                db.session.add(admin_user)
                db.session.commit()
                print("✅ 创建默认管理员用户: admin / admin123")
            
            # 检查是否有现有的SSH连接但没有用户关联
            orphaned_connections = SSHConnection.query.filter_by(user_id=None).all()
            
            if orphaned_connections:
                print(f"⚠️  发现 {len(orphaned_connections)} 个未关联用户的SSH连接")
                
                # 将孤立的连接分配给管理员用户
                for conn in orphaned_connections:
                    conn.user_id = admin_user.id
                
                db.session.commit()
                print(f"✅ 已将 {len(orphaned_connections)} 个SSH连接分配给管理员用户")
            
            # 显示数据库统计信息
            user_count = User.query.count()
            connection_count = SSHConnection.query.count()
            
            print("\n📊 数据库统计:")
            print(f"   用户数量: {user_count}")
            print(f"   SSH连接数量: {connection_count}")
            
            if user_count == 0:
                print("\n🎉 这是一个全新的安装！")
                print("👉 请使用以下信息创建您的第一个账户")
                print("   或者使用默认管理员账户登录")
                print("   用户名: admin")
                print("   密码: admin123")
            
            print("\n✅ 数据库初始化完成!")
            
        except Exception as e:
            print(f"❌ 数据库初始化失败: {e}")
            return False
    
    return True

def create_sample_user():
    """创建示例用户"""
    with app.app_context():
        try:
            # 检查是否已存在示例用户
            if User.query.filter_by(username='demo').first():
                print("示例用户已存在")
                return
            
            # 创建示例用户
            demo_user = User(
                username='demo',
                email='demo@example.com',
                password_hash=hash_password('demo123'),
                is_active=True
            )
            
            db.session.add(demo_user)
            db.session.commit()
            
            print("✅ 创建示例用户成功:")
            print("   用户名: demo")
            print("   密码: demo123")
            
        except Exception as e:
            print(f"❌ 创建示例用户失败: {e}")

if __name__ == '__main__':
    print("🚀 Web SSH 客户端 - 数据库初始化")
    print("=" * 50)
    
    if init_database():
        print("\n🎉 数据库初始化成功！")
        print("现在可以运行应用程序了：")
        print("python app.py")
    else:
        print("\n❌ 数据库初始化失败")
        sys.exit(1) 