#!/usr/bin/env python3
"""
纯Flask Web SSH客户端启动脚本
解决所有依赖和版本兼容性问题
"""

import subprocess
import sys
import os
import time
import webbrowser
from threading import Timer

def run_command(command, description):
    """运行命令并显示结果"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            print(f"✅ {description}成功")
            return True
        else:
            print(f"❌ {description}失败: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏰ {description}超时")
        return False
    except Exception as e:
        print(f"❌ {description}出错: {e}")
        return False

def install_dependencies():
    """安装兼容版本的依赖"""
    print("📦 安装Python依赖（兼容版本）...")
    
    # 依赖列表 - 使用兼容版本
    dependencies = [
        "Flask==3.0.0",
        "Flask-SocketIO==5.3.6", 
        "Flask-CORS==4.0.0",
        "SQLAlchemy==1.4.53",  # 使用兼容版本
        "Flask-SQLAlchemy==3.0.5",  # 使用兼容版本
        "paramiko==3.4.0",
        "python-socketio==5.11.0",
        "eventlet==0.33.3",  # 使用兼容版本
        "cryptography==42.0.0",
        "python-dotenv==1.0.0"
    ]
    
    for dep in dependencies:
        success = run_command(
            f"python3 -m pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org '{dep}'",
            f"安装 {dep}"
        )
        if not success:
            print(f"⚠️  {dep} 安装失败，尝试继续...")

def open_browser():
    """延迟打开浏览器"""
    time.sleep(3)
    url = "http://localhost:5555"
    print(f"🔗 打开浏览器: {url}")
    webbrowser.open(url)

def main():
    print("🚀 Flask Web SSH 客户端启动工具")
    print("=" * 50)
    
    # 检查文件
    if not os.path.exists('backend/app.py'):
        print("❌ 错误: 找不到 backend/app.py 文件")
        sys.exit(1)
    
    # 安装依赖
    install_dependencies()
    
    print("\n🚀 启动Flask服务器...")
    
    # 启动浏览器（在后台线程中）
    browser_thread = Timer(3, open_browser)
    browser_thread.start()
    
    print("\n" + "=" * 50)
    print("✅ 准备启动服务!")
    print("🔗 Web SSH客户端: http://localhost:5555")
    print("=" * 50)
    print("\n🎉 浏览器将自动打开")
    print("📝 现在可以创建SSH连接并测试了！")
    print("\n按 Ctrl+C 停止服务")
    
    try:
        # 启动Flask应用
        os.chdir('backend')
        subprocess.run([sys.executable, 'app.py'], check=True)
    except KeyboardInterrupt:
        print("\n🛑 正在停止服务...")
        print("👋 再见!")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        print("\n🔧 尝试手动启动:")
        print("cd backend && python3 app.py")

if __name__ == '__main__':
    main() 