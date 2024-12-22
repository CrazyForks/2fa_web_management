// 当前语言
let currentLang = document.documentElement.lang || 'en';

// 翻译字典
const translations = {
    en: {
        'dashboard.title': '2FA Token Management',
        'dashboard.logout': 'Logout',
        'dashboard.settings': 'Settings',
        'dashboard.change_password': 'Change Password',
        'dashboard.current_password': 'Current Password',
        'dashboard.new_password': 'New Password',
        'dashboard.confirm_password': 'Confirm Password',
        'dashboard.update_password': 'Update Password',
        'dashboard.change_username': 'Change Username',
        'dashboard.current_username': 'Current Username',
        'dashboard.new_username': 'New Username',
        'dashboard.update_username': 'Update Username',
        'dashboard.enable_2fa': 'Enable 2FA',
        'dashboard.disable_2fa': 'Disable 2FA',
        'dashboard.verify_2fa': 'Verify 2FA',
        'dashboard.input_verify_code': 'Input verification code',
        'dashboard.verify': 'Verify',
        'dashboard.verify_error': 'Verification failed',
        'dashboard.add_token': 'Add Token',
        'dashboard.token_name': 'Token Name',
        'dashboard.token_secret': 'Token Secret',
        'dashboard.add_button': 'Add',
        'dashboard.your_tokens': 'Your Tokens',
        'dashboard.no_tokens': 'No tokens yet',
        'dashboard.copy_verify_code': 'Copy verification code',
        'dashboard.view_details': 'View details',
        'dashboard.remove_token': 'Remove token',
        'dashboard.token_details': 'Token Details',
        'dashboard.secret_key': 'Secret Key',
        'dashboard.current_code': 'Current Code',
        'dashboard.time_left': '',
        'dashboard.copy_success': 'Copied!',
        'dashboard.copy_error': 'Failed to copy',
        'flash.password_updated': 'Password updated successfully',
        'flash.password_error': 'Failed to update password',
        'flash.username_updated': 'Username updated successfully',
        'flash.username_error': 'Failed to update username',
        'flash.2fa_enabled': '2FA enabled successfully',
        'flash.2fa_disabled': '2FA disabled successfully',
        'flash.2fa_error': 'Failed to update 2FA status',
        'flash.token_added': 'Token added successfully',
        'flash.token_exists': 'Token with this name already exists',
        'flash.invalid_secret': 'Invalid token secret',
        'flash.token_removed': 'Token removed successfully',
        'flash.missing_fields': 'Please fill in all fields'
    },
    zh: {
        'dashboard.title': '双因素认证令牌管理',
        'dashboard.logout': '退出登录',
        'dashboard.settings': '设置',
        'dashboard.change_password': '修改密码',
        'dashboard.current_password': '当前密码',
        'dashboard.new_password': '新密码',
        'dashboard.confirm_password': '确认密码',
        'dashboard.update_password': '更新密码',
        'dashboard.change_username': '修改用户名',
        'dashboard.current_username': '当前用户名',
        'dashboard.new_username': '新用户名',
        'dashboard.update_username': '更新用户名',
        'dashboard.enable_2fa': '启用双因素认证',
        'dashboard.disable_2fa': '禁用双因素认证',
        'dashboard.verify_2fa': '验证双因素认证',
        'dashboard.input_verify_code': '输入验证码',
        'dashboard.verify': '验证',
        'dashboard.verify_error': '验证失败',
        'dashboard.add_token': '添加令牌',
        'dashboard.token_name': '令牌名称',
        'dashboard.token_secret': '令牌密钥',
        'dashboard.add_button': '添加',
        'dashboard.your_tokens': '你的令牌',
        'dashboard.no_tokens': '暂无令牌',
        'dashboard.copy_verify_code': '复制验证码',
        'dashboard.view_details': '查看详情',
        'dashboard.remove_token': '删除令牌',
        'dashboard.token_details': '令牌详情',
        'dashboard.secret_key': '密钥',
        'dashboard.current_code': '当前验证码',
        'dashboard.time_left': '',
        'dashboard.copy_success': '已复制',
        'dashboard.copy_error': '复制失败',
        'flash.password_updated': '密码更新成功',
        'flash.password_error': '密码更新失败',
        'flash.username_updated': '用户名更新成功',
        'flash.username_error': '用户名更新失败',
        'flash.2fa_enabled': '双因素认证已启用',
        'flash.2fa_disabled': '双因素认证已禁用',
        'flash.2fa_error': '双因素认证状态更新失败',
        'flash.token_added': '令牌添加成功',
        'flash.token_exists': '该名称的令牌已存在',
        'flash.invalid_secret': '无效的令牌密钥',
        'flash.token_removed': '令牌删除成功',
        'flash.missing_fields': '请填写所有字段'
    }
};

// 翻译函数
function t(key) {
    const lang = currentLang;
    if (translations[lang] && translations[lang][key]) {
        return translations[lang][key];
    }
    // 如果找不到翻译，返回英文
    return translations.en[key] || key;
}

// 切换语言
function switchLanguage(lang) {
    if (translations[lang]) {
        currentLang = lang;
        // 触发页面更新
        updatePageTranslations();
    }
}

// 更新页面所有翻译
function updatePageTranslations() {
    // 更新所有带有 data-i18n 属性的元素
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.getAttribute('data-i18n');
        element.textContent = t(key);
    });
}
