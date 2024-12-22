from flask import Blueprint

main = Blueprint('main', __name__)

# 添加全局模板函数
@main.app_context_processor
def utility_processor():
    from utils import get_translation
    return {'t': get_translation}

# 导入所有路由
from .home import login, logout
from .dashboard import dashboard, get_tokens, add_token_route, remove_token_route