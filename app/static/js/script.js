import io from "socket.io-client";

document.addEventListener("DOMContentLoaded", () => {
    const socket = io("/downloads");
    const loadingButton = document.querySelector(".progress-button");
    
    // Submit handler
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            const btn = e.target.querySelector('button[type="submit"]');
            
            if (btn) {
                btn.innerHTML = '<div class="spinner-border text-light" role="status"></div>';
                btn.disabled = true;
                
                // Simulate async task
                setTimeout(() => {
                    btn.innerHTML = 'Download Completed';
                    btn.disabled = false;
                }, 5000);
            }
        });
    });
    
    // Progress updates (future implementation)
    socket.on("progress", data => {
        document.querySelector(".progress-bar").style.width = `${parseInt(data.progress)}%`;
    });
});