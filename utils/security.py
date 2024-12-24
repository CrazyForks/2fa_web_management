import ipaddress
from functools import wraps
from flask import request, abort, current_app, jsonify
from datetime import datetime, timedelta
import re

# 存储登录尝试记录
_login_attempts = {}

def check_host_allowed(config, host):
    """检查主机名是否在允许列表中"""
    print(f"Checking host: {host}")  # 调试日志
    
    # 确保配置路径正确
    host_control = config.get('auth_forntend', {}).get('host_control', {})
    print(f"Host control config: {host_control}")  # 调试日志
    
    # 检查是否启用了主机控制
    if not host_control.get('enabled', False):
        print("Host control disabled, allowing all hosts")
        return True

    allowed_hosts = host_control.get('allowed_hosts', [])
    print(f"Allowed hosts: {allowed_hosts}")
    
    # 如果 0.0.0.0 在允许列表中，允许所有主机
    if '0.0.0.0' in allowed_hosts:
        print("0.0.0.0 found in allowed hosts, allowing all hosts")
        return True
    
    # 检查是否完全匹配
    if host in allowed_hosts:
        print(f"Host {host} found in exact match")
        return True
    
    # 检查通配符匹配
    for pattern in allowed_hosts:
        print(f"Checking pattern: {pattern}")
        if '*' in pattern:
            # 将通配符模式转换为正则表达式
            regex_pattern = pattern.replace('.', '\\.').replace('*', '[^.]+')
            print(f"Regex pattern: {regex_pattern}")
            if re.match(f"^{regex_pattern}$", host):
                print(f"Host {host} matched pattern {pattern}")
                return True
    
    print(f"Host {host} not allowed")
    return False

def check_ip_allowed(config, ip):
    """检查IP是否在允许列表中"""
    ip_control = config.get('auth_forntend', {}).get('ip_control', {})
    if not ip_control.get('enabled', False):
        return True

    allowed_ips = ip_control.get('allowed_ips', ['127.0.0.1'])
    client_ip = ipaddress.ip_address(ip)

    for allowed in allowed_ips:
        try:
            if '/' in allowed:  # CIDR格式
                network = ipaddress.ip_network(allowed, strict=False)
                if client_ip in network:
                    return True
            else:  # 单个IP
                if client_ip == ipaddress.ip_address(allowed):
                    return True
        except ValueError:
            continue
    return False

def get_login_attempt_info(config, ip):
    """获取登录尝试信息"""
    login_config = config.get('auth_forntend', {}).get('login_attempts', {})
    max_attempts = login_config.get('max_attempts', 5)
    reset_minutes = login_config.get('reset_minutes', 30)

    current_time = datetime.now()
    ip_attempts = _login_attempts.get(ip, {'count': 0, 'last_attempt': current_time})

    # 计算剩余锁定时间
    if ip_attempts['count'] >= max_attempts:
        time_passed = current_time - ip_attempts['last_attempt']
        reset_time = timedelta(minutes=reset_minutes)
        if time_passed < reset_time:
            remaining_time = reset_time - time_passed
            return {
                'allowed': False,
                'remaining_attempts': 0,
                'locked': True,
                'reset_minutes': reset_minutes,
                'remaining_minutes': int(remaining_time.total_seconds() / 60),
                'remaining_seconds': int(remaining_time.total_seconds() % 60)
            }
        else:
            # 重置计数
            ip_attempts = {'count': 0, 'last_attempt': current_time}
            _login_attempts[ip] = ip_attempts

    return {
        'allowed': True,
        'remaining_attempts': max_attempts - ip_attempts['count'],
        'locked': False,
        'reset_minutes': reset_minutes,
        'remaining_minutes': 0,
        'remaining_seconds': 0
    }

def check_login_attempts(config, ip):
    """检查登录尝试次数"""
    return get_login_attempt_info(config, ip)['allowed']

def record_login_attempt(ip, success=False):
    """记录登录尝试"""
    current_time = datetime.now()
    if success:
        # 登录成功，清除记录
        _login_attempts.pop(ip, None)
    else:
        # 登录失败，增加计数
        if ip not in _login_attempts:
            _login_attempts[ip] = {'count': 0, 'last_attempt': current_time}
        _login_attempts[ip]['count'] += 1
        _login_attempts[ip]['last_attempt'] = current_time

def require_ip_permission(f):
    """IP访问控制装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(current_app, 'config'):
            return f(*args, **kwargs)
        
        if not check_ip_allowed(current_app.config, request.remote_addr):
            return jsonify({
                'error': 'IP access denied',
                'message': f'IP {request.remote_addr} is not in the allowed list'
            }), 403
        return f(*args, **kwargs)
    return decorated_function

def require_host_permission(f):
    """主机访问控制装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(current_app, 'config'):
            print("No app config found")
            return jsonify({
                'error': 'Server configuration error',
                'message': 'Application configuration not found'
            }), 500
        
        host = request.host.split(':')[0]  # 移除端口号
        print(f"Checking host permission for: {host}")
        
        if not check_host_allowed(current_app.config, host):
            print(f"Access denied for host: {host}")
            return jsonify({
                'error': 'Host not allowed',
                'message': f'Host {host} is not in the allowed list'
            }), 403
        
        print(f"Access granted for host: {host}")
        return f(*args, **kwargs)
    return decorated_function

def check_login_limit(f):
    """登录限制装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(current_app, 'config'):
            return f(*args, **kwargs)
            
        attempt_info = get_login_attempt_info(current_app.config, request.remote_addr)
        if not attempt_info['allowed']:
            error_message = (
                f"Too many login attempts. Account is locked for "
                f"{attempt_info['remaining_minutes']} minutes and "
                f"{attempt_info['remaining_seconds']} seconds. "
                f"Please try again later."
            )
            return jsonify({
                'error': 'Too many attempts',
                'message': error_message,
                'remaining_minutes': attempt_info['remaining_minutes'],
                'remaining_seconds': attempt_info['remaining_seconds']
            }), 429
        
        response = f(*args, **kwargs)
        
        # 如果是登录请求，在响应中添加剩余尝试次数信息
        if request.endpoint == 'login' and not attempt_info['locked']:
            if isinstance(response, tuple):
                response_data, status_code = response
            else:
                response_data, status_code = response.get_json(), response.status_code
            
            if isinstance(response_data, dict):
                response_data.update({
                    'remaining_attempts': attempt_info['remaining_attempts']
                })
                return jsonify(response_data), status_code
        
        return response
    return decorated_function
