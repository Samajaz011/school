// Main JavaScript for Education Management System

document.addEventListener('DOMContentLoaded', function() {
    // Create additional dynamic particles
    createDynamicParticles();
    
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Add stagger animation to dashboard cards
    const statCards = document.querySelectorAll('.stat-card');
    statCards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('fade-in');
    });

    // Add intersection observer for animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Observe elements for animation
    document.querySelectorAll('.card, .table-container').forEach(el => {
        observer.observe(el);
    });

    // Add hover sound effects (optional)
    document.querySelectorAll('.btn, .nav-link, .card').forEach(el => {
        el.addEventListener('mouseenter', () => {
            el.style.transform = el.style.transform || '';
        });
    });

    // Form validation enhancement
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Dynamic search functionality
    const searchInputs = document.querySelectorAll('[data-search-target]');
    searchInputs.forEach(input => {
        input.addEventListener('input', function() {
            const target = document.querySelector(this.dataset.searchTarget);
            const searchTerm = this.value.toLowerCase();
            const items = target.querySelectorAll('[data-searchable]');
            
            items.forEach(item => {
                const text = item.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    item.style.display = '';
                } else {
                    item.style.display = 'none';
                }
            });
        });
    });

    // Auto-save functionality for forms
    const autoSaveForms = document.querySelectorAll('[data-auto-save]');
    autoSaveForms.forEach(form => {
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('change', function() {
                const formData = new FormData(form);
                const data = Object.fromEntries(formData);
                localStorage.setItem(`autosave_${form.id}`, JSON.stringify(data));
                
                // Show saved indicator
                showSavedIndicator();
            });
        });

        // Restore auto-saved data
        const saved = localStorage.getItem(`autosave_${form.id}`);
        if (saved) {
            const data = JSON.parse(saved);
            Object.keys(data).forEach(key => {
                const input = form.querySelector(`[name="${key}"]`);
                if (input) {
                    input.value = data[key];
                }
            });
        }
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl+S to save forms
        if (e.ctrlKey && e.key === 's') {
            e.preventDefault();
            const activeForm = document.querySelector('form:focus-within');
            if (activeForm) {
                const submitBtn = activeForm.querySelector('button[type="submit"]');
                if (submitBtn) {
                    submitBtn.click();
                }
            }
        }

        // Ctrl+/ to show help
        if (e.ctrlKey && e.key === '/') {
            e.preventDefault();
            showHelp();
        }
    });

    // Copy code functionality
    const copyButtons = document.querySelectorAll('[data-copy]');
    copyButtons.forEach(button => {
        button.addEventListener('click', function() {
            const target = document.querySelector(this.dataset.copy);
            if (target) {
                navigator.clipboard.writeText(target.textContent).then(() => {
                    showToast('Code copied to clipboard!', 'success');
                });
            }
        });
    });
});

// Utility functions
function showSavedIndicator() {
    const indicator = document.createElement('div');
    indicator.className = 'position-fixed bottom-0 end-0 p-3';
    indicator.innerHTML = `
        <div class="toast show" role="alert">
            <div class="toast-body">
                <i data-feather="check" class="me-2"></i>
                Changes saved automatically
            </div>
        </div>
    `;
    document.body.appendChild(indicator);
    
    // Initialize feather icons
    feather.replace();
    
    setTimeout(() => {
        indicator.remove();
    }, 2000);
}

function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    document.body.appendChild(container);
    return container;
}

function showHelp() {
    const helpModal = document.getElementById('helpModal');
    if (helpModal) {
        const modal = new bootstrap.Modal(helpModal);
        modal.show();
    } else {
        showToast('Help documentation coming soon!', 'info');
    }
}

// Confirmation dialogs
function confirmDelete(message = 'Are you sure you want to delete this item?') {
    return confirm(message);
}

// Format date/time utilities
function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function timeAgo(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffMinutes = Math.floor(diffMs / (1000 * 60));

    if (diffDays > 0) {
        return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    } else if (diffHours > 0) {
        return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    } else if (diffMinutes > 0) {
        return `${diffMinutes} minute${diffMinutes > 1 ? 's' : ''} ago`;
    } else {
        return 'Just now';
    }
}

// Create dynamic particles function
function createDynamicParticles() {
    const particleContainer = document.querySelector('.background-particles');
    if (!particleContainer) return;
    
    // Add more particles dynamically
    for (let i = 11; i <= 25; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        
        // Random properties
        const size = Math.random() * 4 + 2; // 2-6px
        const leftPosition = Math.random() * 100; // 0-100%
        const duration = Math.random() * 10 + 15; // 15-25s
        const delay = Math.random() * 20; // 0-20s
        
        particle.style.width = size + 'px';
        particle.style.height = size + 'px';
        particle.style.left = leftPosition + '%';
        particle.style.animationDuration = duration + 's';
        particle.style.animationDelay = delay + 's';
        
        // Random colors from theme
        const colors = [
            'var(--primary-color)',
            'var(--secondary-color)',
            'var(--accent-color)',
            'var(--warning-color)'
        ];
        const randomColor = colors[Math.floor(Math.random() * colors.length)];
        particle.style.background = randomColor;
        particle.style.opacity = Math.random() * 0.1 + 0.05; // 0.05-0.15
        
        particleContainer.appendChild(particle);
    }
    
    // Create floating icons occasionally
    setInterval(() => {
        if (Math.random() > 0.95) { // 5% chance every second
            createFloatingIcon();
        }
    }, 1000);
}

function createFloatingIcon() {
    const icons = ['📚', '💡', '🎓', '✨', '🔬', '📝', '🎯', '⭐'];
    const icon = document.createElement('div');
    icon.className = 'floating-icon';
    icon.textContent = icons[Math.floor(Math.random() * icons.length)];
    
    icon.style.cssText = `
        position: fixed;
        font-size: 20px;
        opacity: 0.1;
        pointer-events: none;
        z-index: -1;
        left: ${Math.random() * 100}%;
        top: 100%;
        animation: float-icon 8s linear forwards;
    `;
    
    document.body.appendChild(icon);
    
    // Remove after animation
    setTimeout(() => {
        icon.remove();
    }, 8000);
}

// Add floating icon animation CSS
const style = document.createElement('style');
style.textContent = `
    @keyframes float-icon {
        0% {
            transform: translateY(0) rotate(0deg);
            opacity: 0;
        }
        10% {
            opacity: 0.1;
        }
        90% {
            opacity: 0.1;
        }
        100% {
            transform: translateY(-100vh) rotate(360deg);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Export for use in other modules
window.EduSystem = {
    showToast,
    showSavedIndicator,
    confirmDelete,
    formatDateTime,
    timeAgo,
    createDynamicParticles
};
