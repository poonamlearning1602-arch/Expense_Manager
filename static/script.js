document.addEventListener('DOMContentLoaded', function() {
    console.log('Expense Manager loaded');

    const getStartedBtn = document.querySelector('.btn-primary');
    if (getStartedBtn) {
        getStartedBtn.addEventListener('click', function() {
            alert('Feature coming soon! Stay tuned.');
        });
    }

    checkApiHealth();
});

function checkApiHealth() {
    fetch('/api/health')
        .then(response => response.json())
        .then(data => {
            console.log('API Health:', data);
        })
        .catch(error => {
            console.error('Error checking API health:', error);
        });
}

function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(value);
}

function formatDate(date) {
    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    }).format(date);
}
