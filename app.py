from flask import Flask, request, session, redirect, url_for
from routes import main
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # 添加 secret_key 用于会话管理

# 添加语言选择中间件
@app.before_request
def before_request():
    # 从 URL 参数、cookie 或 session 中获取语言设置
    lang = request.args.get('lang') or \
           request.cookies.get('lang') or \
           session.get('lang') or \
           'en'  # 默认语言为英语
    
    # 确保语言代码有效
    if lang not in ['en', 'zh']:
        lang = 'en'
    
    session['lang'] = lang

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('main.login'))
    return redirect(url_for('main.dashboard'))

app.register_blueprint(main)

if __name__ == '__main__':
    app.run(debug=True,port=5010,host='0.0.0.0')
