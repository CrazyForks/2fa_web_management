from flask import render_template, request, redirect, url_for, flash, session
from interface.auth import load_config, generate_totp
from . import main

@main.route('/login', methods=['GET', 'POST'])
def login():
    # 处理语言切换
    lang = request.args.get('lang')
    if lang in ['en', 'zh']:
        session['lang'] = lang

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        otp = request.form.get('otp')
        
        config = load_config()
        auth_config = config.get('auth_forntend', {})
        
        if username != auth_config.get('username') or password != auth_config.get('password'):
            flash('invalid_credentials')
            return redirect(url_for('main.login'))
        
        if auth_config.get('is_2fa_enabled', False):
            if not otp:
                flash('2fa_required')
                return redirect(url_for('main.login'))
            
            if otp != generate_totp(auth_config.get('2fa_secret')):
                flash('invalid_2fa')
                return redirect(url_for('main.login'))
        
        session['username'] = username
        return redirect(url_for('main.dashboard'))
    
    # 获取2FA状态传递给模板
    config = load_config()
    is_2fa_enabled = config.get('auth_forntend', {}).get('is_2fa_enabled', False)
    return render_template('login.html', is_2fa_enabled=is_2fa_enabled)

@main.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.login'))
