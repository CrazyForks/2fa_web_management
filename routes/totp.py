from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from utils.auth import login_required
from services.totp_manager import TotpManager
from translations import translations
import pyotp
from datetime import datetime

totp = Blueprint('totp', __name__)

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

@totp.route('/totp')
@login_required
def totp_list():
    """显示TOTP密钥列表页面"""
    manager = TotpManager(session['user_id'])
    totp_keys = manager.get_all_keys()
    return render_template('totp/index.html', totp_keys=totp_keys)

@totp.route('/totp/new', methods=['GET', 'POST'])
@login_required
def add_totp():
    """添加新的TOTP密钥"""
    if request.method == 'POST':
        manager = TotpManager(session['user_id'])
        try:
            key = manager.create_key(
                name=request.form['name'],
                secret=request.form.get('secret') or pyotp.random_base32(),
                digits=6,  # 默认6位
                interval=30  # 默认30秒
            )
            flash(t('totp.create_success'), 'success')
            return redirect(url_for('totp.totp_list'))
        except Exception as e:
            flash(t('totp.create_error'), 'error')
    
    return render_template('totp/edit.html', key=None)

@totp.route('/totp/<key_id>')
@login_required
def view_totp(key_id):
    """查看TOTP密钥详情"""
    manager = TotpManager(session['user_id'])
    key = manager.get_key(key_id)
    if not key:
        flash(t('totp.not_found'), 'error')
        return redirect(url_for('totp.totp_list'))
    return render_template('totp/view.html', key=key)

@totp.route('/totp/<key_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_totp(key_id):
    """编辑TOTP密钥"""
    manager = TotpManager(session['user_id'])
    key = manager.get_key(key_id)
    
    if not key:
        flash(t('totp.not_found'), 'error')
        return redirect(url_for('totp.totp_list'))
    
    if request.method == 'POST':
        try:
            updated_key = manager.update_key(
                key_id,
                name=request.form['name'],
                issuer=request.form.get('issuer'),
                digits=int(request.form.get('digits', 6)),
                interval=int(request.form.get('interval', 30))
            )
            flash(t('totp.update_success'), 'success')
            return redirect(url_for('totp.view_totp', key_id=key_id))
        except Exception as e:
            flash(t('totp.update_error'), 'error')
    
    return render_template('totp/edit.html', key=key)

@totp.route('/totp/<key_id>/delete', methods=['DELETE'])
@login_required
def delete_totp(key_id):
    """删除TOTP密钥"""
    manager = TotpManager(session['user_id'])
    if manager.delete_key(key_id):
        return jsonify({'success': True})
    return jsonify({'success': False}), 400

@totp.route('/totp/<key_id>/code')
@login_required
def get_totp_code(key_id):
    """获取当前TOTP代码"""
    manager = TotpManager(session['user_id'])
    key = manager.get_key(key_id)
    if not key:
        return jsonify({'error': 'Key not found'}), 404
    
    totp = pyotp.TOTP(key['secret'])
    return jsonify({
        'code': totp.now(),
        'valid_until': (datetime.now().timestamp() // 30 + 1) * 30
    })
