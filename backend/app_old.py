from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO, emit, disconnect
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import paramiko
import threading
import time
import os
from datetime import datetime
import json
import base64
from cryptography.fernet import Fernet

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ssh_connections.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 配置CORS允许所有来源
CORS(app, origins="*", resources={r"/*": {"origins": "*"}})

db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# 加密密钥
ENCRYPTION_KEY = Fernet.generate_key()
cipher_suite = Fernet(ENCRYPTION_KEY)

# 数据库模型
class SSHConnection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    host = db.Column(db.String(100), nullable=False)
    port = db.Column(db.Integer, default=22)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.Text)  # 加密存储
    private_key = db.Column(db.Text)  # 加密存储
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# 存储活跃的SSH连接
active_connections = {}

class SSHManager:
    def __init__(self, session_id):
        self.session_id = session_id
        self.ssh_client = None
        self.shell = None
        self.connected = False
        
    def connect(self, host, port, username, password=None, private_key=None):
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # 详细的连接信息
            print(f"尝试连接: {username}@{host}:{port}")
            
            if private_key:
                # 使用私钥连接
                from io import StringIO
                key_file = StringIO(private_key)
                try:
                    key = paramiko.RSAKey.from_private_key(key_file)
                    print("使用RSA私钥认证")
                except:
                    try:
                        key_file.seek(0)
                        key = paramiko.DSAKey.from_private_key(key_file)
                        print("使用DSA私钥认证")
                    except:
                        try:
                            key_file.seek(0)
                            key = paramiko.ECDSAKey.from_private_key(key_file)
                            print("使用ECDSA私钥认证")
                        except:
                            key_file.seek(0)
                            key = paramiko.Ed25519Key.from_private_key(key_file)
                            print("使用Ed25519私钥认证")
                
                self.ssh_client.connect(host, port=port, username=username, pkey=key, timeout=15)
            else:
                # 使用密码连接
                print("使用密码认证")
                self.ssh_client.connect(
                    host, 
                    port=port, 
                    username=username, 
                    password=password, 
                    timeout=15,
                    allow_agent=False,
                    look_for_keys=False
                )
            
            self.shell = self.ssh_client.invoke_shell()
            self.shell.settimeout(0.1)
            self.connected = True
            
            print(f"SSH连接成功: {username}@{host}:{port}")
            
            # 启动输出监听线程
            threading.Thread(target=self._read_output, daemon=True).start()
            
            return True
        except paramiko.AuthenticationException as e:
            error_msg = f"认证失败: 用户名或密码错误，或服务器不允许此认证方式"
            print(f"SSH认证错误: {e}")
            socketio.emit('ssh_error', {'error': error_msg}, room=self.session_id)
            return False
        except paramiko.SSHException as e:
            error_msg = f"SSH连接错误: {str(e)}"
            print(f"SSH连接错误: {e}")
            socketio.emit('ssh_error', {'error': error_msg}, room=self.session_id)
            return False
        except Exception as e:
            error_msg = f"连接失败: {str(e)}"
            print(f"连接错误: {e}")
            socketio.emit('ssh_error', {'error': error_msg}, room=self.session_id)
            return False
    
    def _read_output(self):
        while self.connected and self.shell:
            try:
                if self.shell.recv_ready():
                    output = self.shell.recv(1024).decode('utf-8', errors='ignore')
                    socketio.emit('ssh_output', {'data': output}, room=self.session_id)
                time.sleep(0.01)
            except Exception as e:
                print(f"读取输出错误: {e}")
                break
    
    def send_command(self, command):
        if self.shell and self.connected:
            try:
                self.shell.send(command.encode('utf-8'))
                return True
            except Exception as e:
                print(f"发送命令错误: {e}")
                return False
        return False
    
    def disconnect(self):
        self.connected = False
        if self.shell:
            try:
                self.shell.close()
            except:
                pass
        if self.ssh_client:
            try:
                self.ssh_client.close()
            except:
                pass

