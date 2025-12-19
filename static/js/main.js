// Основной JavaScript файл для деканата

// Автоматическое скрытие уведомлений
document.addEventListener('DOMContentLoaded', function() {
    // Автоскрытие алертов через 5 секунд
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });
    
    // Подсветка активного пункта меню
    highlightActiveNav();
    
    // Инициализация всех форм
    initForms();
});

// Подсветка активного пункта навигации
function highlightActiveNav() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.style.backgroundColor = 'var(--bg-color)';
            link.style.color = 'var(--primary-color)';
        }
    });
}

// Инициализация форм
function initForms() {
    // Подтверждение перед удалением
    const deleteLinks = document.querySelectorAll('[data-confirm]');
    deleteLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            if (!confirm(this.dataset.confirm || 'Вы уверены?')) {
                e.preventDefault();
            }
        });
    });
}

// Утилита для AJAX запросов
async function ajaxRequest(url, method = 'POST', data = {}) {
    try {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        
        const options = {
            method: method,
            headers: {
                'X-CSRFToken': csrfToken,
            }
        };
        
        if (method === 'POST' || method === 'PUT') {
            if (data instanceof FormData) {
                options.body = data;
            } else {
                options.headers['Content-Type'] = 'application/json';
                options.body = JSON.stringify(data);
            }
        }
        
        const response = await fetch(url, options);
        return await response.json();
    } catch (error) {
        console.error('AJAX Error:', error);
        return { success: false, error: error.message };
    }
}

// Показать уведомление
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type}`;
    notification.textContent = message;
    notification.style.position = 'fixed';
    notification.style.bottom = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    notification.style.minWidth = '300px';
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Валидация форм
function validateForm(formElement) {
    const inputs = formElement.querySelectorAll('input[required], select[required], textarea[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.style.borderColor = 'var(--danger-color)';
            isValid = false;
        } else {
            input.style.borderColor = 'var(--border-color)';
        }
    });
    
    return isValid;
}

// Автосохранение для журнала
function initAutoSave() {
    const saveInputs = document.querySelectorAll('[data-autosave]');
    
    saveInputs.forEach(input => {
        input.addEventListener('change', async function() {
            const url = this.dataset.autosaveUrl;
            const data = {
                id: this.dataset.id,
                field: this.dataset.field,
                value: this.value
            };
            
            const result = await ajaxRequest(url, 'POST', data);
            
            if (result.success) {
                showNotification('Сохранено', 'success');
            } else {
                showNotification('Ошибка сохранения', 'error');
            }
        });
    });
}

// Фильтрация таблиц
function initTableFilter() {
    const filterInputs = document.querySelectorAll('[data-table-filter]');
    
    filterInputs.forEach(input => {
        input.addEventListener('input', function() {
            const targetTable = document.querySelector(this.dataset.tableFilter);
            const filterValue = this.value.toLowerCase();
            const rows = targetTable.querySelectorAll('tbody tr');
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(filterValue) ? '' : 'none';
            });
        });
    });
}

// Модальные окна
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = '';
    }
}

// Закрытие модалки при клике вне её
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('modal')) {
        closeModal(e.target.id);
    }
});

// Утилита для работы с датами
function formatDate(date, format = 'dd.mm.yyyy') {
    const d = new Date(date);
    const day = String(d.getDate()).padStart(2, '0');
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const year = d.getFullYear();
    
    return format
        .replace('dd', day)
        .replace('mm', month)
        .replace('yyyy', year);
}

// Проверка на мобильное устройство
function isMobile() {
    return window.innerWidth <= 768;
}

// Плавная прокрутка к элементу
function smoothScrollTo(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.scrollIntoView({ behavior: 'smooth' });
    }
}

// Debounce функция для оптимизации поиска
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Экспорт функций для использования в других скриптах
window.dekanat = {
    ajaxRequest,
    showNotification,
    validateForm,
    openModal,
    closeModal,
    formatDate,
    isMobile,
    smoothScrollTo,
    debounce
};