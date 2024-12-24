from flask import render_template, request, redirect, url_for, session, flash
from utils.auth import login_required
from utils.config import load_config
from werkzeug.security import check_password_hash
from translations import translations
import pyotp

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

def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        totp_code = request.form.get('totp_code')
        
        print(f"Login attempt - Username: {username}, Has Password: {'Yes' if password else 'No'}, TOTP Code: {totp_code}")
        
        config = load_config()
        users = config.get('users', {})
        user = users.get(username)
        
        # 如果用户不存在
        if not user:
            print(f"User not found: {username}")
            flash(t('login.invalid_credentials'), 'error')
            return render_template('login.html', show_2fa=False)
        
        # 验证密码
        if not check_password_hash(user['password_hash'], password):
            print(f"Invalid password for user: {username}")
            flash(t('login.invalid_credentials'), 'error')
            return render_template('login.html', show_2fa=False)
        
        # 密码验证通过，检查2FA
        if user.get('totp_enabled', False):
            print(f"2FA is enabled for user: {username}")
            # 如果需要2FA但没有提供验证码
            if not totp_code:
                print("No TOTP code provided, showing 2FA form")
                return render_template('login.html', show_2fa=True, username=username, request=request)
            
            # 验证2FA代码
            totp = pyotp.TOTP(user['totp_secret'])
            if not totp.verify(totp_code):
                print(f"Invalid TOTP code: {totp_code}")
                flash(t('login.invalid_2fa'), 'error')
                return render_template('login.html', show_2fa=True, username=username, request=request)
            print("TOTP code verified successfully")
        
        # 所有验证通过，设置会话
        print(f"Login successful for user: {username}")
        session['user_id'] = username
        if not session.get('lang'):
            session['lang'] = 'en'
        return redirect(url_for('main.dashboard'))
    
    return render_template('login.html', show_2fa=False)

@login_required
def dashboard():
    config = load_config()
    user = config['users'].get(session.get('user_id'))
    return render_template('dashboard.html', user=user)

def logout():
    # 保存当前语言设置
    current_lang = session.get('lang', 'en')
    session.clear()
    # 恢复语言设置
    session['lang'] = current_lang
    return redirect(url_for('main.login'))

def change_language():
    """更改语言设置，不需要登录即可使用"""
    lang = request.args.get('lang', 'en')
    if lang in ['en', 'zh']:
        session['lang'] = lang
        print(f"Language changed to: {lang}")
    
    # 获取来源页面
    referrer = request.referrer
    if referrer:
        return redirect(referrer)
    
    # 如果用户已登录，重定向到仪表板，否则重定向到登录页面
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('main.login'))
