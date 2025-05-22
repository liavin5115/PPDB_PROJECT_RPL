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

    // Initialize alert dismissal
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        const closeBtn = alert.querySelector('.btn-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                alert.classList.remove('show');
                setTimeout(() => alert.remove(), 150);
            });
        }
        
        // Auto-hide after 10 seconds (optional)
        // setTimeout(() => {
        //     alert.classList.remove('show');
        //     setTimeout(() => alert.remove(), 150);
        // }, 10000);
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
            const allDocs = [trackDocs, achievementDocs, affirmationDocs, domicileDocs];
            allDocs.forEach(doc => {
                if(doc) doc.style.display = 'none';
            });
            
            // Show relevant documents section based on selected track
            if (this.value === 'achievement' && achievementDocs) {
                trackDocs.style.display = 'block';
                achievementDocs.style.display = 'block';
            } else if (this.value === 'affirmation' && affirmationDocs) {
                trackDocs.style.display = 'block';
                affirmationDocs.style.display = 'block';
            } else if (this.value === 'domicile' && domicileDocs) {
                trackDocs.style.display = 'block';
                domicileDocs.style.display = 'block';
            }
            
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

    // Initialize profile progress
    if (document.querySelector('.profile-progress-section')) {
        new ProfileProgress();
    }

    // Initialize view document buttons
    document.querySelectorAll('.view-doc-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const docType = this.dataset.docType;
            const formId = document.querySelector('#formId').value;
            
            // Show modal instead of opening new window
            const modal = new bootstrap.Modal(document.querySelector(`#fileModal_${docType}`));
            modal.show();
        });
    });

    // Handle document upload buttons
    document.querySelectorAll('.upload-doc-btn').forEach(button => {
        button.addEventListener('click', function() {
            const docType = this.dataset.docType;
            const input = this.closest('.document-item').querySelector('.document-input');
            input.click();
        });
    });

    // Handle document file inputs
    document.querySelectorAll('.document-input').forEach(input => {
        input.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const formData = new FormData();
                formData.append('file', this.files[0]);
                
                const docType = this.dataset.docType;
                updateDocument(docType, formData, this);
            }
        });
    });

    // Handle personal information fields
    document.querySelectorAll('.profile-field').forEach(field => {
        field.addEventListener('change', function() {
            updatePersonalInfo(this);
        });
    });

    // Handle personal information form updates
    const personalInfoForm = document.getElementById('personalInfoForm');
    if (personalInfoForm) {
        const fields = personalInfoForm.querySelectorAll('.profile-field');
        
        fields.forEach(field => {
            field.addEventListener('change', function() {
                updatePersonalInfo(this);
            });
        });
    }

    // Personal Information Edit Functionality
    const editButton = document.getElementById('editPersonalInfo');
    const saveButton = document.getElementById('savePersonalInfo');
    const cancelButton = document.getElementById('cancelPersonalInfo');
    const buttonContainer = document.getElementById('personalInfoButtons');
    const form = document.getElementById('personalInfoForm');
    const fields = form.querySelectorAll('.profile-field');
    let originalValues = {};

    if (editButton) {
        editButton.addEventListener('click', function() {
            // Store original values
            fields.forEach(field => {
                originalValues[field.name] = field.value;
                field.disabled = false;
            });
            
            // Show save/cancel buttons, hide edit button
            buttonContainer.classList.remove('d-none');
            editButton.classList.add('d-none');
        });

        saveButton.addEventListener('click', function() {
            // Collect all form data
            const formData = {};
            fields.forEach(field => {
                formData[field.name] = field.value;
            });

            // Send update request
            fetch('/update-personal-info', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
                },
                body: JSON.stringify(formData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Disable fields and update UI
                    fields.forEach(field => field.disabled = true);
                    buttonContainer.classList.add('d-none');
                    editButton.classList.remove('d-none');
                    
                    // Show success message
                    showAlert('Personal information updated successfully', 'success');
                    
                    // Update progress if needed
                    if (data.completion) {
                        updateProgress(data.completion);
                    }
                } else {
                    showAlert('Error updating information', 'danger');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showAlert('Error updating information', 'danger');
            });
        });

        cancelButton.addEventListener('click', function() {
            // Restore original values
            fields.forEach(field => {
                field.value = originalValues[field.name];
                field.disabled = true;
            });
            
            // Hide save/cancel buttons, show edit button
            buttonContainer.classList.add('d-none');
            editButton.classList.remove('d-none');
        });
    }

    // Photo modal handling
    const photoModals = document.querySelectorAll('[id^="photoModal"]');
    photoModals.forEach(modal => {
        const img = modal.querySelector('img');
        const downloadBtn = modal.querySelector('a.btn-primary');

        // Enable image zoom on click
        if (img) {
            let isZoomed = false;
            img.addEventListener('click', function() {
                if (isZoomed) {
                    this.style.cursor = 'zoom-in';
                    this.style.transform = 'scale(1)';
                    this.style.maxHeight = '70vh';
                } else {
                    this.style.cursor = 'zoom-out';
                    this.style.transform = 'scale(1.5)';
                    this.style.maxHeight = 'none';
                }
                isZoomed = !isZoomed;
            });

            // Add zoom-in cursor by default
            img.style.cursor = 'zoom-in';
        }

        // Handle download button
        if (downloadBtn) {
            downloadBtn.addEventListener('click', (e) => {
                e.stopPropagation();
            });
        }

        // Reset zoom when modal is closed
        modal.addEventListener('hidden.bs.modal', function () {
            if (img) {
                img.style.transform = 'scale(1)';
                img.style.maxHeight = '70vh';
                isZoomed = false;
            }
        });
    });

    // Handle photo modal views
    document.querySelectorAll('.view-doc-btn[data-doc-type="photo"]').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();

            const formId = document.getElementById('formId').value;
            const modalId = `fileModal_photo`;
            const modal = document.getElementById(modalId);

            if (modal) {
                // Disable animations temporarily
                modal.style.transition = 'none';
                modal.style.transform = 'translateZ(0)';
                modal.style.backfaceVisibility = 'hidden';
                modal.style.perspective = '1000';
                
                const img = modal.querySelector('img');
                if (img) {
                    img.style.opacity = '0';
                    img.style.transition = 'opacity 0.2s ease-out';
                    img.onload = function() {
                        img.style.opacity = '1';
                    };
                }

                const modalInstance = new bootstrap.Modal(modal, {
                    backdrop: 'static',
                    keyboard: false
                });

                modalInstance.show();

                // Re-enable animations after modal is shown
                setTimeout(() => {
                    modal.style.transition = '';
                }, 100);
            }
        });
    });

    // Handle status update forms
    document.querySelectorAll('form[action*="update-status"]').forEach(form => {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            const button = form.querySelector('button');
            const originalText = button.innerHTML;
            button.disabled = true;
            button.innerHTML = '<i class="bi bi-hourglass-split me-1"></i>Memproses...';

            try {
                const response = await fetch(form.action, {
                    method: 'POST',
                    body: new FormData(form),
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });

                if (response.ok) {
                    // Refresh halaman setelah sukses
                    window.location.reload();
                } else {
                    throw new Error('Network response was not ok');
                }
            } catch (error) {
                console.error('Error:', error);
                button.innerHTML = originalText;
                button.disabled = false;
                showAlert('Terjadi kesalahan. Silakan coba lagi.', 'danger');
            }
        });
    });

    // Handle status update and payment verification forms
    document.addEventListener('submit', function(e) {
        const form = e.target;
        if (form.matches('.status-update-form, .payment-verify-form')) {
            e.preventDefault();
            
            const button = form.querySelector('button');
            const originalText = button.innerHTML;
            button.disabled = true;
            button.innerHTML = '<i class="bi bi-hourglass-split me-1"></i>Memproses...';

            fetch(form.action, {
                method: 'POST',
                body: new FormData(form),
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    // Refresh halaman
                    window.location.reload();
                } else {
                    throw new Error(data.error || 'Terjadi kesalahan');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                button.innerHTML = originalText;
                button.disabled = false;
                showAlert('Terjadi kesalahan. Silakan coba lagi.', 'danger');
            });
        }
    });

    // Handle payment verification forms
    document.addEventListener('submit', function(e) {
        const form = e.target;
        if (form.matches('.payment-verify-form')) {
            e.preventDefault();
            
            const button = form.querySelector('button');
            const originalHtml = button.innerHTML;
            
            button.disabled = true;
            button.innerHTML = '<i class="bi bi-hourglass-split"></i>';

            fetch(form.action, {
                method: 'POST',
                body: new FormData(form),
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Reload halaman untuk memperbarui status
                    window.location.reload();
                } else {
                    throw new Error(data.error || 'Terjadi kesalahan');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showAlert('Terjadi kesalahan. Silakan coba lagi.', 'danger');
                button.innerHTML = originalHtml;
                button.disabled = false;
            });
        }
    });

    // Show alert function
    function showAlert(message, type = 'info') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 end-0 m-3`;
        alertDiv.style.zIndex = '1050';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.body.appendChild(alertDiv);
        
        // Auto dismiss after 5 seconds
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }
});

function updateDocument(docType, formData, inputElement) {
    const documentItem = inputElement.closest('.document-item');
    const statusElement = documentItem.querySelector('.doc-status');
    
    fetch(`/update-document/${docType}`, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update status text
            if (statusElement) {
                statusElement.textContent = `Uploaded: ${inputElement.files[0].name}`;
            }
            
            // Add view button if it doesn't exist
            const btnGroup = documentItem.querySelector('.btn-group');
            if (!documentItem.querySelector('.view-doc-btn')) {
                const viewBtn = document.createElement('button');
                viewBtn.className = 'btn btn-sm btn-outline-primary view-doc-btn';
                viewBtn.dataset.docType = docType;
                viewBtn.innerHTML = '<i class="bi bi-eye"></i> View';
                btnGroup.insertBefore(viewBtn, btnGroup.firstChild);
                
                // Add click event listener to new view button
                viewBtn.addEventListener('click', function() {
                    const formId = document.querySelector('#formId').value;
                    const modal = new bootstrap.Modal(document.querySelector(`#fileModal_${docType}`));
                    modal.show();
                });
            }
            
            // Show success message
            showAlert('Document updated successfully', 'success');
            
            // Reload page to update modals
            location.reload();
        } else {
            showAlert(data.message || 'Error updating document', 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('Error updating document', 'danger');
    });
}

