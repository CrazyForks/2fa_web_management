// 全局变量
let currentGroupId = null;
let totpIntervals = {};

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', () => {
    loadPasswordGroups();
    initializeEventListeners();
});

// 初始化事件监听器
function initializeEventListeners() {
    // 新建分组按钮
    document.getElementById('new-group-btn').addEventListener('click', () => {
        document.getElementById('group-form').reset();
        document.getElementById('group-modal-title').textContent = t('passwords.new_group');
        document.getElementById('group-modal').dataset.mode = 'create';
        $('#group-modal').modal('show');
    });

    // 新建密码按钮
    document.getElementById('new-password-btn').addEventListener('click', () => {
        if (!currentGroupId) {
            showAlert('error', t('passwords.select_group_first'));
            return;
        }
        document.getElementById('password-form').reset();
        document.getElementById('password-modal-title').textContent = t('passwords.new_password');
        document.getElementById('password-modal').dataset.mode = 'create';
        document.getElementById('custom-fields').innerHTML = '';
        $('#password-modal').modal('show');
    });

    // 分组表单提交
    document.getElementById('group-form').addEventListener('submit', handleGroupSubmit);

    // 密码表单提交
    document.getElementById('password-form').addEventListener('submit', handlePasswordSubmit);

    // 添加自定义字段按钮
    document.getElementById('add-field-btn').addEventListener('click', addCustomField);

    // 生成密码按钮
    document.getElementById('generate-password-btn').addEventListener('click', generatePassword);

    // 搜索框
    document.getElementById('search-input').addEventListener('input', handleSearch);
}

// 加载密码分组
async function loadPasswordGroups() {
    try {
        const response = await fetch('/api/password-groups');
        if (!response.ok) throw new Error('Failed to load password groups');
        
        const groups = await response.json();
        const groupList = document.getElementById('group-list');
        groupList.innerHTML = '';

        groups.forEach(group => {
            const li = document.createElement('li');
            li.className = 'group-item';
            li.dataset.id = group.id;
            li.innerHTML = `
                <div class="d-flex justify-content-between align-items-center">
                    <span>${escapeHtml(group.name)}</span>
                    <div class="group-actions">
                        <button class="btn btn-sm btn-link edit-group" title="${t('passwords.edit_group')}">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-link text-danger delete-group" title="${t('passwords.delete_group')}">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
                ${group.description ? `<small class="text-muted">${escapeHtml(group.description)}</small>` : ''}
            `;

            li.addEventListener('click', (e) => {
                if (!e.target.closest('.group-actions')) {
                    selectGroup(group.id);
                }
            });

            li.querySelector('.edit-group').addEventListener('click', (e) => {
                e.stopPropagation();
                editGroup(group);
            });

            li.querySelector('.delete-group').addEventListener('click', (e) => {
                e.stopPropagation();
                deleteGroup(group.id);
            });

            groupList.appendChild(li);
        });

        if (currentGroupId) {
            const currentGroup = groupList.querySelector(`[data-id="${currentGroupId}"]`);
            if (currentGroup) {
                currentGroup.classList.add('active');
                loadPasswordEntries(currentGroupId);
            } else {
                currentGroupId = null;
                document.getElementById('password-list').innerHTML = '';
            }
        }
    } catch (error) {
        console.error('Error loading password groups:', error);
        showAlert('error', t('passwords.load_groups_error'));
    }
}

// 选择分组
async function selectGroup(groupId) {
    const previousGroup = document.querySelector('.group-item.active');
    if (previousGroup) {
        previousGroup.classList.remove('active');
    }

    const currentGroup = document.querySelector(`.group-item[data-id="${groupId}"]`);
    if (currentGroup) {
        currentGroup.classList.add('active');
        currentGroupId = groupId;
        await loadPasswordEntries(groupId);
    }
}

// 加载密码条目
async function loadPasswordEntries(groupId) {
    try {
        const response = await fetch(`/api/password-groups/${groupId}/entries`);
        if (!response.ok) throw new Error('Failed to load password entries');
        
        const entries = await response.json();
        const passwordList = document.getElementById('password-list');
        passwordList.innerHTML = '';

        entries.forEach(entry => {
            const card = createPasswordCard(entry);
            passwordList.appendChild(card);
        });
    } catch (error) {
        console.error('Error loading password entries:', error);
        showAlert('error', t('passwords.load_entries_error'));
    }
}

