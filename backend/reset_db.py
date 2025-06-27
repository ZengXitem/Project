#!/usr/bin/env python3
"""
数据库重置脚本
用于清理旧的加密数据，解决加密密钥不匹配的问题
"""

import os
import sys

def reset_database():
    """重置数据库和加密密钥"""
    
    # 数据库文件路径
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'ssh_connections.db')
    key_path = os.path.join(os.path.dirname(__file__), 'instance', 'encryption.key')
    
    print("🔄 重置数据库和加密密钥...")
    
    # 删除数据库文件
    if os.path.exists(db_path):
        os.remove(db_path)
        print("✅ 已删除旧数据库文件")
    else:
        print("ℹ️ 数据库文件不存在")
    
    # 删除加密密钥文件
    if os.path.exists(key_path):
        os.remove(key_path)
        print("✅ 已删除旧加密密钥")
    else:
        print("ℹ️ 加密密钥文件不存在")
    
    print("🎉 重置完成！")
    print("📝 下次启动应用时将创建新的数据库和加密密钥")
    print("⚠️ 需要重新保存所有SSH连接配置")

if __name__ == '__main__':
    print("=" * 50)
    print("🗃️ Flask Web SSH 数据库重置工具")
    print("=" * 50)
    
    confirm = input("确定要重置数据库吗？这将删除所有保存的连接配置 (y/N): ")
    
    if confirm.lower() in ['y', 'yes']:
        reset_database()
    else:
        print("❌ 取消重置操作") 