let updateInterval;
let currentDetailToken = null;

function showCopyFeedback(button, success) {
    // 移除旧的反馈元素
    const oldFeedback = button.parentElement.querySelector('.copy-feedback');
    if (oldFeedback) {
        oldFeedback.remove();
    }

    // 创建新的反馈元素
    const feedback = document.createElement('span');
    feedback.className = 'copy-feedback ' + (success ? 'success' : 'error');
    feedback.textContent = success ? t('dashboard.copy_success') : t('dashboard.copy_error');
    
    // 插入反馈元素
    button.parentElement.appendChild(feedback);
    
    // 2秒后移除反馈
    setTimeout(() => {
        feedback.remove();
    }, 2000);
}

function updateTimerProgress(element, secondsRemaining) {
    const circle = element.querySelector('.timer-progress');
    const timerText = element.querySelector('.timer-text');
    const circumference = 2 * Math.PI * 16; // r=16
    
    if (!circle || !timerText) return;
    
    circle.style.strokeDasharray = circumference;
    const offset = circumference * (1 - secondsRemaining / 30);
    circle.style.strokeDashoffset = offset;
    
    // 更新剩余时间文本
    timerText.textContent = secondsRemaining;

    // 根据剩余时间改变颜色
    if (secondsRemaining <= 5) {
        circle.style.stroke = '#dc3545'; // 红色
    } else if (secondsRemaining <= 10) {
        circle.style.stroke = '#ffc107'; // 黄色
    } else {
        circle.style.stroke = '#28a745'; // 绿色
    }
}

function updateTokens() {
    fetch('/api/tokens')
        .then(response => response.json())
        .then(data => {
            const tokenList = document.querySelector('.token-list ul');
            if (!tokenList) return;

            // 清空现有列表
            tokenList.innerHTML = '';

            // 添加新的令牌
            data.tokens.forEach(token => {
                const li = document.createElement('li');
                li.innerHTML = `
                    <div class="token-info">
                        <h3>${token.name}</h3>
                        <div class="code-display">
                            <div class="code-section">
                                <div class="code-with-copy">
                                    <span class="current-code">${token.current_code}</span>
                                    <button class="copy-btn" title="${t('dashboard.copy_verify_code')}">
                                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                            <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                                            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                                        </svg>
                                    </button>
                                </div>
                                <div class="timer-container">
                                    <svg class="timer-svg" viewBox="0 0 36 36">
                                        <circle class="timer-background" cx="18" cy="18" r="16"/>
                                        <circle class="timer-progress" cx="18" cy="18" r="16"/>
                                    </svg>
                                    <span class="timer-text"></span>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="token-actions">
                        <button type="button" class="detail-btn" title="${t('dashboard.view_details')}" onclick="showTokenDetails('${token.name}')">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                                <circle cx="12" cy="12" r="3"></circle>
                            </svg>
                        </button>
                        <form action="/remove_token" method="POST" class="remove-form">
                            <input type="hidden" name="token_name" value="${token.name}">
                            <button type="submit" class="remove-btn" title="${t('dashboard.remove_token')}">
                                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <polyline points="3 6 5 6 21 6"></polyline>
                                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                                    <line x1="10" y1="11" x2="10" y2="17"></line>
                                    <line x1="14" y1="11" x2="14" y2="17"></line>
                                </svg>
                            </button>
                        </form>
                    </div>
                `;

                // 添加复制功能
                const copyBtn = li.querySelector('.copy-btn');
                copyBtn.addEventListener('click', async () => {
                    const code = li.querySelector('.current-code').textContent;
                    try {
                        await navigator.clipboard.writeText(code);
                        showCopyFeedback(copyBtn, true);
                    } catch (err) {
                        console.error('复制失败:', err);
                        showCopyFeedback(copyBtn, false);
                    }
                });

                // 更新圆形进度条
                const timerContainer = li.querySelector('.timer-container');
                updateTimerProgress(timerContainer.parentElement, token.seconds_remaining);

                tokenList.appendChild(li);
            });

            // 如果正在查看令牌详情，也更新详情
            if (currentDetailToken) {
                const token = data.tokens.find(t => t.name === currentDetailToken);
                if (token) {
                    document.getElementById('detail-current-code').textContent = token.current_code;
                    const timerContainer = document.querySelector('#token-details-modal .timer-container');
                    updateTimerProgress(timerContainer.parentElement, token.seconds_remaining);
                }
            }

            // 如果没有令牌，显示提示信息
            if (data.tokens.length === 0) {
                const p = document.createElement('p');
                p.textContent = t('dashboard.no_tokens');
                tokenList.parentElement.appendChild(p);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

async function showTokenDetails(tokenName) {
    try {
        const response = await fetch(`/api/token_details/${tokenName}`);
        const data = await response.json();
        
        if (response.ok) {
            currentDetailToken = tokenName;
            
            // 更新模态框内容
            document.getElementById('detail-token-name').textContent = data.name;
            document.getElementById('detail-qr-code').src = data.qr_code;
            document.getElementById('detail-secret-key').textContent = data.secret;
            document.getElementById('detail-current-code').textContent = data.current_code;
            
            // 更新计时器
            const timerContainer = document.querySelector('#token-details-modal .timer-container');
            updateTimerProgress(timerContainer.parentElement, data.seconds_remaining);
            
            // 显示模态框
            document.getElementById('token-details-modal').classList.add('show');
            document.body.style.overflow = 'hidden';
            
            // 创建遮罩层
            const overlay = document.createElement('div');
            overlay.id = 'modal-overlay';
            overlay.className = 'modal-overlay';
            overlay.onclick = closeTokenDetails;
            document.body.appendChild(overlay);
        } else {
            console.error('获取令牌详情失败:', data.message);
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

function closeTokenDetails() {
    currentDetailToken = null;
    const modal = document.getElementById('token-details-modal');
    modal.classList.remove('show');
    document.body.style.overflow = '';
    
    // 移除遮罩层
    const overlay = document.getElementById('modal-overlay');
    if (overlay) {
        overlay.remove();
    }
}

async function copyDetailSecret() {
    const secretKey = document.getElementById('detail-secret-key').textContent;
    try {
        await navigator.clipboard.writeText(secretKey);
        showCopyFeedback(document.querySelector('#token-details-modal .secret-key .copy-btn'), true);
    } catch (err) {
        console.error('复制失败:', err);
        showCopyFeedback(document.querySelector('#token-details-modal .secret-key .copy-btn'), false);
    }
}

async function copyDetailCode() {
    const code = document.getElementById('detail-current-code').textContent;
    try {
        await navigator.clipboard.writeText(code);
        showCopyFeedback(document.querySelector('#token-details-modal .code-with-copy .copy-btn'), true);
    } catch (err) {
        console.error('复制失败:', err);
        showCopyFeedback(document.querySelector('#token-details-modal .code-with-copy .copy-btn'), false);
    }
}

// ESC键关闭详情
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        const modal = document.getElementById('token-details-modal');
        if (modal.classList.contains('show')) {
            closeTokenDetails();
        }
    }
});

// 页面加载时启动更新
document.addEventListener('DOMContentLoaded', () => {
    updateTokens();
    updateInterval = setInterval(updateTokens, 1000);
});
