from flask import Flask, request, jsonify, render_template, session
from flask_socketio import SocketIO, emit, disconnect
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import paramiko
import threading
import time
import os
import io
import socket
from datetime import datetime
import json
import base64
from cryptography.fernet import Fernet
import hashlib
import secrets

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ssh_connections.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 配置CORS允许所有来源
CORS(app, origins="*", resources={r"/*": {"origins": "*"}})

db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# 加密密钥管理
def get_or_create_encryption_key():
    key_file = os.path.join(os.path.dirname(__file__), 'instance', 'encryption.key')
    
    # 确保instance目录存在
    os.makedirs(os.path.dirname(key_file), exist_ok=True)
    
    if os.path.exists(key_file):
        # 读取现有密钥
        with open(key_file, 'rb') as f:
            return f.read()
    else:
        # 生成新密钥并保存
        key = Fernet.generate_key()
        with open(key_file, 'wb') as f:
            f.write(key)
        return key

ENCRYPTION_KEY = get_or_create_encryption_key()
cipher_suite = Fernet(ENCRYPTION_KEY)

# 密码哈希函数
def hash_password(password):
    """使用SHA256哈希密码"""
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{hashed}"

def verify_password(password, hashed_password):
    """验证密码"""
    try:
        salt, hash_value = hashed_password.split(':')
        return hashlib.sha256((password + salt).encode()).hexdigest() == hash_value
    except:
        return False

# 数据库模型
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # 关联到SSH连接
    ssh_connections = db.relationship('SSHConnection', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active
        }

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
    
    # 添加用户关联
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

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

# 认证装饰器
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': '请先登录'}), 401
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """获取当前登录用户"""
    user_id = session.get('user_id')
    if user_id:
        return db.session.get(User, user_id)
    return None

