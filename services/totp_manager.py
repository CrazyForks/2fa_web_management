import json
import os
from datetime import datetime
import uuid
from utils.config import load_config, save_config

class TotpManager:
    def __init__(self, user_id):
        self.user_id = user_id
        self.config = load_config()
        self._ensure_totp_store()

    def _ensure_totp_store(self):
        """确保TOTP密钥存储相关的配置存在"""
        if 'totp_store' not in self.config:
            self.config['totp_store'] = {}
        if self.user_id not in self.config['totp_store']:
            self.config['totp_store'][self.user_id] = {
                'keys': {}
            }
            save_config(self.config)

    def get_all_keys(self):
        """获取所有TOTP密钥"""
        return [
            {**key, 'id': key_id}
            for key_id, key in self.config['totp_store'][self.user_id]['keys'].items()
        ]

    def get_key(self, key_id):
        """获取指定的TOTP密钥"""
        key = self.config['totp_store'][self.user_id]['keys'].get(key_id)
        if key:
            return {**key, 'id': key_id}
        return None

    def create_key(self, name, secret, issuer=None, digits=6, interval=30):
        """创建新的TOTP密钥"""
        key_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        key = {
            'name': name,
            'secret': secret,
            'issuer': issuer,
            'digits': digits,
            'interval': interval,
            'created_at': now.isoformat(),
            'updated_at': now.isoformat()
        }
        
        self.config['totp_store'][self.user_id]['keys'][key_id] = key
        save_config(self.config)
        
        return {**key, 'id': key_id}

    def update_key(self, key_id, name, secret=None, issuer=None, digits=None, interval=None):
        """更新TOTP密钥"""
        keys = self.config['totp_store'][self.user_id]['keys']
        if key_id not in keys:
            return None
        
        key = keys[key_id]
        key['name'] = name
        if secret:
            key['secret'] = secret
        if issuer is not None:
            key['issuer'] = issuer
        if digits is not None:
            key['digits'] = digits
        if interval is not None:
            key['interval'] = interval
        key['updated_at'] = datetime.utcnow().isoformat()
        
        save_config(self.config)
        return {**key, 'id': key_id}

    def delete_key(self, key_id):
        """删除TOTP密钥"""
        keys = self.config['totp_store'][self.user_id]['keys']
        if key_id not in keys:
            return False
        
        del keys[key_id]
        save_config(self.config)
        return True
