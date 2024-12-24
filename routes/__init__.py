from flask import Blueprint

main = Blueprint('main', __name__)

from .home import login, logout, dashboard, change_language
from .backup import (backup_manager, create_backup, download_backup, delete_backup, 
                    restore_backup, upload_backup)
from .settings import settings, update_password, update_username, toggle_2fa

# 登录相关路由
main.add_url_rule('/', view_func=login, methods=['GET', 'POST'])
main.add_url_rule('/login', view_func=login, methods=['GET', 'POST'])
main.add_url_rule('/logout', view_func=logout)
main.add_url_rule('/dashboard', view_func=dashboard)
main.add_url_rule('/change_language', view_func=change_language)

# 备份管理路由
main.add_url_rule('/backup', view_func=backup_manager)
main.add_url_rule('/backup/create', view_func=create_backup)
main.add_url_rule('/backup/upload', view_func=upload_backup, methods=['POST'])
main.add_url_rule('/backup/download/<filename>', view_func=download_backup)
main.add_url_rule('/backup/delete/<filename>', view_func=delete_backup)
main.add_url_rule('/backup/restore/<filename>', view_func=restore_backup)

# 设置路由
main.add_url_rule('/settings', view_func=settings)
main.add_url_rule('/settings/username', view_func=update_username, methods=['POST'])
main.add_url_rule('/settings/password', view_func=update_password, methods=['POST'])
main.add_url_rule('/settings/2fa', view_func=toggle_2fa, methods=['POST'])