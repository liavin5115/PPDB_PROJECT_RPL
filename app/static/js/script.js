document.addEventListener('DOMContentLoaded', function() {
    // Handle form submission
    const admissionForm = document.querySelector('#admission-form');
    if (admissionForm) {
        admissionForm.addEventListener('submit', function(e) {
            const submitButton = this.querySelector('button[type="submit"]');
            submitButton.disabled = true;
            submitButton.innerHTML = 'Submitting...';
        });
    }
    
    // Handle status update buttons
    const statusForms = document.querySelectorAll('.status-update-form');
    statusForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const button = this.querySelector('button');
            button.disabled = true;
        });
    });
    
    // Handle flash messages auto-hide
    const flashMessages = document.querySelectorAll('.alert');
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => message.remove(), 300);
        }, 5000);
    });
});