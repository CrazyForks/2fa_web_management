# 2FA Web Management System

[English](#english) | [中文](#chinese)

<a name="english"></a>
## 🌍 English

### Introduction
A secure and user-friendly web application for managing two-factor authentication (2FA) credentials. This system provides a centralized platform for managing TOTP (Time-based One-Time Password) tokens and secure password storage.

### Core Features

#### 🔐 TOTP Management
- Add, edit, and delete TOTP tokens
- Automatic token generation and refresh
- QR code scanning support
- Token backup and restore functionality

#### 🔑 Password Management
- Secure password storage with encryption
- Password strength assessment
- Password categories and tags
- Password history tracking

#### 🛡️ Security Features
- AES-256 encryption for sensitive data
- Secure session management
- Rate limiting for login attempts
- Activity logging and monitoring
- Regular security audits

#### 🌐 User Interface
- Clean and intuitive dashboard
- Responsive design for mobile devices
- Dark/Light theme support
- Real-time token countdown

#### 🔄 Backup System
- Encrypted backup files
- Automatic scheduled backups
- Backup file verification
- Easy restore process

### Quick Start
```bash
# Install dependencies
pip install -r requirements.txt

# Start the application
python app.py
```

---

<a name="chinese"></a>
## 🌍 中文

### 介绍
一个安全、用户友好的双因素认证（2FA）凭据管理系统。该系统提供了一个集中化的平台，用于管理基于时间的一次性密码（TOTP）令牌和安全密码存储。

### 核心功能

#### 🔐 TOTP管理
- 添加、编辑和删除TOTP令牌
- 自动令牌生成和刷新
- 支持二维码扫描
- 令牌备份和恢复功能

#### 🔑 密码管理
- 加密的安全密码存储
- 密码强度评估
- 密码分类和标签
- 密码历史记录跟踪

#### 🛡️ 安全特性
- AES-256加密敏感数据
- 安全的会话管理
- 登录尝试限制
- 活动日志记录和监控
- 定期安全审计

#### 🌐 用户界面
- 清晰直观的仪表板
- 适配移动设备的响应式设计
- 深色/浅色主题支持
- 实时令牌倒计时

#### 🔄 备份系统
- 加密的备份文件
- 自动定时备份
- 备份文件验证
- 简单的恢复流程

### 快速开始
```bash
# 安装依赖
pip install -r requirements.txt

# 启动应用
python app.py
```

## 技术栈 / Tech Stack
- Backend: Flask
- Database: SQLite
- Encryption: cryptography
- 2FA: pyotp
- Frontend: HTML5, CSS3, JavaScript
- UI Framework: Bootstrap

## 系统要求 / Requirements
- Python 3.8+
- Modern Web Browser
- 500MB+ Free Disk Space

## 许可证 / License
MIT License
