document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide alerts
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
});

// Image preview
function previewImage(input) {
    const preview = document.getElementById('imagePreview');
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            preview.src = e.target.result;
            preview.style.display = 'block';
        }
        reader.readAsDataURL(input.files[0]);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const imageInputs = document.querySelectorAll('input[type="file"][accept*="image"]');
    imageInputs.forEach(input => {
        input.addEventListener('change', function() {
            previewImage(this);
        });
    });
});

// Confirm delete
function confirmDelete(itemName) {
    return confirm(`Delete ${itemName}?`);
}

// Calculate rewards
function calculateRewards() {
    const materialType = document.getElementById('id_material_type');
    const weight = document.getElementById('id_weight');
    const rewardsDisplay = document.getElementById('estimatedRewards');
    
    if (materialType && weight && rewardsDisplay) {
        weight.addEventListener('input', function() {
            const weightValue = parseFloat(this.value);
            const material = materialType.value;
            
            if (weightValue > 0)