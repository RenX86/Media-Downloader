// Handle form submissions and loading states
document.addEventListener('DOMContentLoaded', () => {
    // Show loading state during downloads
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', (e) => {
            const btn = form.querySelector('button[type="submit"]');
            if (btn) {
                btn.disabled = true;
                btn.innerHTML = `
                    <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                    Processing...
                `;
            }
        });
    });

    // Handle download progress updates (placeholder for future implementation)
    const progressBar = document.querySelector('.progress-bar');
    if (progressBar) {
        // You can implement WebSocket/Socket.io updates here later
    }
});