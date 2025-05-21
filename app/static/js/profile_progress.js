class ProfileProgress {
    constructor() {
        // Main elements
        this.formFields = document.querySelectorAll('.profile-field');
        this.progressBar = document.querySelector('.progress-bar');
        this.progressBadge = document.querySelector('.progress-badge .badge');
        this.progressStatus = document.querySelector('.progress-status');
        
        // Document elements
        this.documentChecklist = document.querySelector('.document-checklist');
        this.documentInputs = document.querySelectorAll('.document-input');
        this.uploadButtons = document.querySelectorAll('.upload-doc-btn');
        this.viewButtons = document.querySelectorAll('.view-doc-btn');
        
        // Timeout for autosave
        this.autoSaveTimeout = null;
        
        // Initialize
        this.init();
    }

    init() {
        this.attachFieldListeners();
        this.attachDocumentListeners();
        this.initTooltips();
        this.initClipboard();
        this.updateProgress();
    }

    initTooltips() {
        const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
        tooltips.forEach(el => new bootstrap.Tooltip(el));
    }

    initClipboard() {
        const clipboard = new ClipboardJS('.copy-button');
        clipboard.on('success', (e) => {
            const button = e.trigger;
            const icon = button.querySelector('i');
            const originalClass = icon.className;
            
            icon.className = 'bi bi-check text-success';
            setTimeout(() => {
                icon.className = originalClass;
            }, 1500);
            
            e.clearSelection();
        });
    }

    attachFieldListeners() {
        this.formFields.forEach(field => {
            // Handle input changes
            field.addEventListener('input', () => {
                this.handleFieldChange(field);
            });

            // Handle focus for visual feedback
            field.addEventListener('focus', () => {
                field.closest('.input-group')?.classList.add('focused');
            });

            field.addEventListener('blur', () => {
                field.closest('.input-group')?.classList.remove('focused');
                this.autosaveField(field);
            });
        });
    }

    attachDocumentListeners() {
        // Upload button listeners
        this.uploadButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                this.handleDocumentUpload(btn);
            });
        });

        // Document input change listeners
        this.documentInputs.forEach(input => {
            input.addEventListener('change', () => {
                this.handleDocumentChange(input);
            });
        });

        // View button listeners
        this.viewButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                this.handleDocumentView(btn);
            });
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
        const statusIndicator = document.createElement('div');
        statusIndicator.className = 'save-indicator';
        field.parentNode.appendChild(statusIndicator);

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
                this.showSaveSuccess(statusIndicator);
            } else {
                this.showSaveError(statusIndicator);
            }
        } catch (error) {
            console.error('Error saving field:', error);
            this.showSaveError(statusIndicator);
        }

        setTimeout(() => {
            statusIndicator.remove();
        }, 2000);
    }

    showSaveSuccess(indicator) {
        indicator.innerHTML = `
            <div class="save-success">
                <i class="bi bi-check-circle text-success"></i>
                <span class="text-success">Tersimpan</span>
            </div>
        `;
    }

    showSaveError(indicator) {
        indicator.innerHTML = `
            <div class="save-error">
                <i class="bi bi-x-circle text-danger"></i>
                <span class="text-danger">Gagal menyimpan</span>
            </div>
        `;
    }

    calculateProgress() {
        const totalFields = this.formFields.length;
        const completedFields = Array.from(this.formFields)
            .filter(field => field.value.trim() !== '').length;
            
        const totalDocs = this.documentInputs.length;
        const uploadedDocs = Array.from(this.documentInputs)
            .filter(input => input.dataset.uploaded === 'true').length;
            
        const profileWeight = 0.6; // Profile completion is 60% of total progress
        const docsWeight = 0.4;    // Document uploads are 40% of total progress
        
        const profileProgress = (completedFields / totalFields) * profileWeight * 100;
        const docsProgress = (uploadedDocs / totalDocs) * docsWeight * 100;
        
        return Math.round(profileProgress + docsProgress);
    }

    updateProgress() {
        const progress = this.calculateProgress();
        const progressClass = this.getProgressClass(progress);
        
        // Update progress bar
        this.progressBar.style.width = `${progress}%`;
        this.progressBar.className = `progress-bar bg-${progressClass} progress-bar-striped progress-bar-animated`;
        
        // Update badge
        this.progressBadge.textContent = `${progress}%`;
        this.progressBadge.className = `badge bg-${progressClass} rounded-pill`;
        
        // Update status message
        this.updateStatusMessage(progress);
    }

    getProgressClass(progress) {
        if (progress >= 80) return 'success';
        if (progress >= 50) return 'info';
        if (progress >= 25) return 'warning';
        return 'danger';
    }

    updateStatusMessage(progress) {
        const messages = {
            complete: 'Selamat! Semua informasi dan dokumen telah lengkap.',
            almostComplete: 'Hampir selesai! Tinggal sedikit lagi untuk melengkapi pendaftaran.',
            inProgress: 'Terus lengkapi profil dan upload dokumen yang diperlukan.',
            starting: 'Mulai dengan melengkapi informasi profil dasar Anda.'
        };

        let message;
        if (progress === 100) message = messages.complete;
        else if (progress >= 80) message = messages.almostComplete;
        else if (progress >= 40) message = messages.inProgress;
        else message = messages.starting;

        this.progressStatus.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="bi bi-info-circle me-2"></i>
                <div>${message}</div>
            </div>
        `;
    }

    async handleDocumentUpload(btn) {
        const docType = btn.dataset.docType;
        const input = document.querySelector(`.document-input[data-doc-type="${docType}"]`);
        input.click();
    }

    async handleDocumentChange(input) {
        const docType = input.dataset.docType;
        const file = input.files[0];
        if (!file) return;

        const docItem = input.closest('.document-check-item');
        const loadingIndicator = this.showUploadingState(docItem);

        try {
            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch(`/api/upload-document/${docType}`, {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const data = await response.json();
                this.updateDocumentStatus(docType, file.name, true);
                this.updateProgress();
            } else {
                this.updateDocumentStatus(docType, null, false);
            }
        } catch (error) {
            console.error('Error uploading document:', error);
            this.updateDocumentStatus(docType, null, false);
        } finally {
            loadingIndicator.remove();
        }
    }

    showUploadingState(docItem) {
        const indicator = document.createElement('div');
        indicator.className = 'upload-indicator';
        indicator.innerHTML = `
            <div class="spinner-border spinner-border-sm text-primary" role="status">
                <span class="visually-hidden">Mengupload...</span>
            </div>
            <span class="ms-2">Mengupload dokumen...</span>
        `;
        docItem.appendChild(indicator);
        return indicator;
    }

    updateDocumentStatus(docType, filename, success) {
        const docItem = document.querySelector(`.document-check-item[data-doc-type="${docType}"]`);
        if (!docItem) return;

        const statusIcon = docItem.querySelector('.document-status-icon i');
        const statusText = docItem.querySelector('.document-info small');
        const actionButtons = docItem.querySelector('.document-actions');

        if (success) {
            statusIcon.className = 'bi bi-check-circle-fill text-success';
            statusText.textContent = `Terunggah: ${filename}`;
            actionButtons.innerHTML = `
                <div class="btn-group">
                    <button type="button" class="btn btn-sm btn-outline-primary view-doc-btn"
                            data-doc-type="${docType}">
                        <i class="bi bi-eye"></i>
                    </button>
                    <button type="button" class="btn btn-sm btn-outline-secondary upload-doc-btn"
                            data-doc-type="${docType}">
                        <i class="bi bi-arrow-repeat"></i>
                    </button>
                </div>
            `;
        } else {
            statusIcon.className = 'bi bi-exclamation-circle text-warning';
            statusText.textContent = 'Gagal mengunggah dokumen';
            actionButtons.innerHTML = `
                <button type="button" class="btn btn-sm btn-primary upload-doc-btn"
                        data-doc-type="${docType}">
                    <i class="bi bi-upload me-1"></i>Upload
                </button>
            `;
        }

        // Reinitialize tooltips and listeners
        this.initTooltips();
        this.attachDocumentListeners();
    }

    handleDocumentView(btn) {
        const docType = btn.dataset.docType;
        const modalId = `fileModal_${docType}`;
        const modal = document.getElementById(modalId);
        
        if (modal) {
            const bsModal = new bootstrap.Modal(modal);
            bsModal.show();
        }
    }
}

// Initialize on document load
document.addEventListener('DOMContentLoaded', () => {
    if (document.querySelector('.profile-progress-section')) {
        new ProfileProgress();
    }
});