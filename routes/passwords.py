from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from utils.auth import login_required
from services.password_manager import PasswordManager
from services.totp_manager import TotpManager
import pyotp
from translations import translations
from datetime import datetime
import qrcode
import io
import base64

passwords = Blueprint('passwords', __name__)

def t(key):
    """翻译函数"""
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

@passwords.route('/passwords')
@login_required
def password_list():
    """显示密码列表页面"""
    manager = PasswordManager(session['user_id'])
    passwords = manager.get_all_entries()
    return render_template('passwords/index.html', passwords=passwords)

@passwords.route('/passwords/new', methods=['GET', 'POST'])
@login_required
def new_password():
    """创建新的密码条目"""
    if request.method == 'POST':
        manager = PasswordManager(session['user_id'])
        try:
            entry = manager.create_entry(
                title=request.form['title'],
                username=request.form.get('username'),
                password=request.form['password'],
                url=request.form.get('url'),
                notes=request.form.get('notes'),
                category=request.form.get('category', 'login'),
                totp_secret=request.form.get('totp_secret') if request.form.get('enableTotp') else None
            )
            flash(t('passwords.create_success'), 'success')
            return redirect(url_for('passwords.password_list'))
        except Exception as e:
            flash(t('passwords.create_error'), 'error')
    
    return render_template('passwords/edit.html', entry=None)

@passwords.route('/passwords/<entry_id>')
@login_required
def view_password(entry_id):
    """查看密码条目详情"""
    manager = PasswordManager(session['user_id'])
    entry = manager.get_entry(entry_id)
    if not entry:
        flash(t('passwords.not_found'), 'error')
        return redirect(url_for('passwords.password_list'))
    return render_template('passwords/view.html', entry=entry)

@passwords.route('/passwords/<entry_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_password(entry_id):
    """编辑密码条目"""
    manager = PasswordManager(session['user_id'])
    entry = manager.get_entry(entry_id)
    
    if not entry:
        flash(t('passwords.not_found'), 'error')
        return redirect(url_for('passwords.password_list'))
    
    if request.method == 'POST':
        try:
            # 处理 TOTP 设置
            enable_totp = request.form.get('enableTotp') == 'on'
            totp_secret = request.form.get('totp_secret') if enable_totp else None
            
            updated_entry = manager.update_entry(
                entry_id,
                title=request.form['title'],
                username=request.form.get('username'),
                password=request.form.get('password', entry.password),
                url=request.form.get('url'),
                notes=request.form.get('notes'),
                category=request.form.get('category'),
                totp_secret=totp_secret
            )
            flash(t('passwords.update_success'), 'success')
            return redirect(url_for('passwords.view_password', entry_id=entry_id))
        except Exception as e:
            flash(t('passwords.update_error'), 'error')
    
    return render_template('passwords/edit.html', entry=entry)

@passwords.route('/passwords/<entry_id>/delete', methods=['POST'])
@login_required
def delete_password(entry_id):
    """删除密码条目"""
    manager = PasswordManager(session['user_id'])
    if manager.delete_entry(entry_id):
        flash(t('passwords.delete_success'), 'success')
        return redirect(url_for('passwords.password_list'))
    flash(t('passwords.delete_error'), 'error')
    return redirect(url_for('passwords.password_list'))

@passwords.route('/passwords/search')
@login_required
def search_passwords():
    """搜索密码条目"""
    query = request.args.get('q', '').lower()
    manager = PasswordManager(session['user_id'])
    entries = manager.get_all_entries()
    
    if query:
        entries = [
            entry for entry in entries
            if query in entry['title'].lower() or
               query in entry.get('username', '').lower() or
               query in entry.get('url', '').lower()
        ]
    
    return jsonify(entries)

@passwords.route('/passwords/<entry_id>/totp')
@login_required
def get_totp_code(entry_id):
    """获取TOTP验证码"""
    manager = PasswordManager(session['user_id'])
    entry = manager.get_entry(entry_id)
    
    if not entry or not entry.totp_secret:
        return jsonify({'error': 'TOTP not found'}), 404
        
    # 创建 TOTP 对象
    totp = pyotp.TOTP(entry.totp_secret)
    
    # 获取当前时间和剩余秒数
    now = datetime.now().timestamp()
    step = 30  # TOTP 默认时间步长
    progress = 1.0 - ((now % step) / step)  # 计算进度
    
    return jsonify({
        'code': totp.now(),
        'progress': progress
    })

@passwords.route('/passwords/generate-totp')
@login_required
def generate_totp_secret():
    """生成新的TOTP密钥"""
    secret = pyotp.random_base32()
    return jsonify({'secret': secret})

@passwords.route('/api/generate_totp_secret')
@login_required
def api_generate_totp_secret():
    """生成新的TOTP密钥"""
    secret = pyotp.random_base32()
    return jsonify({'secret': secret})

@passwords.route('/api/totp_code')
@login_required
def api_get_totp_code():
    """获取TOTP代码"""
    secret = request.args.get('secret')
    if not secret:
        return jsonify({'error': 'Secret is required'}), 400
        
    try:
        totp = pyotp.TOTP(secret)
        code = totp.now()
        return jsonify({'code': code})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@passwords.route('/passwords/<id>/totp_qr')
@login_required
def get_totp_qr(id):
    """生成TOTP二维码"""
    manager = PasswordManager(session['user_id'])
    entry = manager.get_entry(id)
    
    if not entry or not entry.totp_secret:
        return jsonify({'error': 'TOTP secret not found'}), 404
    
    try:
        # 生成otpauth URI
        uri = pyotp.TOTP(entry.totp_secret).provisioning_uri(entry.title, issuer_name="2FA Manager")
        
        # 生成二维码
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(uri)
        qr.make(fit=True)
        
        # 将二维码转换为图片
        img = qr.make_image(fill_color="black", back_color="white")
        
        # 将图片转换为base64
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return jsonify({
            'qr_code': f"data:image/png;base64,{img_str}"
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@passwords.route('/api/decrypt', methods=['POST'])
@login_required
def decrypt_text():
    """解密文本"""
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'Missing text parameter'}), 400
        
    try:
        manager = PasswordManager(session['user_id'])
        decrypted_text = manager.decrypt_text(data['text'])
        return jsonify({'text': decrypted_text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
