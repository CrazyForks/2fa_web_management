import yaml
import pyotp
import binascii

# 读取配置文件
def load_config():
    with open('config.yaml', 'r') as f:
        return yaml.safe_load(f)

# 保存配置文件
def save_config(config):
    with open('config.yaml', 'w') as f:
        yaml.dump(config, f)

# 添加2FA令牌
def add_token(name, secret):
    try:
        # 验证密钥是否是有效的 base32 编码
        pyotp.TOTP(secret).now()
        config = load_config()
        config['2fa_token_list'].append({'name': name, 'secret': secret})
        save_config(config)
        return True
    except (binascii.Error, TypeError):
        return False

# 删除2FA令牌
def remove_token(name):
    config = load_config()
    config['2fa_token_list'] = [token for token in config['2fa_token_list'] if token['name'] != name]
    save_config(config)

# 生成当前2FA验证码
def generate_totp(secret):
    try:
        totp = pyotp.TOTP(secret)
        return totp.now()
    except (binascii.Error, TypeError):
        return "Invalid Secret"  # 返回错误信息而不是抛出异常

# 生成一个新的随机 TOTP 密钥
def generate_random_secret():
    """生成一个新的随机 TOTP 密钥"""
    return pyotp.random_base32()
