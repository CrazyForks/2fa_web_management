from flask import render_template, request, redirect, url_for, session, flash, jsonify
from interface.auth import load_config, add_token, remove_token, generate_totp, save_config
from . import main
import time
import qrcode
import base64
import io
import pyotp
import re
import yaml

@main.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('main.login'))
    
    config = load_config()
    is_2fa_enabled = config['auth_forntend']['is_2fa_enabled']
    
    return render_template('dashboard.html', 
                         username=session['username'],
                         is_2fa_enabled=is_2fa_enabled)

@main.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('main.login'))
    
    # 处理语言切换
    lang = request.args.get('lang')
    if lang in ['en', 'zh']:
        session['lang'] = lang
    
    config = load_config()
    tokens = [{'name': token['name'], 'current_code': generate_totp(token['secret'])} for token in config.get('2fa_token_list', [])]
    
    return render_template('dashboard.html', tokens=tokens, config=config)

@main.route('/api/tokens')
def get_tokens():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    config = load_config()
    tokens = []
    current_time = int(time.time())
    time_step = 30  # TOTP 默认30秒更新一次
    
    for token in config.get('2fa_token_list', []):
        current_code = generate_totp(token['secret'])
        seconds_remaining = time_step - (current_time % time_step)
        tokens.append({
            'name': token['name'],
            'current_code': current_code,
            'seconds_remaining': seconds_remaining
        })
    
    return jsonify({'tokens': tokens})

@main.route('/update_password', methods=['POST'])
def update_password():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if not all([current_password, new_password, confirm_password]):
        flash('missing_fields', 'error')
        return redirect(url_for('main.dashboard'))
    
    if new_password != confirm_password:
        flash('passwords_not_match', 'error')
        return redirect(url_for('main.dashboard'))
    
    config = load_config()
    if current_password != config['auth_forntend']['password']:
        flash('current_password_incorrect', 'error')
        return redirect(url_for('main.dashboard'))
    
    # 更新密码
    config['auth_forntend']['password'] = new_password
    save_config(config)
    
    flash('password_updated', 'success')
    return redirect(url_for('main.dashboard'))

@main.route('/update_username', methods=['POST'])
def update_username():
    if 'username' not in session:
        return redirect(url_for('main.login'))
        
    current_username = request.form.get('current_username')
    new_username = request.form.get('new_username')
    
    if not current_username or not new_username:
        flash('missing_fields', 'error')
        return redirect(url_for('main.dashboard'))
    
    # 加载配置
    config = load_config()
    auth_config = config.get('auth_forntend', {})
    
    # 验证当前用户名
    if current_username != auth_config.get('username'):
        flash('current_username_incorrect', 'error')
        return redirect(url_for('main.dashboard'))
    
    # 更新配置
    auth_config['username'] = new_username
    config['auth_forntend'] = auth_config
    
    # 保存配置
    try:
        save_config(config)
        # 更新会话中的用户名
        session['username'] = new_username
        flash('username_updated', 'success')
    except Exception as e:
        flash('update_failed', 'error')
        print(f"Error updating username: {str(e)}")
    
    return redirect(url_for('main.dashboard'))

@main.route('/api/toggle_2fa', methods=['POST'])
def toggle_2fa():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    config = load_config()
    
    if config['auth_forntend']['is_2fa_enabled']:
        # 禁用2FA
        config['auth_forntend']['is_2fa_enabled'] = False
        config['auth_forntend']['2fa_secret'] = ''
        save_config(config)
        return jsonify({'enabled': False, 'message': '2FA已禁用'})
    else:
        # 生成新的2FA密钥
        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret)
        
        # 生成二维码
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        provisioning_uri = totp.provisioning_uri(config['auth_forntend']['username'], issuer_name="2FA Token Management")
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return jsonify({
            'enabled': True,
            'secret': secret,
            'qr_code': f'data:image/png;base64,{img_str}',
            'message': '请扫描二维码'
        })

@main.route('/api/verify_2fa', methods=['POST'])
def verify_2fa():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    if not data or 'secret' not in data or 'code' not in data:
        return jsonify({'error': 'Invalid request', 'message': '缺少必要字段'}), 400
    
    secret = data['secret']
    code = data['code']
    
    # 验证代码
    totp = pyotp.TOTP(secret)
    if totp.verify(code):
        # 验证成功，保存配置
        config = load_config()
        config['auth_forntend']['2fa_secret'] = secret
        config['auth_forntend']['is_2fa_enabled'] = True
        save_config(config)
        return jsonify({'success': True, 'message': '2FA已启用'})
    else:
        return jsonify({'success': False, 'message': '无效的2FA验证码'})

@main.route('/add_token', methods=['POST'])
def add_token_route():
    if 'username' not in session:
        return redirect(url_for('main.login'))
    
    token_name = request.form.get('token_name')
    token_secret = request.form.get('token_secret')
    
    if not token_name or not token_secret:
        flash('missing_fields', 'error')
        return redirect(url_for('main.dashboard'))
    
    config = load_config()
    # 检查令牌名是否已存在
    if any(token['name'] == token_name for token in config.get('2fa_token_list', [])):
        flash('token_exists', 'error')
        return redirect(url_for('main.dashboard'))
    
    # 检查密钥格式是否正确
    try:
        # 尝试生成一个验证码来验证密钥是否有效
        totp = pyotp.TOTP(token_secret)
        totp.now()
        add_token(token_name, token_secret)
        flash('token_added', 'success')
    except Exception as e:
        flash('invalid_secret', 'error')
        print(f"Error validating token secret: {str(e)}")
    
    return redirect(url_for('main.dashboard'))

@main.route('/remove_token', methods=['POST'])
def remove_token_route():
    if 'username' not in session:
        return redirect(url_for('main.login'))
    
    token_name = request.form.get('token_name')
    remove_token(token_name)
    flash('token_removed', 'success')
    return redirect(url_for('main.dashboard'))

@main.route('/api/token_details/<token_name>')
def get_token_details(token_name):
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    config = load_config()
    token = next((t for t in config.get('2fa_token_list', []) if t['name'] == token_name), None)
    
    if not token:
        return jsonify({'error': 'Token not found'}), 404
    
    current_time = int(time.time())
    time_step = 30  # TOTP 默认30秒更新一次
    current_code = generate_totp(token['secret'])
    seconds_remaining = time_step - (current_time % time_step)
    
    # 生成二维码
    totp = pyotp.TOTP(token['secret'])
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    provisioning_uri = totp.provisioning_uri(token['name'], issuer_name="2FA Token Management")
    qr.add_data(provisioning_uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return jsonify({
        'name': token['name'],
        'secret': token['secret'],
        'current_code': current_code,
        'seconds_remaining': seconds_remaining,
        'qr_code': f'data:image/png;base64,{img_str}'
    })
