// TravelReady AI - Main JavaScript Utilities

document.addEventListener('DOMContentLoaded', function () {
    // Enable Bootstrap tooltips if any
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-dismiss alerts after 6 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 6000);
    });

    // Form validation helpers: ensure travel date is in the future
    const travelDateInput = document.getElementById('travel_date');
    const returnDateInput = document.getElementById('return_date');
    
    if (travelDateInput && returnDateInput) {
        const today = new Date().toISOString().split('T')[0];
        travelDateInput.min = today;
        
        travelDateInput.addEventListener('change', function () {
            returnDateInput.min = this.value;
            if (returnDateInput.value && returnDateInput.value < this.value) {
                returnDateInput.value = this.value;
            }
        });
    }
});