// 创建密码卡片
function createPasswordCard(entry) {
    const card = document.createElement('div');
    card.className = 'password-card';
    card.dataset.id = entry.id;

    card.innerHTML = `
        <div class="d-flex justify-content-between align-items-start mb-3">
            <h5 class="password-title mb-0">${escapeHtml(entry.title)}</h5>
            <div class="btn-group">
                <button class="btn btn-sm btn-link edit-password" title="${t('passwords.edit_password')}">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-link text-danger delete-password" title="${t('passwords.delete_password')}">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </div>
        
        <div class="password-info">
            <span class="password-field">${escapeHtml(entry.username)}</span>
            <button class="copy-btn" title="${t('passwords.copy')}" onclick="copyToClipboard('${escapeHtml(entry.username)}')">
                <i class="fas fa-copy"></i>
            </button>
        </div>

        <div class="password-info">
            <span class="password-field">••••••••</span>
            <button class="copy-btn" title="${t('passwords.copy')}" onclick="copyToClipboard('${escapeHtml(entry.password)}')">
                <i class="fas fa-copy"></i>
            </button>
        </div>

        ${entry.url ? `
        <div class="password-info">
            <a href="${escapeHtml(entry.url)}" target="_blank" class="password-field">${escapeHtml(entry.url)}</a>
            <button class="copy-btn" title="${t('passwords.copy')}" onclick="copyToClipboard('${escapeHtml(entry.url)}')">
                <i class="fas fa-copy"></i>
            </button>
        </div>
        ` : ''}

        ${entry.have_totp ? `
        <div class="totp-section">
            <div class="totp-code" id="totp-${entry.id}">------</div>
            <div class="totp-timer">
                <div class="totp-progress" id="totp-progress-${entry.id}"></div>
            </div>
        </div>
        ` : ''}
    `;

    // 添加事件监听器
    card.querySelector('.edit-password').addEventListener('click', () => editPassword(entry));
    card.querySelector('.delete-password').addEventListener('click', () => deletePassword(entry.id));

    // 如果启用了TOTP，开始更新TOTP代码
    if (entry.have_totp) {
        updateTOTPCode(entry.id);
    }

    return card;
}

// 更新TOTP代码
async function updateTOTPCode(entryId) {
    try {
        const response = await fetch(`/api/password-groups/${currentGroupId}/entries/${entryId}/totp`);
        if (!response.ok) throw new Error('Failed to get TOTP code');
        
        const data = await response.json();
        const codeElement = document.getElementById(`totp-${entryId}`);
        const progressElement = document.getElementById(`totp-progress-${entryId}`);
        
        if (codeElement && progressElement) {
            codeElement.textContent = data.code;
            
            // 更新进度条
            const percentage = (data.remaining_seconds / data.interval) * 100;
            progressElement.style.width = `${percentage}%`;

            // 清除之前的定时器
            if (totpIntervals[entryId]) {
                clearInterval(totpIntervals[entryId]);
            }

            // 设置新的定时器
            totpIntervals[entryId] = setInterval(() => {
                updateTOTPCode(entryId);
            }, data.remaining_seconds * 1000);
        }
    } catch (error) {
        console.error('Error updating TOTP code:', error);
    }
}

