from flask import render_template, request, redirect, url_for, session, flash
from utils.auth import login_required
from utils.config import load_config, save_config
from werkzeug.security import check_password_hash, generate_password_hash
import pyotp
import qrcode
import io
import base64
from translations import translations

def t(key):
    """翻译函数，支持嵌套键"""
    try:
        lang = session.get('lang', 'en')
        keys = key.split('.')
        value = translations[lang]
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, key)
            else:
                return key
        return value
    except (KeyError, AttributeError):
        return key

@login_required
def settings():
    config = load_config()
    user = config['users'].get(session.get('user_id'))
    
    # 总是生成新的TOTP密钥用于启用2FA
    if not user.get('totp_enabled'):
        new_secret = pyotp.random_base32()
        totp_secret = new_secret
        session['new_totp_secret'] = new_secret  # 保存到会话中供后续验证使用
    else:
        totp_secret = user['totp_secret']
    
    totp_uri = pyotp.TOTP(totp_secret).provisioning_uri(
        user['username'], 
        issuer_name=t('dashboard.title')
    )
    
    # 生成QR码
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(totp_uri)
    qr.make(fit=True)
    qr_image = qr.make_image(fill_color="black", back_color="white")
    
    # 将QR码转换为base64字符串
    buffered = io.BytesIO()
    qr_image.save(buffered, format="PNG")
    qr_base64 = base64.b64encode(buffered.getvalue()).decode()
    
    return render_template('settings.html', 
                         user=user,
                         qr_code=qr_base64,
                         totp_secret=totp_secret)

@login_required
def update_username():
    if not request.form.get('new_username'):
        flash(t('settings.all_fields_required'), 'danger')
        return redirect(url_for('main.settings'))
    
    config = load_config()
    current_user = config['users'].get(session.get('user_id'))
    new_username = request.form.get('new_username')
    password = request.form.get('password')
    
    if not check_password_hash(current_user['password_hash'], password):
        flash(t('settings.password_wrong'), 'danger')
        return redirect(url_for('main.settings'))
    
    if new_username in config['users'] and new_username != session.get('user_id'):
        flash(t('settings.username_exists'), 'danger')
        return redirect(url_for('main.settings'))
    
    old_username = session.get('user_id')
    
    # 更新用户名
    user_data = config['users'].pop(old_username)
    user_data['username'] = new_username
    config['users'][new_username] = user_data
    
    # 更新密码存储
    if 'password_store' in config and old_username in config['password_store']:
        password_store = config['password_store'].pop(old_username)
        config['password_store'][new_username] = password_store
    
    # 更新TOTP存储
    if 'totp_store' in config and old_username in config['totp_store']:
        totp_store = config['totp_store'].pop(old_username)
        config['totp_store'][new_username] = totp_store
    
    save_config(config)
    
    # 更新会话
    session['user_id'] = new_username
    flash(t('settings.username_updated'), 'success')
    return redirect(url_for('main.settings'))

@login_required
def update_password():
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if not all([current_password, new_password, confirm_password]):
        flash(t('settings.all_fields_required'), 'danger')
        return redirect(url_for('main.settings'))
    
    if new_password != confirm_password:
        flash(t('settings.passwords_not_match'), 'danger')
        return redirect(url_for('main.settings'))
    
    config = load_config()
    current_user = config['users'].get(session.get('user_id'))
    
    if not check_password_hash(current_user['password_hash'], current_password):
        flash(t('settings.password_wrong'), 'danger')
        return redirect(url_for('main.settings'))
    
    # 更新密码
    current_user['password_hash'] = generate_password_hash(new_password)
    save_config(config)
    
    flash(t('settings.password_updated'), 'success')
    return redirect(url_for('main.settings'))

@login_required
def toggle_2fa():
    config = load_config()
    user = config['users'].get(session.get('user_id'))
    action = request.form.get('action')
    totp_code = request.form.get('totp_code')
    password = request.form.get('password', '')
    
    if action == 'enable':
        if not totp_code:
            flash(t('settings.all_fields_required'), 'error')
            return redirect(url_for('main.settings'))
        
        # 验证新的TOTP代码
        new_secret = session.get('new_totp_secret')
        if not new_secret:
            flash(t('settings.setup_2fa_first'), 'error')
            return redirect(url_for('main.settings'))
            
        totp = pyotp.TOTP(new_secret)
        if not totp.verify(totp_code):
            flash(t('login.invalid_2fa'), 'error')
            # 验证失败时生成新的密钥
            session.pop('new_totp_secret', None)
            return redirect(url_for('main.settings'))
        
        # 启用2FA并保存新密钥
        user['totp_enabled'] = True
        user['totp_secret'] = new_secret
        session.pop('new_totp_secret', None)  # 清除会话中的临时密钥
        
    elif action == 'disable':
        if not all([password, totp_code]):
            flash(t('settings.all_fields_required'), 'error')
            return redirect(url_for('main.settings'))
            
        # 验证密码
        if not check_password_hash(user['password_hash'], password):
            flash(t('settings.password_wrong'), 'error')
            return redirect(url_for('main.settings'))
            
        # 验证当前TOTP代码
        totp = pyotp.TOTP(user['totp_secret'])
        if not totp.verify(totp_code):
            flash(t('login.invalid_2fa'), 'error')
            return redirect(url_for('main.settings'))
            
        # 禁用2FA
        user['totp_enabled'] = False
        
    save_config(config)
    
    if action == 'enable':
        flash(t('settings.2fa_enabled_success'), 'success')
    else:
        flash(t('settings.2fa_disabled_success'), 'success')
    
    return redirect(url_for('main.settings'))