function updatePersonalInfo(field) {
    const formData = {
        [field.name]: field.value
    };

    fetch('/update-personal-info', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showUpdateStatus(field, true, 'Updated successfully');
            updateProgress(data.completion);
        } else {
            showUpdateStatus(field, false, data.message || 'Update failed');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showUpdateStatus(field, false, 'Error updating information');
    });
}

function showUpdateStatus(element, success, message) {
    const statusDiv = element.parentElement.querySelector('.update-status');
    if (statusDiv) {
        statusDiv.innerHTML = `
            <small class="text-${success ? 'success' : 'danger'} d-flex align-items-center mt-1">
                <i class="bi bi-${success ? 'check-circle' : 'x-circle'}-fill me-1"></i>
                ${message}
            </small>
        `;
        
        setTimeout(() => {
            statusDiv.innerHTML = '';
        }, 3000);
    }
}

function updateProgress(completion) {
    const progressBar = document.querySelector('.progress-bar');
    const progressBadge = document.querySelector('.profile-progress .badge');
    
    if (progressBar && progressBadge) {
        progressBar.style.width = `${completion}%`;
        progressBadge.textContent = `${completion}%`;
        
        const progressClass = completion >= 75 ? 'success' : 
                            completion >= 50 ? 'info' : 
                            completion >= 25 ? 'warning' : 'danger';
        
        progressBar.className = `progress-bar bg-${progressClass}`;
        progressBadge.className = `badge bg-${progressClass}`;
    }
}

function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="bi bi-${type === 'success' ? 'check-circle' : 'exclamation-circle'}-fill me-2"></i>
            <div>${message}</div>
        </div>
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    const alertsContainer = document.querySelector('.notifications-section');
    if (alertsContainer) {
        alertsContainer.appendChild(alertDiv);
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }
}