// 处理分组表单提交
async function handleGroupSubmit(event) {
    event.preventDefault();
    const form = event.target;
    const mode = document.getElementById('group-modal').dataset.mode;
    const groupId = form.dataset.groupId;

    const data = {
        name: form.querySelector('[name="name"]').value,
        description: form.querySelector('[name="description"]').value
    };

    try {
        let response;
        if (mode === 'create') {
            response = await fetch('/api/password-groups', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
        } else {
            response = await fetch(`/api/password-groups/${groupId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
        }

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error);
        }

        $('#group-modal').modal('hide');
        await loadPasswordGroups();
        showAlert('success', t(mode === 'create' ? 'flash.group_created' : 'flash.group_updated'));
    } catch (error) {
        console.error('Error saving group:', error);
        showAlert('error', error.message);
    }
}

// 处理密码表单提交
async function handlePasswordSubmit(event) {
    event.preventDefault();
    const form = event.target;
    const mode = document.getElementById('password-modal').dataset.mode;
    const entryId = form.dataset.entryId;

    // 收集自定义字段
    const customFields = [];
    form.querySelectorAll('.custom-field').forEach(field => {
        const nameInput = field.querySelector('[name="field_name[]"]');
        const valueInput = field.querySelector('[name="field_value[]"]');
        if (nameInput.value && valueInput.value) {
            customFields.push({
                name: nameInput.value,
                value: valueInput.value
            });
        }
    });

    const data = {
        title: form.querySelector('[name="title"]').value,
        username: form.querySelector('[name="username"]').value,
        password: form.querySelector('[name="password"]').value,
        url: form.querySelector('[name="url"]').value,
        notes: form.querySelector('[name="notes"]').value,
        have_totp: form.querySelector('[name="have_totp"]').checked,
        totp_token: form.querySelector('[name="totp_token"]').value,
        custom_fields: customFields
    };

    try {
        let response;
        if (mode === 'create') {
            response = await fetch(`/api/password-groups/${currentGroupId}/entries`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
        } else {
            response = await fetch(`/api/password-groups/${currentGroupId}/entries/${entryId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
        }

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error);
        }

        $('#password-modal').modal('hide');
        await loadPasswordEntries(currentGroupId);
        showAlert('success', t(mode === 'create' ? 'flash.password_created' : 'flash.password_updated'));
    } catch (error) {
        console.error('Error saving password:', error);
        showAlert('error', error.message);
    }
}

// 编辑分组
function editGroup(group) {
    const form = document.getElementById('group-form');
    form.dataset.groupId = group.id;
    form.querySelector('[name="name"]').value = group.name;
    form.querySelector('[name="description"]').value = group.description || '';
    
    document.getElementById('group-modal-title').textContent = t('passwords.edit_group');
    document.getElementById('group-modal').dataset.mode = 'edit';
    $('#group-modal').modal('show');
}

// 删除分组
async function deleteGroup(groupId) {
    if (!confirm(t('passwords.confirm_delete'))) return;

    try {
        const response = await fetch(`/api/password-groups/${groupId}`, {
            method: 'DELETE'
        });

        if (!response.ok) throw new Error('Failed to delete group');

        if (currentGroupId === groupId) {
            currentGroupId = null;
            document.getElementById('password-list').innerHTML = '';
        }

        await loadPasswordGroups();
        showAlert('success', t('flash.group_deleted'));
    } catch (error) {
        console.error('Error deleting group:', error);
        showAlert('error', t('passwords.delete_group_error'));
    }
}

// 编辑密码
function editPassword(entry) {
    const form = document.getElementById('password-form');
    form.dataset.entryId = entry.id;
    form.querySelector('[name="title"]').value = entry.title;
    form.querySelector('[name="username"]').value = entry.username;
    form.querySelector('[name="password"]').value = entry.password;
    form.querySelector('[name="url"]').value = entry.url || '';
    form.querySelector('[name="notes"]').value = entry.notes || '';
    form.querySelector('[name="have_totp"]').checked = entry.have_totp;
    form.querySelector('[name="totp_token"]').value = entry.totp_token || '';

    // 清空并重新添加自定义字段
    const customFieldsContainer = document.getElementById('custom-fields');
    customFieldsContainer.innerHTML = '';
    entry.custom_fields.forEach(field => {
        addCustomField(field.name, field.value);
    });

    document.getElementById('password-modal-title').textContent = t('passwords.edit_password');
    document.getElementById('password-modal').dataset.mode = 'edit';
    $('#password-modal').modal('show');
}

// 删除密码
async function deletePassword(entryId) {
    if (!confirm(t('passwords.confirm_delete'))) return;

    try {
        const response = await fetch(`/api/password-groups/${currentGroupId}/entries/${entryId}`, {
            method: 'DELETE'
        });

        if (!response.ok) throw new Error('Failed to delete password');

        await loadPasswordEntries(currentGroupId);
        showAlert('success', t('flash.password_deleted'));
    } catch (error) {
        console.error('Error deleting password:', error);
        showAlert('error', t('passwords.delete_password_error'));
    }
}

// 添加自定义字段
function addCustomField(name = '', value = '') {
    const container = document.getElementById('custom-fields');
    const field = document.createElement('div');
    field.className = 'custom-field mb-3';
    field.innerHTML = `
        <div class="row">
            <div class="col">
                <input type="text" name="field_name[]" class="form-control" placeholder="${t('passwords.field_name')}" value="${escapeHtml(name)}">
            </div>
            <div class="col">
                <input type="text" name="field_value[]" class="form-control" placeholder="${t('passwords.field_value')}" value="${escapeHtml(value)}">
            </div>
            <div class="col-auto">
                <button type="button" class="btn btn-danger remove-field">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        </div>
    `;

    field.querySelector('.remove-field').addEventListener('click', () => field.remove());
    container.appendChild(field);
}

// 生成随机密码
async function generatePassword() {
    try {
        const response = await fetch('/api/generate-password');
        if (!response.ok) throw new Error('Failed to generate password');
        
        const data = await response.json();
        document.querySelector('[name="password"]').value = data.password;
    } catch (error) {
        console.error('Error generating password:', error);
        showAlert('error', t('passwords.generate_password_error'));
    }
}

// 复制到剪贴板
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showAlert('success', t('passwords.copied_to_clipboard'), 2000);
    } catch (error) {
        console.error('Error copying to clipboard:', error);
        showAlert('error', t('passwords.copy_error'));
    }
}

// 搜索密码
function handleSearch(event) {
    const searchTerm = event.target.value.toLowerCase();
    const cards = document.querySelectorAll('.password-card');
    
    cards.forEach(card => {
        const title = card.querySelector('.password-title').textContent.toLowerCase();
        const username = card.querySelector('.password-info').textContent.toLowerCase();
        const isVisible = title.includes(searchTerm) || username.includes(searchTerm);
        card.style.display = isVisible ? '' : 'none';
    });
}

// 显示提示消息
function showAlert(type, message, duration = 3000) {
    const alertContainer = document.getElementById('alert-container');
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    alertContainer.appendChild(alert);

    if (duration > 0) {
        setTimeout(() => {
            alert.remove();
        }, duration);
    }
}

// HTML转义
function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// 清理资源
window.addEventListener('beforeunload', () => {
    // 清除所有TOTP更新定时器
    Object.values(totpIntervals).forEach(interval => clearInterval(interval));
});
