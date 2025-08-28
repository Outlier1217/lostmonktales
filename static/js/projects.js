document.querySelectorAll('.project-card, .thumbnail').forEach(item => {
    item.addEventListener('click', function() {
        const detailSection = document.getElementById('project-detail');
        detailSection.classList.remove('hidden');
        
        // Smooth scroll to the detail section
        detailSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        
        // Update detail section with clicked item's data
        document.getElementById('detail-image').src = this.dataset.image;
        document.getElementById('detail-name').textContent = this.dataset.name;
        document.getElementById('detail-client').textContent = this.dataset.client || 'Not specified';
        document.getElementById('detail-location').textContent = this.dataset.location || 'Not specified';
        document.getElementById('detail-site-area').textContent = this.dataset.site_area || 'Not specified';
        document.getElementById('detail-built-up-area').textContent = this.dataset.built_up_area || 'Not specified';
        document.getElementById('detail-cost').textContent = this.dataset.cost || 'Not specified';
        document.getElementById('detail-duration').textContent = this.dataset.duration || 'Not specified';
        document.getElementById('detail-dwelling-units').textContent = this.dataset.dwelling_units || 'Not specified';
        
        // Highlight the selected thumbnail
        document.querySelectorAll('.thumbnail').forEach(thumb => {
            thumb.classList.remove('ring-2', 'ring-orange');
        });
        this.classList.add('ring-2', 'ring-orange');
    });
});

// Initialize first project as active if available
document.addEventListener('DOMContentLoaded', function() {
    const firstProject = document.querySelector('.project-card');
    if (firstProject) {
        firstProject.click();
    }
});