# 2FA Web Management System

一个简单的基于Web的双因素认证（2FA）管理系统，用于管理TOTP（基于时间的一次性密码）令牌。

## 重要提示

- 默认登录密码：`admin`
- **首次登录后请立即修改密码！**

## 主要功能

- TOTP令牌管理（添加、查看、删除）
- 实时显示TOTP验证码
- 配置文件使用YAML格式存储
- 简单直观的Web界面

## 技术栈

- 后端：Flask
- 配置存储：YAML
- 前端：HTML + JavaScript
- UI框架：Bootstrap 5
- TOTP实现：pyotp

## 开发环境要求

- Python 3.8+
- 现代浏览器（Chrome、Firefox等）
- 50MB以上磁盘空间

## 快速开始

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 启动应用：
```bash
python app.py
```

3. 在浏览器中访问：`http://localhost:5000`

4. 使用默认密码 `admin` 登录

5. **立即修改默认密码**

## 文件说明

- `config.yaml`: 存储系统配置和TOTP令牌信息
- 建议定期备份此配置文件

## 注意事项

- 所有数据存储在本地config.yaml文件中
- 请定期备份配置文件
- 建议使用强密码替换默认密码
- 配置文件包含敏感信息，请注意访问权限管理

## 许可证

MIT License
