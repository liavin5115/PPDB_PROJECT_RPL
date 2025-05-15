class ProfileProgress {
    constructor() {
        this.formFields = document.querySelectorAll('.profile-field');
        this.progressBar = document.querySelector('.profile-progress .progress-bar');
        this.progressBadge = document.querySelector('.profile-progress .badge');
        this.progressMessage = document.querySelector('.profile-status');
        this.autoSaveTimeout = null;
        this.init();
    }

    init() {
        this.attachFieldListeners();
        this.attachDocumentListeners();
        this.initTooltips();
        this.updateProgress();
    }

    initTooltips() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    }

    attachFieldListeners() {
        this.formFields.forEach(field => {
            field.addEventListener('input', () => {
                this.handleFieldChange(field);
            });

            field.addEventListener('blur', () => {
                this.autosaveField(field);
            });
        });

        // Handle document upload buttons
        document.querySelectorAll('.upload-doc-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                this.handleDocumentUpload(btn);
            });
        });
    }

    attachDocumentListeners() {
        document.querySelectorAll('.upload-doc-btn').forEach(btn => {
            btn.addEventListener('click', () => this.handleDocumentUpload(btn));
        });

        document.querySelectorAll('.document-input').forEach(input => {
            input.addEventListener('change', () => this.uploadDocument(input));
        });
    }

    handleFieldChange(field) {
        clearTimeout(this.autoSaveTimeout);
        this.autoSaveTimeout = setTimeout(() => {
            this.autosaveField(field);
        }, 1000);
        
        this.updateProgress();
    }

    async autosaveField(field) {
        try {
            const response = await fetch('/api/update-profile', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
                },
                body: JSON.stringify({
                    field: field.name,
                    value: field.value
                })
            });
            
            if (response.ok) {
                this.showSaveIndicator(field, true);
            } else {
                this.showSaveIndicator(field, false);
            }
        } catch (error) {
            this.showSaveIndicator(field, false);
            console.error('Error saving field:', error);
        }
    }

    calculateProgress() {
        const totalFields = this.formFields.length;
        const completedFields = Array.from(this.formFields)
            .filter(field => field.value.trim() !== '').length;
        return Math.round((completedFields / totalFields) * 100);
    }

    updateProgress() {
        const progress = this.calculateProgress();
        const progressClass = this.getProgressClass(progress);
        
        this.progressBar.style.width = `${progress}%`;
        this.progressBar.className = `progress-bar bg-${progressClass}`;
        this.progressBadge.textContent = `${progress}%`;
        this.progressBadge.className = `badge bg-${progressClass} rounded-pill`;
        
        this.updateStatusMessage(progress);
    }

    showSaveIndicator(field, success) {
        const indicator = document.createElement('span');
        indicator.className = `save-indicator ${success ? 'text-success' : 'text-danger'} ms-2`;
        indicator.innerHTML = success ? 
            '<i class="bi bi-check-circle"></i>' : 
            '<i class="bi bi-x-circle"></i>';
        
        const existing = field.parentNode.querySelector('.save-indicator');
        if (existing) existing.remove();
        
        field.parentNode.appendChild(indicator);
        setTimeout(() => indicator.remove(), 2000);
    }

    getProgressClass(progress) {
        if (progress >= 80) return 'success';
        if (progress >= 40) return 'warning';
        return 'danger';
    }

    updateStatusMessage(progress) {
        const messages = {
            complete: 'Profil Anda sudah lengkap! Silakan lanjutkan dengan upload dokumen.',
            almostComplete: 'Hampir selesai! Tinggal beberapa informasi lagi.',
            inProgress: 'Terus lengkapi informasi profil Anda.',
            starting: 'Silakan lengkapi informasi profil Anda.'
        };

        let message;
        if (progress === 100) message = messages.complete;
        else if (progress >= 80) message = messages.almostComplete;
        else if (progress >= 40) message = messages.inProgress;
        else message = messages.starting;

        this.progressMessage.textContent = message;
    }

    handleDocumentUpload(btn) {
        const docType = btn.dataset.docType;
        const input = document.querySelector(`.document-input[data-doc-type="${docType}"]`);
        input.click();
    }

    async uploadDocument(input) {
        const docType = input.dataset.docType;
        const file = input.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch(`/update-document/${docType}`, {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const data = await response.json();
                this.updateDocumentStatus(docType, file.name);
                this.updateProgress();
                this.showSaveIndicator(input.parentElement, true);
            } else {
                this.showSaveIndicator(input.parentElement, false);
            }
        } catch (error) {
            console.error('Error uploading document:', error);
            this.showSaveIndicator(input.parentElement, false);
        }
    }

    updateDocumentStatus(docType, filename) {
        const statusEl = document.querySelector(`.doc-status[data-doc-type="${docType}"]`);
        if (statusEl) {
            statusEl.textContent = `Uploaded: ${filename}`;
        }
    }
}

// Initialize on document load
document.addEventListener('DOMContentLoaded', () => {
    new ProfileProgress();
});