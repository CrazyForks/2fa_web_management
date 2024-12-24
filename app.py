from flask import Flask, session
from routes import main
from routes.passwords import passwords
from routes.totp import totp
from translations import translations
import os

def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    
    # 注册蓝图
    app.register_blueprint(main)
    app.register_blueprint(passwords)
    app.register_blueprint(totp)
    
    # 添加翻译函数到模板全局变量
    @app.context_processor
    def utility_processor():
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
        return dict(t=t)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0')