# HTML模板
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Web SSH 客户端</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.7.2/socket.io.js"></script>
    <script src="https://unpkg.com/xterm@5.3.0/lib/xterm.js"></script>
    <link rel="stylesheet" href="https://unpkg.com/xterm@5.3.0/css/xterm.css">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f0f2f5; height: 100vh; overflow: hidden; }
        
        /* 顶部导航栏 */
        .header { 
            background: #2c3e50; 
            color: white; 
            padding: 0.8rem 1.5rem; 
            display: flex; 
            justify-content: space-between; 
            align-items: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            z-index: 1000;
        }
        .header h1 { 
            margin: 0; 
            font-size: 1.5rem; 
            display: flex; 
            align-items: center; 
            gap: 0.5rem;
        }
        .header-actions {
            display: flex;
            gap: 0.5rem;
        }
        
        /* 主容器 */
        .main-container { 
            display: flex; 
            height: calc(100vh - 64px); 
        }
        
        /* 左侧连接列表栏 */
        .sidebar { 
            width: 300px; 
            background: white; 
            border-right: 1px solid #e1e8ed;
            display: flex;
            flex-direction: column;
            transition: margin-left 0.3s ease;
        }
        .sidebar.collapsed {
            margin-left: -300px;
        }
        
        .sidebar-header {
            padding: 1rem;
            border-bottom: 1px solid #e1e8ed;
            background: #f8f9fa;
        }
        .sidebar-header h3 {
            color: #2c3e50;
            margin: 0;
            font-size: 1.1rem;
        }
        
        .connections-list { 
            flex: 1;
            overflow-y: auto;
            padding: 0.5rem 0;
        }
        .connection-item { 
            padding: 0.8rem 1rem; 
            margin: 0.2rem 0.5rem;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s ease;
            border-left: 3px solid transparent;
        }
        .connection-item:hover { 
            background: #f8f9fa; 
            border-left-color: #3498db;
        }
        .connection-item.active {
            background: #e3f2fd;
            border-left-color: #2196f3;
        }
        .connection-info { 
            display: flex;
            flex-direction: column;
            gap: 0.2rem;
        }
        .connection-name { 
            font-weight: 600; 
            color: #2c3e50; 
            font-size: 0.9rem;
        }
        .connection-details { 
            color: #7f8c8d; 
            font-size: 0.8rem; 
        }
        .connection-status-indicator {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #95a5a6;
            margin-left: auto;
            margin-top: 0.2rem;
        }
        .connection-status-indicator.connected {
            background: #27ae60;
        }
        
        .empty-connections {
            padding: 2rem 1rem;
            text-align: center;
            color: #7f8c8d;
        }
        .empty-connections .icon {
            font-size: 3rem;
            margin-bottom: 1rem;
            opacity: 0.3;
        }
        
        /* 右侧终端区域 */
        .terminal-container { 
            flex: 1; 
            display: flex;
            flex-direction: column;
            background: white;
        }
        
        .terminal-header { 
            padding: 1rem 1.5rem; 
            border-bottom: 1px solid #e1e8ed;
            display: flex; 
            justify-content: space-between; 
            align-items: center;
            background: #f8f9fa;
        }
        .terminal-title {
            font-weight: 600;
            color: #2c3e50;
        }
        .connection-status { 
            padding: 0.4rem 0.8rem; 
            border-radius: 20px; 
            font-size: 0.8rem;
            font-weight: 500;
        }
        .status-connected { 
            background: #d5f4e6; 
            color: #27ae60; 
        }
        .status-disconnected { 
            background: #fadbd8; 
            color: #e74c3c; 
        }
        .status-connecting {
            background: #fff3cd;
            color: #856404;
        }
        
        .terminal-content {
            flex: 1;
            position: relative;
        }
        #terminal { 
            width: 100%;
            height: 100%;
            background: #1e1e1e;
        }
        
        /* 按钮样式 */
        .btn { 
            padding: 0.5rem 1rem; 
            border: none; 
            border-radius: 4px; 
            cursor: pointer; 
            font-size: 0.9rem; 
            transition: all 0.2s ease;
            font-weight: 500;
        }
        .btn-primary { 
            background: #3498db; 
            color: white; 
        }
        .btn-primary:hover { 
            background: #2980b9; 
        }
        .btn-success { 
            background: #27ae60; 
            color: white; 
        }
        .btn-success:hover { 
            background: #219a52; 
        }
        .btn-danger { 
            background: #e74c3c; 
            color: white; 
        }
        .btn-danger:hover { 
            background: #c0392b; 
        }
        .btn-secondary { 
            background: #95a5a6; 
            color: white; 
        }
        .btn-secondary:hover { 
            background: #7f8c8d; 
        }
        .btn-outline {
            background: transparent;
            border: 1px solid #ddd;
            color: #666;
        }
        .btn-outline:hover {
            background: #f8f9fa;
        }
        
        /* 新建连接表单模态框 */
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 2000;
        }
        .modal.show {
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .modal-content {
            background: white;
            border-radius: 8px;
            padding: 2rem;
            width: 90%;
            max-width: 500px;
            max-height: 80vh;
            overflow-y: auto;
        }
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
        }
        .modal-header h3 {
            margin: 0;
            color: #2c3e50;
        }
        .close-btn {
            background: none;
            border: none;
            font-size: 1.5rem;
            cursor: pointer;
            color: #7f8c8d;
        }
        .close-btn:hover {
            color: #2c3e50;
        }
        
        .form-group { 
            margin-bottom: 1rem; 
        }
        .form-group label { 
            display: block; 
            margin-bottom: 0.5rem; 
            font-weight: 600; 
            color: #34495e; 
        }
        .form-group input, .form-group select, .form-group textarea { 
            width: 100%; 
            padding: 0.75rem; 
            border: 1px solid #ddd; 
            border-radius: 4px; 
            font-size: 1rem; 
        }
        .form-group input:focus, .form-group select:focus, .form-group textarea:focus { 
            outline: none; 
            border-color: #3498db; 
        }
        
        .form-row { 
            display: flex; 
            gap: 1rem; 
        }
        .form-row .form-group { 
            flex: 1; 
        }
        
        .auth-method textarea { 
            height: 100px; 
            font-family: monospace; 
            resize: vertical;
        }
        
        .form-actions {
            display: flex;
            gap: 0.5rem;
            justify-content: flex-end;
            margin-top: 1.5rem;
        }
        
        .hidden { 
            display: none !important; 
        }
        
        /* 响应式设计 */
        @media (max-width: 768px) {
            .sidebar {
                width: 280px;
            }
            .header h1 {
                font-size: 1.2rem;
            }
            .form-row { 
                flex-direction: column; 
            }
            .modal-content {
                padding: 1.5rem;
                margin: 1rem;
            }
        }
        
        /* 滚动条样式 */
        .connections-list::-webkit-scrollbar {
            width: 6px;
        }
        .connections-list::-webkit-scrollbar-track {
            background: #f1f1f1;
        }
        .connections-list::-webkit-scrollbar-thumb {
            background: #c1c1c1;
            border-radius: 3px;
        }
        .connections-list::-webkit-scrollbar-thumb:hover {
            background: #a8a8a8;
        }
    </style>
