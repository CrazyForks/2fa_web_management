import json
import os
from typing import List, Optional
from datetime import datetime
import uuid
from models.password_entry import PasswordEntry
from utils.config import load_config, save_config
from cryptography.fernet import Fernet
import base64

class PasswordManager:
    def __init__(self, user_id: str):
        """初始化密码管理器"""
        self.user_id = user_id
        self.config = load_config()
        self._ensure_password_store()
        
        # 获取或创建用户的加密密钥
        self.encryption_key = self._get_or_create_encryption_key()
        self.crypto = Fernet(self.encryption_key)
    
    def _ensure_password_store(self):
        """确保密码存储相关的配置存在"""
        if 'password_store' not in self.config:
            self.config['password_store'] = {}
        if self.user_id not in self.config['password_store']:
            self.config['password_store'][self.user_id] = {
                'encryption_key': PasswordEntry.generate_key().decode(),
                'entries': {}
            }
            save_config(self.config)
    
    def _get_or_create_encryption_key(self) -> bytes:
        """获取或创建用户的加密密钥"""
        user_store = self.config['password_store'][self.user_id]
        if 'encryption_key' not in user_store:
            key = PasswordEntry.generate_key()
            user_store['encryption_key'] = key.decode()
            save_config(self.config)
            return key
        return user_store['encryption_key'].encode()
    
    def create_entry(self, title: str, password: str, username: Optional[str] = None,
                    url: Optional[str] = None, notes: Optional[str] = None,
                    category: str = 'login', totp_secret: Optional[str] = None) -> PasswordEntry:
        """创建新的密码条目"""
        entry_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        # 加密敏感数据
        encrypted_password = PasswordEntry.encrypt_data(self.encryption_key, password)
        encrypted_notes = PasswordEntry.encrypt_data(self.encryption_key, notes) if notes else None
        encrypted_totp = PasswordEntry.encrypt_data(self.encryption_key, totp_secret) if totp_secret else None
        
        entry = PasswordEntry(
            id=entry_id,
            title=title,
            username=username,
            password=encrypted_password,
            url=url,
            notes=encrypted_notes,
            category=category,
            created_at=now,
            updated_at=now,
            totp_secret=encrypted_totp
        )
        
        self.config['password_store'][self.user_id]['entries'][entry_id] = entry.to_dict()
        save_config(self.config)
        
        # 返回解密后的条目
        return self.get_entry(entry_id)
    
    def get_all_entries(self) -> List[PasswordEntry]:
        """获取所有密码条目"""
        entries = []
        for entry_id, entry_data in self.config['password_store'][self.user_id]['entries'].items():
            entry_data = entry_data.copy()  # 创建副本以避免修改原始数据
            # 解密敏感数据
            if entry_data.get('password'):
                entry_data['password'] = PasswordEntry.decrypt_data(self.encryption_key, entry_data['password'])
            if entry_data.get('notes'):
                entry_data['notes'] = PasswordEntry.decrypt_data(self.encryption_key, entry_data['notes'])
            if entry_data.get('totp_secret'):
                entry_data['totp_secret'] = PasswordEntry.decrypt_data(self.encryption_key, entry_data['totp_secret'])
            
            entries.append(PasswordEntry.from_dict(entry_data))
        return entries
    
    def get_entry(self, entry_id: str) -> Optional[PasswordEntry]:
        """获取指定的密码条目"""
        entries = self.config['password_store'][self.user_id]['entries']
        if entry_id not in entries:
            return None
            
        entry_data = entries[entry_id].copy()  # 创建副本以避免修改原始数据
        
        # 解密敏感数据
        if entry_data.get('password'):
            entry_data['password'] = PasswordEntry.decrypt_data(self.encryption_key, entry_data['password'])
        if entry_data.get('notes'):
            entry_data['notes'] = PasswordEntry.decrypt_data(self.encryption_key, entry_data['notes'])
        if entry_data.get('totp_secret'):
            entry_data['totp_secret'] = PasswordEntry.decrypt_data(self.encryption_key, entry_data['totp_secret'])
            
        return PasswordEntry.from_dict(entry_data)
    
    def update_entry(self, entry_id: str, title: Optional[str] = None,
                    password: Optional[str] = None, username: Optional[str] = None,
                    url: Optional[str] = None, notes: Optional[str] = None,
                    category: Optional[str] = None, totp_secret: Optional[str] = None) -> Optional[PasswordEntry]:
        """更新密码条目"""
        # 获取现有条目
        entry = self.get_entry(entry_id)
        if not entry:
            return None
            
        # 创建一个新的条目对象，保留未更新的字段
        updated_data = {
            'id': entry_id,
            'title': title if title is not None else entry.title,
            'username': username if username is not None else entry.username,
            'url': url if url is not None else entry.url,
            'category': category if category is not None else entry.category,
            'created_at': entry.created_at,
            'updated_at': datetime.utcnow()
        }
        
        # 处理需要加密的字段
        if password is not None:
            updated_data['password'] = PasswordEntry.encrypt_data(self.encryption_key, password)
        else:
            # 重新加密现有密码
            updated_data['password'] = PasswordEntry.encrypt_data(self.encryption_key, entry.password)
            
        if notes is not None:
            updated_data['notes'] = PasswordEntry.encrypt_data(self.encryption_key, notes) if notes else None
        elif entry.notes:
            updated_data['notes'] = PasswordEntry.encrypt_data(self.encryption_key, entry.notes)
        else:
            updated_data['notes'] = None
            
        if totp_secret is not None:
            updated_data['totp_secret'] = PasswordEntry.encrypt_data(self.encryption_key, totp_secret) if totp_secret else None
        elif entry.totp_secret:
            updated_data['totp_secret'] = PasswordEntry.encrypt_data(self.encryption_key, entry.totp_secret)
        else:
            updated_data['totp_secret'] = None
            
        # 保存更新后的条目
        self.config['password_store'][self.user_id]['entries'][entry_id] = updated_data
        save_config(self.config)
        
        # 返回解密后的条目
        return self.get_entry(entry_id)
    
    def delete_entry(self, entry_id: str) -> bool:
        """删除密码条目"""
        entries = self.config['password_store'][self.user_id]['entries']
        if entry_id not in entries:
            return False
            
        del entries[entry_id]
        save_config(self.config)
        return True
    
    def search_entries(self, query: str) -> List[PasswordEntry]:
        """搜索密码条目"""
        query = query.lower()
        results = []
        
        for entry in self.get_all_entries():
            if (query in entry.title.lower() or
                (entry.username and query in entry.username.lower()) or
                (entry.url and query in entry.url.lower())):
                results.append(entry)
        
        return results
    
    def decrypt_text(self, encrypted_text: str) -> str:
        """解密文本"""
        try:
            # 将 base64 编码的文本转换为字节
            encrypted_bytes = base64.b64decode(encrypted_text)
            # 解密
            decrypted_bytes = self.crypto.decrypt(encrypted_bytes)
            # 转换为字符串
            return decrypted_bytes.decode('utf-8')
        except Exception as e:
            raise ValueError(f"Failed to decrypt text: {str(e)}")
