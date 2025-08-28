document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', (e) => {
        const fileInput = form.querySelector('input[type="file"]');
        if (fileInput && !fileInput.value && form.action.includes('edit')) {
            return true; // Allow edit without new image
        }
        if (fileInput && !fileInput.value) {
            e.preventDefault();
            alert('Please upload an image');
        }
    });
});