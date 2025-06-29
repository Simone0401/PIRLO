function showToast(type, message) {
    const container = document.querySelector('.toast-container');
    const toastEl = document.createElement('div');
    toastEl.className = 'toast-custom';
    toastEl.setAttribute('role', 'alert');
    toastEl.setAttribute('aria-live', 'assertive');
    toastEl.setAttribute('aria-atomic', 'true');

    // Icon and progress color
    let icon, progressColor;
    if (type === 'success') {
    icon = '✅';
    progressColor = '#28a745'; // green
    } else {
    icon = '❌';
    progressColor = '#dc3545'; // red
    }

    // Toast inner HTML
    toastEl.innerHTML = `
    <div class="toast-body">
        <span class="me-2">${icon}</span>
        <div class="flex-grow-1">${message}</div>
        <div class="close-icon">&times;</div>
    </div>
    <div class="toast-progress" style="background:${progressColor}; animation-name: progress-animate; animation-duration:10s;"></div>
    `;

    // Append and animate
    container.append(toastEl);

    // Close icon event
    const closeIcon = toastEl.querySelector('.close-icon');
    closeIcon.addEventListener('click', (e) => {
        e.stopPropagation();
        removeToast(toastEl);
    });

    // Auto-remove after 5s
    setTimeout(() => removeToast(toastEl), 10000);
}

function removeToast(el) {
    el.style.transition = 'opacity 0.3s ease-out, transform 0.3s ease-out';
    el.style.opacity = '0';
    el.style.transform = 'translateX(100%)';
    setTimeout(() => el.remove(), 300);
}