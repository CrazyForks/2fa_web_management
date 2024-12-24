let tempSecret = null;

function toggleSettings() {
    const settingsPanel = document.getElementById('settings-panel');
    const modalOverlay = document.getElementById('modal-overlay');
    
    if (!settingsPanel.classList.contains('show')) {
        settingsPanel.classList.add('show');
        document.body.style.overflow = 'hidden';
        
        // 创建遮罩层
        const overlay = document.createElement('div');
        overlay.id = 'modal-overlay';
        overlay.className = 'modal-overlay';
        overlay.onclick = toggleSettings;  // 点击遮罩层关闭设置
        document.body.appendChild(overlay);
    } else {
        settingsPanel.classList.remove('show');
        document.body.style.overflow = '';
        
        // 移除遮罩层
        const overlay = document.getElementById('modal-overlay');
        if (overlay) {
            overlay.remove();
        }
    }
}

// 添加 ESC 键关闭功能
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        const settingsPanel = document.getElementById('settings-panel');
        if (settingsPanel.classList.contains('show')) {
            toggleSettings();
        }
    }
});

async function toggle2FA() {
    try {
        const response = await fetch('/api/toggle_2fa', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        const data = await response.json();
        
        if (response.ok) {
            if (data.enabled) {
                // 保存临时密钥
                tempSecret = data.secret;
                
                // 显示二维码和验证表单
                document.getElementById('qr-code').src = data.qr_code;
                document.getElementById('secret-key').textContent = data.secret;
                document.getElementById('qr-container').style.display = 'block';
                
                // 重置验证状态
                document.getElementById('verify-code').value = '';
                document.querySelector('.verify-error').style.display = 'none';
                
                // 隐藏启用按钮，等待验证
                const toggleBtn = document.querySelector('.tfa-toggle');
                toggleBtn.style.display = 'none';
                
                showMessage(data.message, 'info');
            } else {
                // 禁用2FA
                document.getElementById('qr-container').style.display = 'none';
                tempSecret = null;
                
                // 更新按钮和状态
                const toggleBtn = document.querySelector('.tfa-toggle');
                toggleBtn.textContent = '启用';
                toggleBtn.classList.remove('enabled');
                toggleBtn.style.display = 'block';
                
                const statusText = document.querySelector('.status-text');
                statusText.textContent = '未启用';
                
                showMessage(data.message, 'success');

                // 延迟一小段时间后关闭设置面板
                setTimeout(() => {
                    toggleSettings();
                }, 1500);
            }
        } else {
            showMessage(data.message || '操作失败', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showMessage('操作失败，请重试', 'error');
    }
}

async function verify2FA() {
    if (!tempSecret) {
        showMessage('请先启用2FA', 'error');
        return;
    }

    const code = document.getElementById('verify-code').value;
    if (!code || code.length !== 6) {
        showMessage('请输入6位验证码', 'error');
        return;
    }

    try {
        const response = await fetch('/api/verify_2fa', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                secret: tempSecret,
                code: code
            })
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            // 验证成功
            document.querySelector('.verify-error').style.display = 'none';
            
            // 更新按钮状态
            const toggleBtn = document.querySelector('.tfa-toggle');
            toggleBtn.textContent = '禁用';
            toggleBtn.classList.add('enabled');
            toggleBtn.style.display = 'block';
            
            // 更新状态文本
            const statusText = document.querySelector('.status-text');
            statusText.textContent = '已启用';
            
            // 清除临时密钥
            tempSecret = null;
            
            showMessage(data.message, 'success');

            // 延迟一小段时间后关闭设置面板，让用户能看到成功消息
            setTimeout(() => {
                toggleSettings();
            }, 1500);
        } else {
            // 验证失败
            document.querySelector('.verify-error').style.display = 'block';
            showMessage(data.message, 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showMessage('验证失败，请重试', 'error');
    }
}

async function copySecretKey() {
    const secretKey = document.getElementById('secret-key').textContent;
    try {
        await navigator.clipboard.writeText(secretKey);
        const btn = document.querySelector('.copy-btn');
        btn.classList.add('copied');
        setTimeout(() => btn.classList.remove('copied'), 2000);
        showMessage('密钥已复制到剪贴板', 'success');
    } catch (err) {
        console.error('复制失败:', err);
        showMessage('复制失败，请手动复制', 'error');
    }
}

function showMessage(message, type = 'info') {
    const messagesContainer = document.querySelector('.flash-messages') || createMessagesContainer();
    const messageElement = document.createElement('div');
    messageElement.className = `flash-message ${type}`;
    messageElement.textContent = message;
    
    messagesContainer.appendChild(messageElement);
    
    setTimeout(() => {
        messageElement.style.animation = 'slideOut 0.3s ease-in forwards';
        setTimeout(() => messageElement.remove(), 300);
    }, 5000);
}

function createMessagesContainer() {
    const container = document.createElement('div');
    container.className = 'flash-messages';
    document.body.appendChild(container);
    return container;
}

// 密码确认验证
document.querySelectorAll('.settings-form').forEach(form => {
    form.addEventListener('submit', function(e) {
        if (this.querySelector('#new_password')) {
            const newPassword = this.querySelector('#new_password').value;
            const confirmPassword = this.querySelector('#confirm_password').value;
            
            if (newPassword !== confirmPassword) {
                e.preventDefault();
                showMessage('两次输入的密码不一致', 'error');
            }
        }
    });
});

// 密码表单验证
document.getElementById('password-form').addEventListener('submit', function(e) {
    const newPassword = this.querySelector('#new_password').value;
    const confirmPassword = this.querySelector('#confirm_password').value;
    
    if (newPassword !== confirmPassword) {
        e.preventDefault();
        showMessage('两次输入的密码不一致', 'error');
        return false;
    }
    return true;
});

// 密码表单处理
document.querySelectorAll('.toggle-password').forEach(button => {
    button.addEventListener('click', function() {
        const input = this.parentElement.querySelector('input');
        const icon = this.querySelector('i');
        
        if (input.type === 'password') {
            input.type = 'text';
            icon.classList.remove('fa-eye');
            icon.classList.add('fa-eye-slash');
        } else {
            input.type = 'password';
            icon.classList.remove('fa-eye-slash');
            icon.classList.add('fa-eye');
        }
    });
});

// 密码强度检查
const passwordInput = document.getElementById('new_password');
const strengthBar = document.querySelector('.password-strength-bar');
const strengthText = document.querySelector('.password-strength-text');

const requirements = {
    length: str => str.length >= 8,
    uppercase: str => /[A-Z]/.test(str),
    lowercase: str => /[a-z]/.test(str),
    number: str => /[0-9]/.test(str),
    special: str => /[^A-Za-z0-9]/.test(str)
};

function checkPasswordStrength(password) {
    let score = 0;
    let metRequirements = 0;
    
    // 检查每个要求
    for (let [key, test] of Object.entries(requirements)) {
        const requirement = document.querySelector(`[data-requirement="${key}"]`);
        const met = test(password);
        
        if (met) {
            requirement.classList.add('met');
            requirement.querySelector('i').classList.remove('fa-circle');
            requirement.querySelector('i').classList.add('fa-check-circle');
            metRequirements++;
        } else {
            requirement.classList.remove('met');
            requirement.querySelector('i').classList.remove('fa-check-circle');
            requirement.querySelector('i').classList.add('fa-circle');
        }
    }
    
    // 计算强度分数
    score = (metRequirements / Object.keys(requirements).length) * 100;
    
    // 更新强度条
    strengthBar.style.width = `${score}%`;
    if (score < 40) {
        strengthBar.style.backgroundColor = '#dc3545';
        strengthText.textContent = '弱';
        strengthText.style.color = '#dc3545';
    } else if (score < 80) {
        strengthBar.style.backgroundColor = '#ffc107';
        strengthText.textContent = '中';
        strengthText.style.color = '#ffc107';
    } else {
        strengthBar.style.backgroundColor = '#28a745';
        strengthText.textContent = '强';
        strengthText.style.color = '#28a745';
    }
    
    return score >= 100;
}

if (passwordInput) {
    passwordInput.addEventListener('input', function() {
        checkPasswordStrength(this.value);
    });
}
