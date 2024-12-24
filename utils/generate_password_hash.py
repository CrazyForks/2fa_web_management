from werkzeug.security import generate_password_hash
import yaml

def update_password():
    # 生成密码哈希
    password = 'admin'  # 默认密码
    password_hash = generate_password_hash(password)
    
    # 读取现有配置
    try:
        with open('config.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        config = {}
    
    # 更新配置
    if 'users' not in config:
        config['users'] = {}
    
    if 'admin' not in config['users']:
        config['users']['admin'] = {}
    
    config['users']['admin'].update({
        'username': 'admin',
        'password_hash': password_hash,
        'totp_secret': None,
        'totp_enabled': False
    })
    
    # 保存配置
    with open('config.yaml', 'w', encoding='utf-8') as f:
        yaml.dump(config, f, allow_unicode=True)
    
    print(f'Password hash updated for admin user')
    print(f'Username: admin')
    print(f'Password: admin')

if __name__ == '__main__':
    update_password()
