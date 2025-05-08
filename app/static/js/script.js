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

    // Handle track selection and document visibility
    const trackSelect = document.getElementById('registration_track');
    const trackDocs = document.getElementById('trackDocs');
    const achievementDocs = document.getElementById('achievementDocs');
    const affirmationDocs = document.getElementById('affirmationDocs');
    const domicileDocs = document.getElementById('domicileDocs');
    
    if (trackSelect) {
        trackSelect.addEventListener('change', function() {
            // Hide all doc sections first
            trackDocs.style.display = 'none';
            achievementDocs.style.display = 'none';
            affirmationDocs.style.display = 'none';
            domicileDocs.style.display = 'none';
            
            // Show relevant section based on selection
            if (this.value) {
                trackDocs.style.display = 'block';
                switch(this.value) {
                    case 'achievement':
                        achievementDocs.style.display = 'block';
                        break;
                    case 'affirmation':
                        affirmationDocs.style.display = 'block';
                        break;
                    case 'domicile':
                        domicileDocs.style.display = 'block';
                        break;
                }
            }
        });
    }

    // Initialize toasts
    const toastElList = document.querySelectorAll('.toast');
    const toasts = [...toastElList].map(toastEl => {
        const toast = new bootstrap.Toast(toastEl, {
            autohide: true,
            delay: 3000
        });
        toast.show();
        return toast;
    });

    // Theme toggler
    const themeToggle = document.getElementById('themeToggle');
    const lightIcon = document.getElementById('lightIcon');
    const darkIcon = document.getElementById('darkIcon');

    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const currentTheme = document.documentElement.getAttribute('data-bs-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            
            document.documentElement.setAttribute('data-bs-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            
            lightIcon.classList.toggle('d-none');
            darkIcon.classList.toggle('d-none');
        });
    }

    // Load saved theme
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-bs-theme', savedTheme);
    if (savedTheme === 'dark') {
        lightIcon.classList.add('d-none');
        darkIcon.classList.remove('d-none');
    }

    // File input preview
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            const fileLabel = this.nextElementSibling;
            if (fileLabel && this.files.length > 0) {
                fileLabel.textContent = this.files[0].name;
            }
        });
    });

    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
});