# 2FA Token Management System | 双因素认证令牌管理系统

[English](#english) | [中文](#中文)

## English

### Introduction
2FA Token Management System is a web-based application that helps you manage your two-factor authentication (2FA) tokens securely. It provides a user-friendly interface to add, view, and manage TOTP-based authentication tokens, similar to Google Authenticator but with more features.

### Features
- 🔐 Secure token management
- 🌐 Web-based interface
- 🔄 Real-time token code updates with countdown timer
- 📱 Mobile-friendly responsive design
- 🌍 Multi-language support (English/Chinese)
- 👁️ QR code support for easy token import
- 📋 One-click copy for token codes
- ⚙️ User settings management
- 🎨 Modern and intuitive UI

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/2fa-token-management.git
cd 2fa-token-management
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

4. Access the application at `http://localhost:5010`

### Default Login
- Username: admin
- Password: admin123

### Dependencies
- Python 3.7+
- Flask
- PyOTP
- PyYAML
- qrcode

### Configuration
The system uses `config.yaml` for configuration:
```yaml
auth_forntend:
  username: admin
  password: admin123
  2fa_secret: ''
  is_2fa_enabled: false
2fa_token_list:
  - name: example_token
    secret: YOUR_TOKEN_SECRET
```

### Security Notes
- Change the default admin password immediately after first login
- Keep your token secrets secure
- Enable 2FA for additional security
- Regularly backup your configuration

### License
This project is licensed under the MIT License - see the LICENSE file for details.

---

## 中文

### 简介
双因素认证令牌管理系统是一个基于Web的应用程序，帮助您安全地管理双因素认证(2FA)令牌。它提供了一个用户友好的界面来添加、查看和管理基于TOTP的认证令牌，类似于Google Authenticator但具有更多功能。

### 功能特点
- 🔐 安全的令牌管理
- 🌐 基于Web的界面
- 🔄 实时令牌码更新与倒计时
- 📱 移动端友好的响应式设计
- 🌍 多语言支持（中文/英文）
- 👁️ 支持二维码导入令牌
- 📋 验证码一键复制
- ⚙️ 用户设置管理
- 🎨 现代直观的界面

### 安装说明

1. 克隆仓库：
```bash
git clone https://github.com/yourusername/2fa-token-management.git
cd 2fa-token-management
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 运行应用：
```bash
python app.py
```

4. 访问 `http://localhost:5010`

### 默认登录信息
- 用户名：admin
- 密码：admin123

### 依赖项
- Python 3.7+
- Flask
- PyOTP
- PyYAML
- qrcode

### 配置说明
系统使用 `config.yaml` 进行配置：
```yaml
auth_forntend:
  username: admin
  password: admin123
  2fa_secret: ''
  is_2fa_enabled: false
2fa_token_list:
  - name: example_token
    secret: YOUR_TOKEN_SECRET
```

### 安全提示
- 首次登录后立即修改默认管理员密码
- 确保令牌密钥的安全
- 建议启用双因素认证以提高安全性
- 定期备份配置文件

### 开源协议
本项目采用 MIT 许可证 - 详见 LICENSE 文件
