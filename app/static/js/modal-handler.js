class DocumentModalHandler {
    constructor() {
        this.modalInstances = new Map();
        this.currentModal = null;
        this.init();
    }

    init() {
        // Initialize modal instances
        document.querySelectorAll('.document-viewer-modal').forEach(modal => {
            this.optimizeModal(modal);
        });

        // Add click handlers to view buttons
        document.querySelectorAll('.view-doc-btn').forEach(button => {
            button.addEventListener('click', (e) => this.handleViewClick(e, button));
        });

        // Add modal event listeners
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('shown.bs.modal', () => {
                document.body.style.overflow = 'hidden';
            });

            modal.addEventListener('hidden.bs.modal', () => {
                document.body.style.overflow = '';
                this.cleanupModal(modal.id);
            });
        });
    }

    handleViewClick(event, button) {
        event.preventDefault();
        event.stopPropagation();

        const formId = document.getElementById('formId')?.value || '';
        const docType = button.dataset.docType;
        const modalId = `fileModal${formId}_${docType}`;
        const modal = document.getElementById(modalId);

        if (!modal) return;

        // Get or create modal instance
        let modalInstance = this.modalInstances.get(modalId);
        if (!modalInstance) {
            modalInstance = new bootstrap.Modal(modal, {
                backdrop: 'static',
                keyboard: false
            });
            this.modalInstances.set(modalId, modalInstance);
        }

        // Show modal without animation
        modal.classList.remove('fade');
        modalInstance.show();
        // Re-add animation class after short delay
        setTimeout(() => {
            modal.classList.add('fade');
        }, 10);
    }

    cleanupModal(modalId) {
        const instance = this.modalInstances.get(modalId);
        if (instance) {
            instance.dispose();
            this.modalInstances.delete(modalId);
        }
    }

    optimizeModal(modal) {
        // Apply performance optimizations
        modal.style.transform = 'translateZ(0)';
        modal.style.backfaceVisibility = 'hidden';
        modal.style.webkitBackfaceVisibility = 'hidden';
        modal.style.perspective = '1000';
        modal.style.webkitPerspective = '1000';
        modal.style.willChange = 'transform';

        // Optimize images in modal
        const images = modal.querySelectorAll('img');
        images.forEach(img => this.optimizeImage(img));
    }

    optimizeImage(img) {
        img.style.opacity = '0';
        img.style.transition = 'opacity 0.2s ease-out';
        img.addEventListener('load', () => {
            img.style.opacity = '1';
            const spinner = img.previousElementSibling;
            if (spinner && spinner.classList.contains('spinner-border')) {
                spinner.style.display = 'none';
            }
        });
        img.style.transform = 'translateZ(0)';
        img.style.backfaceVisibility = 'hidden';
        img.style.webkitBackfaceVisibility = 'hidden';
    }
}

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', () => {
    window.documentModalHandler = new DocumentModalHandler();
});
