from flask import render_template, request, redirect, url_for, flash, send_file, session
from utils.auth import login_required
import os
import shutil
from datetime import datetime
import yaml
import zipfile
import io
from translations import translations
from werkzeug.utils import secure_filename

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

BACKUP_DIR = 'backups'

def ensure_backup_dir():
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

def is_valid_backup_file(file):
    try:
        with zipfile.ZipFile(file, 'r') as zf:
            # 检查是否包含必要的文件
            file_list = zf.namelist()
            return 'config.yaml' in file_list
    except zipfile.BadZipFile:
        return False

@login_required
def backup_manager():
    ensure_backup_dir()
    backups = []
    if os.path.exists(BACKUP_DIR):
        for item in os.listdir(BACKUP_DIR):
            if item.endswith('.zip'):
                path = os.path.join(BACKUP_DIR, item)
                stat = os.stat(path)
                backups.append({
                    'name': item,
                    'date': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                    'size': f"{stat.st_size / 1024:.1f} KB"
                })
    backups.sort(key=lambda x: x['date'], reverse=True)
    return render_template('backup.html', backups=backups)

@login_required
def create_backup():
    ensure_backup_dir()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f'backup_{timestamp}.zip'
    backup_path = os.path.join(BACKUP_DIR, backup_name)

    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        # 备份配置文件
        if os.path.exists('config.yaml'):
            zf.write('config.yaml')

    memory_file.seek(0)
    with open(backup_path, 'wb') as f:
        f.write(memory_file.getvalue())

    flash(t('backup.create_success'), 'success')
    return redirect(url_for('main.backup_manager'))

@login_required
def upload_backup():
    if 'backup_file' not in request.files:
        flash(t('backup.no_file_selected'), 'error')
        return redirect(url_for('main.backup_manager'))
    
    file = request.files['backup_file']
    if file.filename == '':
        flash(t('backup.no_file_selected'), 'error')
        return redirect(url_for('main.backup_manager'))
    
    if not file.filename.endswith('.zip'):
        flash(t('backup.invalid_file_type'), 'error')
        return redirect(url_for('main.backup_manager'))

    ensure_backup_dir()
    filename = secure_filename(file.filename)
    temp_path = os.path.join(BACKUP_DIR, 'temp_' + filename)
    
    # 保存文件并验证
    file.save(temp_path)
    if not is_valid_backup_file(temp_path):
        os.remove(temp_path)
        flash(t('backup.invalid_backup_file'), 'error')
        return redirect(url_for('main.backup_manager'))

    # 生成唯一文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    new_filename = f'backup_{timestamp}.zip'
    new_path = os.path.join(BACKUP_DIR, new_filename)
    
    # 重命名文件
    os.rename(temp_path, new_path)
    
    flash(t('backup.upload_success'), 'success')
    return redirect(url_for('main.backup_manager'))

@login_required
def download_backup(filename):
    backup_path = os.path.join(BACKUP_DIR, filename)
    if os.path.exists(backup_path):
        return send_file(backup_path, as_attachment=True)
    flash(t('backup.file_not_found'), 'error')
    return redirect(url_for('main.backup_manager'))

@login_required
def delete_backup(filename):
    backup_path = os.path.join(BACKUP_DIR, filename)
    if os.path.exists(backup_path):
        os.remove(backup_path)
        flash(t('backup.delete_success'), 'success')
    else:
        flash(t('backup.file_not_found'), 'error')
    return redirect(url_for('main.backup_manager'))

@login_required
def restore_backup(filename):
    backup_path = os.path.join(BACKUP_DIR, filename)
    if not os.path.exists(backup_path):
        flash(t('backup.file_not_found'), 'error')
        return redirect(url_for('main.backup_manager'))

    try:
        with zipfile.ZipFile(backup_path, 'r') as zf:
            # 恢复配置文件
            if 'config.yaml' in zf.namelist():
                zf.extract('config.yaml', '.')
        
        flash(t('backup.restore_success'), 'success')
    except Exception as e:
        flash(t('backup.restore_error'), 'error')
        
    return redirect(url_for('main.backup_manager'))