</head>
<body>
    <!-- 顶部导航栏 -->
    <div class="header">
        <h1>🖥️ Web SSH 客户端</h1>
        <div class="header-actions">
            <button class="btn btn-primary" onclick="showNewConnectionModal()">+ 新建连接</button>
            <button class="btn btn-outline" onclick="toggleSidebar()" id="toggleSidebarBtn">📋 连接列表</button>
        </div>
    </div>
    
    <!-- 主容器 -->
    <div class="main-container">
        <!-- 左侧连接列表栏 -->
        <div class="sidebar" id="sidebar">
            <div class="sidebar-header">
                <h3>SSH 连接</h3>
            </div>
            <div class="connections-list" id="connectionsList">
                <div class="empty-connections">
                    <div class="icon">📁</div>
                    <p>暂无SSH连接</p>
                    <p>点击"新建连接"创建第一个SSH连接</p>
                </div>
            </div>
        </div>
        
        <!-- 右侧终端区域 -->
        <div class="terminal-container">
            <div class="terminal-header">
                <div class="terminal-title" id="terminalTitle">SSH 终端</div>
                <div style="display: flex; align-items: center; gap: 1rem;">
                    <div class="connection-status status-disconnected" id="connectionStatus">未连接</div>
                    <button class="btn btn-danger hidden" onclick="disconnect()" id="disconnectBtn">断开连接</button>
                </div>
            </div>
            <div class="terminal-content">
                <div id="terminal"></div>
            </div>
        </div>
    </div>
    
    <!-- 新建连接模态框 -->
    <div class="modal" id="newConnectionModal">
        <div class="modal-content">
            <div class="modal-header">
                <h3>新建SSH连接</h3>
                <button class="close-btn" onclick="hideNewConnectionModal()">&times;</button>
            </div>
            <form id="connectionForm">
                <div class="form-row">
                    <div class="form-group">
                        <label>连接名称</label>
                        <input type="text" id="connectionName" placeholder="例如：我的服务器" required>
                    </div>
                    <div class="form-group">
                        <label>主机地址</label>
                        <input type="text" id="host" placeholder="IP地址或域名" required>
                    </div>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label>端口</label>
                        <input type="number" id="port" value="22" required>
                    </div>
                    <div class="form-group">
                        <label>用户名</label>
                        <input type="text" id="username" placeholder="SSH用户名" required>
                    </div>
                </div>
                
                <div class="form-group">
                    <label>认证方式</label>
                    <select id="authMethod" onchange="toggleAuthMethod()">
                        <option value="password">密码认证</option>
                        <option value="key">私钥认证</option>
                    </select>
                </div>
                
                <div id="passwordAuth" class="auth-method">
                    <div class="form-group">
                        <label>密码</label>
                        <input type="password" id="password" placeholder="SSH密码">
                    </div>
                </div>
                
                <div id="keyAuth" class="auth-method hidden">
                    <div class="form-group">
                        <label>私钥内容</label>
                        <textarea id="privateKey" placeholder="粘贴私钥内容..."></textarea>
                    </div>
                </div>
                
                <div class="form-actions">
                    <button type="button" class="btn btn-secondary" onclick="hideNewConnectionModal()">取消</button>
                    <button type="button" class="btn btn-success" onclick="connectDirect()">直接连接</button>
                    <button type="submit" class="btn btn-primary">保存连接</button>
                </div>
            </form>
        </div>
    </div>

    <script>
        // 全局变量
        let socket = null;
        let terminal = null;
        let connections = [];
        let isConnected = false;
        let currentConnectionId = null;
        let sidebarVisible = true;

        // 初始化
        document.addEventListener('DOMContentLoaded', function() {
            initializeSocket();
            initializeTerminal();
            loadConnections();
            
            document.getElementById('connectionForm').addEventListener('submit', saveConnection);
            
            // 点击模态框背景关闭
            document.getElementById('newConnectionModal').addEventListener('click', function(e) {
                if (e.target === this) {
                    hideNewConnectionModal();
                }
            });
        });

        // 初始化Socket连接
        function initializeSocket() {
            socket = io();
            
            socket.on('connect', function() {
                console.log('Socket连接成功');
            });
            
            socket.on('ssh_connected', function(data) {
                isConnected = true;
                updateConnectionStatus('已连接', true);
                updateTerminalTitle(data.connection_name || data.host, data.username, data.host);
                document.getElementById('disconnectBtn').classList.remove('hidden');
                terminal.write('\\r\\n✅ 连接成功! 主机: ' + data.host + '\\r\\n');
                
                // 更新连接状态指示器
                if (currentConnectionId) {
                    updateConnectionIndicator(currentConnectionId, true);
                }
                
                // 隐藏新建连接模态框
                hideNewConnectionModal();
            });
            
            socket.on('ssh_output', function(data) {
                terminal.write(data.data);
            });
            
            socket.on('ssh_error', function(data) {
                isConnected = false;
                updateConnectionStatus('连接错误: ' + data.error, false);
                terminal.write('\\r\\n❌ 错误: ' + data.error + '\\r\\n');
                
                // 显示故障排除提示
                if (data.error.includes('认证失败') || data.error.includes('Authentication failed')) {
                    terminal.write('\\r\\n💡 故障排除提示:\\r\\n');
                    terminal.write('1. 检查用户名和密码是否正确\\r\\n');
                    terminal.write('2. 确认服务器允许密码认证\\r\\n');
                    terminal.write('3. 尝试使用普通用户而不是root用户\\r\\n');
                    terminal.write('4. 检查服务器SSH配置(/etc/ssh/sshd_config)\\r\\n');
                    terminal.write('5. 如果服务器只允许密钥认证，请使用私钥方式\\r\\n');
                }
            });
            
            socket.on('ssh_disconnected', function() {
                isConnected = false;
                updateConnectionStatus('未连接', false);
                updateTerminalTitle('SSH 终端');
                document.getElementById('disconnectBtn').classList.add('hidden');
                terminal.write('\\r\\n🔌 连接已断开\\r\\n');
                
                // 更新连接状态指示器
                if (currentConnectionId) {
                    updateConnectionIndicator(currentConnectionId, false);
                    currentConnectionId = null;
                }
                
                // 清除活跃状态
                document.querySelectorAll('.connection-item.active').forEach(item => {
                    item.classList.remove('active');
                });
            });
        }

        // 初始化终端
        function initializeTerminal() {
            terminal = new Terminal({
                rows: 24,
                cols: 80,
                theme: {
                    background: '#000000',
                    foreground: '#ffffff'
                }
            });
            
            terminal.open(document.getElementById('terminal'));
            terminal.write('Web SSH 客户端已就绪，请建立连接...\\r\\n');
            
            // 监听键盘输入
            terminal.onData(function(data) {
                if (isConnected) {
                    socket.emit('ssh_command', {command: data});
                }
            });
        }

        // 加载已保存的连接
        function loadConnections() {
            fetch('/api/connections')
                .then(response => response.json())
                .then(data => {
                    connections = data;
                    renderConnectionsList();
                })
                .catch(error => console.error('加载连接失败:', error));
        }

        // 渲染连接列表
        function renderConnectionsList() {
            const listElement = document.getElementById('connectionsList');
            if (connections.length === 0) {
                listElement.innerHTML = `
                    <div class="empty-connections">
                        <div class="icon">📁</div>
                        <p>暂无SSH连接</p>
                        <p>点击"新建连接"创建第一个SSH连接</p>
                    </div>
                `;
                return;
            }
            
            listElement.innerHTML = connections.map(conn => `
                <div class="connection-item" onclick="connectSaved(${conn.id})" oncontextmenu="showConnectionMenu(event, ${conn.id})">
                    <div class="connection-info">
                        <div class="connection-name">${conn.name}</div>
                        <div class="connection-details">${conn.username}@${conn.host}:${conn.port}</div>
                    </div>
                    <div class="connection-status-indicator" id="indicator-${conn.id}"></div>
                </div>
            `).join('');
        }

        // 切换认证方式
        function toggleAuthMethod() {
            const authMethod = document.getElementById('authMethod').value;
            const passwordAuth = document.getElementById('passwordAuth');
            const keyAuth = document.getElementById('keyAuth');
            
            if (authMethod === 'password') {
                passwordAuth.classList.remove('hidden');
                keyAuth.classList.add('hidden');
            } else {
                passwordAuth.classList.add('hidden');
                keyAuth.classList.remove('hidden');
            }
        }

        // 保存连接
        function saveConnection(event) {
            event.preventDefault();
            
            const connectionData = {
                name: document.getElementById('connectionName').value,
                host: document.getElementById('host').value,
                port: parseInt(document.getElementById('port').value),
                username: document.getElementById('username').value,
                password: document.getElementById('authMethod').value === 'password' ? document.getElementById('password').value : '',
                private_key: document.getElementById('authMethod').value === 'key' ? document.getElementById('privateKey').value : ''
            };
            
            fetch('/api/connections', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(connectionData)
            })
            .then(response => response.json())
            .then(data => {
                alert('连接保存成功!');
                hideNewConnectionModal();
                loadConnections();
            })
            .catch(error => {
                console.error('保存连接失败:', error);
                alert('保存连接失败: ' + error.message);
            });
        }

        // 直接连接
        function connectDirect() {
            const connectionData = {
                host: document.getElementById('host').value,
                port: parseInt(document.getElementById('port').value),
                username: document.getElementById('username').value,
                password: document.getElementById('authMethod').value === 'password' ? document.getElementById('password').value : '',
                private_key: document.getElementById('authMethod').value === 'key' ? document.getElementById('privateKey').value : ''
            };
            
            if (!connectionData.host || !connectionData.username) {
                alert('请填写主机地址和用户名');
                return;
            }
            
            // 断开当前连接
            if (isConnected) {
                disconnect();
            }
            
            currentConnectionId = null;
            
            // 清除活跃状态
            document.querySelectorAll('.connection-item.active').forEach(item => {
                item.classList.remove('active');
            });
            
            terminal.clear();
            terminal.write('🔄 正在连接 ' + connectionData.host + '...\\r\\n');
            updateConnectionStatus('连接中...', false);
            updateTerminalTitle('连接中...');
            
            socket.emit('ssh_connect', connectionData);
        }

        // 使用保存的连接
        function connectSaved(connectionId) {
            // 如果已经连接到这个服务器，则不重复连接
            if (currentConnectionId === connectionId && isConnected) {
                return;
            }
            
            // 断开当前连接
            if (isConnected) {
                disconnect();
            }
            
            currentConnectionId = connectionId;
            
            // 更新UI状态
            document.querySelectorAll('.connection-item.active').forEach(item => {
                item.classList.remove('active');
            });
            document.querySelector(`[onclick="connectSaved(${connectionId})"]`).classList.add('active');
            
            terminal.clear();
            terminal.write('🔄 正在连接...\\r\\n');
            updateConnectionStatus('连接中...', false);
            updateTerminalTitle('连接中...');
            
            socket.emit('ssh_connect_saved', {connection_id: connectionId});
        }

        // 断开连接
        function disconnect() {
            socket.emit('ssh_disconnect');
        }

        // 删除连接
        function deleteConnection(connectionId) {
            if (!confirm('确定要删除这个连接吗？')) return;
            
            fetch(`/api/connections/${connectionId}`, {method: 'DELETE'})
                .then(() => {
                    alert('连接删除成功!');
                    loadConnections();
                })
                .catch(error => {
                    console.error('删除连接失败:', error);
                    alert('删除连接失败');
                });
        }

        // 更新连接状态
        function updateConnectionStatus(message, connected) {
            const statusElement = document.getElementById('connectionStatus');
            statusElement.className = 'connection-status ' + (connected ? 'status-connected' : 'status-disconnected');
            statusElement.textContent = message;
        }
        
        // 更新终端标题
        function updateTerminalTitle(title, username = '', host = '') {
            const titleElement = document.getElementById('terminalTitle');
            if (username && host) {
                titleElement.textContent = `${title} - ${username}@${host}`;
            } else {
                titleElement.textContent = title;
            }
        }
        
        // 更新连接状态指示器
        function updateConnectionIndicator(connectionId, connected) {
            const indicator = document.getElementById(`indicator-${connectionId}`);
            if (indicator) {
                if (connected) {
                    indicator.classList.add('connected');
                } else {
                    indicator.classList.remove('connected');
                }
            }
        }
        
        // 显示新建连接模态框
        function showNewConnectionModal() {
            document.getElementById('newConnectionModal').classList.add('show');
            document.getElementById('connectionName').focus();
        }
        
        // 隐藏新建连接模态框
        function hideNewConnectionModal() {
            document.getElementById('newConnectionModal').classList.remove('show');
            document.getElementById('connectionForm').reset();
            toggleAuthMethod(); // 重置认证方式显示
        }
        
        // 切换侧边栏显示/隐藏
        function toggleSidebar() {
            const sidebar = document.getElementById('sidebar');
            const toggleBtn = document.getElementById('toggleSidebarBtn');
            
            sidebarVisible = !sidebarVisible;
            
            if (sidebarVisible) {
                sidebar.classList.remove('collapsed');
                toggleBtn.textContent = '📋 连接列表';
            } else {
                sidebar.classList.add('collapsed');
                toggleBtn.textContent = '📋 显示列表';
            }
        }
        
        // 显示连接右键菜单（删除功能）
        function showConnectionMenu(event, connectionId) {
            event.preventDefault();
            event.stopPropagation();
            
            if (confirm('确定要删除这个连接吗？')) {
                deleteConnection(connectionId);
            }
        }
    </script>
