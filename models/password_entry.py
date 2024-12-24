from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from cryptography.fernet import Fernet
import json
import base64

@dataclass
class PasswordEntry:
    id: str  # UUID
    title: str
    username: Optional[str]
    password: str
    url: Optional[str]
    notes: Optional[str]
    category: str  # login, note, card, identity
    created_at: datetime
    updated_at: datetime
    totp_secret: Optional[str] = None
    totp_digits: int = 6
    totp_interval: int = 30
    
    @staticmethod
    def generate_key():
        """生成新的加密密钥"""
        return Fernet.generate_key()
    
    @staticmethod
    def encrypt_data(key: bytes, data: str) -> str:
        """使用给定的密钥加密数据"""
        if not data:
            return None
        f = Fernet(key)
        return base64.urlsafe_b64encode(f.encrypt(data.encode())).decode()
    
    @staticmethod
    def decrypt_data(key: bytes, encrypted_data: str) -> str:
        """使用给定的密钥解密数据"""
        if not encrypted_data:
            return None
        f = Fernet(key)
        return f.decrypt(base64.urlsafe_b64decode(encrypted_data)).decode()
    
    def to_dict(self) -> dict:
        """将条目转换为字典格式"""
        return {
            'id': self.id,
            'title': self.title,
            'username': self.username,
            'password': self.password,
            'url': self.url,
            'notes': self.notes,
            'category': self.category,
            'created_at': self.created_at.strftime('%Y-%m-%dT%H:%M:%S.%f'),
            'updated_at': self.updated_at.strftime('%Y-%m-%dT%H:%M:%S.%f'),
            'totp_secret': self.totp_secret,
            'totp_digits': self.totp_digits,
            'totp_interval': self.totp_interval
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'PasswordEntry':
        """从字典创建条目"""
        try:
            # 尝试解析不同格式的日期时间
            created_at = data['created_at']
            updated_at = data['updated_at']
            
            if isinstance(created_at, str):
                try:
                    created_at = datetime.fromisoformat(created_at)
                except ValueError:
                    # 尝试解析其他格式
                    created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S.%f')
            
            if isinstance(updated_at, str):
                try:
                    updated_at = datetime.fromisoformat(updated_at)
                except ValueError:
                    # 尝试解析其他格式
                    updated_at = datetime.strptime(updated_at, '%Y-%m-%d %H:%M:%S.%f')
            
            return cls(
                id=data['id'],
                title=data['title'],
                username=data.get('username'),
                password=data['password'],
                url=data.get('url'),
                notes=data.get('notes'),
                category=data['category'],
                created_at=created_at,
                updated_at=updated_at,
                totp_secret=data.get('totp_secret'),
                totp_digits=data.get('totp_digits', 6),
                totp_interval=data.get('totp_interval', 30)
            )
        except Exception as e:
            raise ValueError(f"无法解析密码条目数据: {str(e)}, data: {data}")