# 用户认证路由
@app.route('/api/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        # 验证输入
        if not username or not email or not password:
            return jsonify({'error': '用户名、邮箱和密码不能为空'}), 400
        
        if len(username) < 3:
            return jsonify({'error': '用户名至少需要3个字符'}), 400
        
        if len(password) < 6:
            return jsonify({'error': '密码至少需要6个字符'}), 400
        
        # 检查用户名是否已存在
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return jsonify({'error': '用户名已存在'}), 409
        
        # 检查邮箱是否已存在
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            return jsonify({'error': '邮箱已被注册'}), 409
        
        # 创建新用户
        password_hash = hash_password(password)
        user = User(
            username=username,
            email=email,
            password_hash=password_hash
        )
        
        db.session.add(user)
        db.session.commit()
        
        # 自动登录
        session['user_id'] = user.id
        session['username'] = user.username
        
        return jsonify({
            'message': '注册成功',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        print(f"注册错误: {e}")
        return jsonify({'error': '注册失败，请稍后重试'}), 500

@app.route('/api/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({'error': '用户名和密码不能为空'}), 400
        
        # 查找用户（支持用户名或邮箱登录）
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if not user or not verify_password(password, user.password_hash):
            return jsonify({'error': '用户名或密码错误'}), 401
        
        if not user.is_active:
            return jsonify({'error': '账户已被禁用'}), 403
        
        # 设置会话
        session['user_id'] = user.id
        session['username'] = user.username
        
        return jsonify({
            'message': '登录成功',
            'user': user.to_dict()
        })
        
    except Exception as e:
        print(f"登录错误: {e}")
        return jsonify({'error': '登录失败，请稍后重试'}), 500

@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    """用户登出"""
    try:
        session.clear()
        return jsonify({'message': '已成功登出'})
    except Exception as e:
        print(f"登出错误: {e}")
        return jsonify({'error': '登出失败'}), 500

@app.route('/api/user/profile', methods=['GET'])
@login_required
def get_profile():
    """获取用户资料"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': '用户未找到'}), 404
        
        return jsonify({
            'user': user.to_dict(),
            'ssh_connections_count': len(user.ssh_connections)
        })
    except Exception as e:
        print(f"获取用户资料错误: {e}")
        return jsonify({'error': '获取用户资料失败'}), 500

@app.route('/api/auth/check', methods=['GET'])
def check_auth():
    """检查登录状态"""
    try:
        user = get_current_user()
        if user:
            return jsonify({
                'authenticated': True,
                'user': user.to_dict()
            })
        else:
            return jsonify({'authenticated': False})
    except Exception as e:
        print(f"检查认证状态错误: {e}")
        return jsonify({'authenticated': False})

# 路由
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/connections', methods=['GET'])
@login_required
def get_connections():
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': '用户未找到'}), 404
        
        connections = SSHConnection.query.filter_by(user_id=user.id).all()
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
@login_required
def create_connection():
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': '用户未找到'}), 404
        
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
            private_key=encrypted_private_key,
            user_id=user.id  # 关联当前用户
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
@login_required
def delete_connection(conn_id):
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': '用户未找到'}), 404
        
        connection = db.session.get(SSHConnection, conn_id)
        if not connection:
            return jsonify({'error': '连接不存在'}), 404
        
        # 确保只能删除自己的连接
        if connection.user_id != user.id:
            return jsonify({'error': '无权限删除此连接'}), 403
        
        db.session.delete(connection)
        db.session.commit()
        return '', 204
    except Exception as e:
        print(f"删除连接错误: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/connections/test', methods=['POST'])
def test_connection():
    """测试SSH连接"""
    try:
        data = request.get_json()
        host = data.get('host')
        port = data.get('port', 22)
        username = data.get('username')
        password = data.get('password', '')
        private_key = data.get('private_key', '')
        
        if not host or not username:
            return jsonify({'success': False, 'error': '主机地址和用户名不能为空'}), 400
        
        # 创建SSH客户端进行测试
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            # 尝试连接
            if private_key:
                # 使用私钥认证
                key_file = io.StringIO(private_key)
                try:
                    pkey = paramiko.RSAKey.from_private_key(key_file)
                except:
                    try:
                        key_file.seek(0)
                        pkey = paramiko.Ed25519Key.from_private_key(key_file)
                    except:
                        try:
                            key_file.seek(0)
                            pkey = paramiko.ECDSAKey.from_private_key(key_file)
                        except:
                            key_file.seek(0)
                            pkey = paramiko.DSSKey.from_private_key(key_file)
                
                ssh_client.connect(
                    hostname=host,
                    port=port,
                    username=username,
                    pkey=pkey,
                    timeout=10
                )
            else:
                # 使用密码认证
                ssh_client.connect(
                    hostname=host,
                    port=port,
                    username=username,
                    password=password,
                    timeout=10
                )
            
            # 执行一个简单的命令来验证连接
            stdin, stdout, stderr = ssh_client.exec_command('echo "Connection test successful"')
            output = stdout.read().decode('utf-8').strip()
            
            # 获取系统信息
            stdin, stdout, stderr = ssh_client.exec_command('uname -a')
            system_info = stdout.read().decode('utf-8').strip()
            
            ssh_client.close()
            
            return jsonify({
                'success': True,
                'message': '连接测试成功！',
                'system_info': system_info,
                'details': {
                    'host': host,
                    'port': port,
                    'username': username,
                    'auth_method': '私钥认证' if private_key else '密码认证'
                }
            })
            
        except paramiko.AuthenticationException:
            return jsonify({
                'success': False,
                'error': '认证失败',
                'suggestions': [
                    '检查用户名和密码是否正确',
                    '确认服务器允许密码认证',
                    '尝试使用普通用户而不是root用户',
                    '检查服务器SSH配置'
                ]
            }), 401
            
        except paramiko.SSHException as e:
            return jsonify({
                'success': False,
                'error': f'SSH连接错误: {str(e)}',
                'suggestions': [
                    '检查网络连接是否正常',
                    '确认SSH服务是否运行',
                    '检查防火墙设置'
                ]
            }), 500
            
        except socket.timeout:
            return jsonify({
                'success': False,
                'error': '连接超时',
                'suggestions': [
                    '检查主机地址是否正确',
                    '确认网络连接是否正常',
                    '检查防火墙是否阻止连接'
                ]
            }), 408
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'连接失败: {str(e)}',
                'suggestions': [
                    '检查所有连接参数是否正确',
                    '确认服务器是否可访问'
                ]
            }), 500
            
        finally:
            try:
                ssh_client.close()
            except:
                pass
                
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'请求处理失败: {str(e)}'
        }), 500

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
        # 检查用户是否已登录
        if 'user_id' not in session:
            emit('ssh_error', {'error': '请先登录'})
            return
        
        user_id = session['user_id']
        connection = db.session.get(SSHConnection, conn_id)
        if not connection:
            emit('ssh_error', {'error': '连接不存在'})
            return
        
        # 确保用户只能连接自己的SSH连接
        if connection.user_id != user_id:
            emit('ssh_error', {'error': '无权限使用此连接'})
            return
        
        # 如果已经有连接，先断开
        if session_id in active_connections:
            active_connections[session_id].disconnect()
        
        # 创建新的SSH管理器
        ssh_manager = SSHManager(session_id)
        
        # 解密密码
        password = None
        if connection.password:
            try:
                password = cipher_suite.decrypt(connection.password.encode()).decode()
            except Exception as decrypt_error:
                print(f"密码解密失败: {decrypt_error}")
                emit('ssh_error', {'error': '密码解密失败，可能是加密密钥已更改。请重新保存连接。'})
                return
        
        private_key = None
        if connection.private_key:
            try:
                private_key = cipher_suite.decrypt(connection.private_key.encode()).decode()
            except Exception as decrypt_error:
                print(f"私钥解密失败: {decrypt_error}")
                emit('ssh_error', {'error': '私钥解密失败，可能是加密密钥已更改。请重新保存连接。'})
                return
        
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