</body>
</html>
'''

# 路由
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/connections', methods=['GET'])
def get_connections():
    try:
        connections = SSHConnection.query.all()
        result = []
        for conn in connections:
            result.append({
                'id': conn.id,
                'name': conn.name,
                'host': conn.host,
                'port': conn.port,
                'username': conn.username,
                'created_at': conn.created_at.isoformat(),
                'updated_at': conn.updated_at.isoformat()
            })
        return jsonify(result)
    except Exception as e:
        print(f"获取连接列表错误: {e}")
        return jsonify([])

@app.route('/api/connections', methods=['POST'])
def create_connection():
    try:
        data = request.get_json()
        
        # 加密敏感数据
        encrypted_password = None
        if data.get('password'):
            encrypted_password = cipher_suite.encrypt(data['password'].encode()).decode()
        
        encrypted_private_key = None
        if data.get('private_key'):
            encrypted_private_key = cipher_suite.encrypt(data['private_key'].encode()).decode()
        
        connection = SSHConnection(
            name=data['name'],
            host=data['host'],
            port=data.get('port', 22),
            username=data['username'],
            password=encrypted_password,
            private_key=encrypted_private_key
        )
        
        db.session.add(connection)
        db.session.commit()
        
        return jsonify({
            'id': connection.id,
            'name': connection.name,
            'host': connection.host,
            'port': connection.port,
            'username': connection.username,
            'created_at': connection.created_at.isoformat()
        }), 201
    except Exception as e:
        print(f"创建连接错误: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/connections/<int:conn_id>', methods=['DELETE'])
def delete_connection(conn_id):
    try:
        connection = db.session.get(SSHConnection, conn_id)
        if not connection:
            return jsonify({'error': 'Connection not found'}), 404
        db.session.delete(connection)
        db.session.commit()
        return '', 204
    except Exception as e:
        print(f"删除连接错误: {e}")
        return jsonify({'error': str(e)}), 500

# WebSocket事件处理
@socketio.on('connect')
def handle_connect():
    print(f'客户端连接: {request.sid}')
    emit('connected', {'data': 'Connected to server'})

@socketio.on('disconnect')
def handle_disconnect():
    print(f'客户端断开: {request.sid}')
    if request.sid in active_connections:
        active_connections[request.sid].disconnect()
        del active_connections[request.sid]

@socketio.on('ssh_connect')
def handle_ssh_connect(data):
    session_id = request.sid
    print(f'SSH连接请求: {data}')
    
    # 如果已经有连接，先断开
    if session_id in active_connections:
        active_connections[session_id].disconnect()
    
    # 创建新的SSH管理器
    ssh_manager = SSHManager(session_id)
    
    # 连接SSH
    if ssh_manager.connect(
        data['host'], 
        data.get('port', 22), 
        data['username'], 
        password=data.get('password'),
        private_key=data.get('private_key')
    ):
        active_connections[session_id] = ssh_manager
        emit('ssh_connected', {
            'status': 'connected',
            'host': data['host'],
            'username': data['username']
        })
    else:
        emit('ssh_error', {'error': 'Failed to connect'})

@socketio.on('ssh_connect_saved')
def handle_ssh_connect_saved(data):
    """使用保存的连接配置进行连接"""
    session_id = request.sid
    conn_id = data['connection_id']
    print(f'使用保存的连接: {conn_id}')
    
    try:
        connection = db.session.get(SSHConnection, conn_id)
        if not connection:
            emit('ssh_error', {'error': 'Connection not found'})
            return
        
        # 如果已经有连接，先断开
        if session_id in active_connections:
            active_connections[session_id].disconnect()
        
        # 创建新的SSH管理器
        ssh_manager = SSHManager(session_id)
        
        # 解密密码
        password = None
        if connection.password:
            password = cipher_suite.decrypt(connection.password.encode()).decode()
        
        private_key = None
        if connection.private_key:
            private_key = cipher_suite.decrypt(connection.private_key.encode()).decode()
        
        # 连接SSH
        if ssh_manager.connect(
            connection.host, 
            connection.port, 
            connection.username, 
            password=password,
            private_key=private_key
        ):
            active_connections[session_id] = ssh_manager
            emit('ssh_connected', {
                'status': 'connected',
                'connection_name': connection.name,
                'host': connection.host,
                'username': connection.username
            })
        else:
            emit('ssh_error', {'error': 'Failed to connect'})
    except Exception as e:
        print(f"保存连接错误: {e}")
        emit('ssh_error', {'error': str(e)})

@socketio.on('ssh_command')
def handle_ssh_command(data):
    session_id = request.sid
    if session_id in active_connections:
        active_connections[session_id].send_command(data['command'])

@socketio.on('ssh_disconnect')
def handle_ssh_disconnect():
    session_id = request.sid
    if session_id in active_connections:
        active_connections[session_id].disconnect()
        del active_connections[session_id]
        emit('ssh_disconnected', {'status': 'disconnected'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("数据库已创建")
    
    print("启动Flask Web SSH客户端...")
    print("访问地址: http://localhost:5555")
    socketio.run(app, host='0.0.0.0', port=5555, debug=True, allow_unsafe_werkzeug=True) 