// Main JavaScript for GitHub Repository Analyzer

document.addEventListener('DOMContentLoaded', function() {
    initializeThemeToggle();
    initializeTooltips();
    setupFormValidation();
    setupSampleRepoLinks();
    setupProgressBars();
    setupExportFunctionality();
    addAnimationsOnScroll();
});

// Theme Toggle Functionality
function initializeThemeToggle() {
    const themeToggle = document.querySelector('.theme-toggle');
    const currentTheme = localStorage.getItem('theme') || 'light';
    
    // Set initial theme
    document.documentElement.setAttribute('data-theme', currentTheme);
    updateThemeIcon(currentTheme);
    
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateThemeIcon(newTheme);
            
            // Add a nice transition effect
            document.body.style.transition = 'all 0.3s ease';
            setTimeout(() => {
                document.body.style.transition = '';
            }, 300);
        });
    }
}

function updateThemeIcon(theme) {
    const themeToggle = document.querySelector('.theme-toggle');
    if (themeToggle) {
        themeToggle.innerHTML = theme === 'dark' ? '☀️' : '🌙';
        themeToggle.title = theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode';
    }
}

// Add scroll animations
function addAnimationsOnScroll() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    }, observerOptions);
    
    // Observe cards and metric cards
    document.querySelectorAll('.card, .metric-card, .issue-card, .recommendation-card, .action-item').forEach(el => {
        observer.observe(el);
    });
}

// Initialize Bootstrap tooltips
function initializeTooltips() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Setup form validation
function setupFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
    
    // GitHub URL validation
    const repoInput = document.getElementById('repo_url');
    if (repoInput) {
        repoInput.addEventListener('input', function() {
            validateGitHubUrl(this);
        });
    }
}

// Validate GitHub URL format
function validateGitHubUrl(input) {
    const url = input.value.trim();
    const githubPattern = /^https:\/\/github\.com\/[\w\-\.]+\/[\w\-\.]+\/?$/;
    
    if (url && !githubPattern.test(url)) {
        input.setCustomValidity('Please enter a valid GitHub repository URL (e.g., https://github.com/owner/repo)');
        input.classList.add('is-invalid');
    } else {
        input.setCustomValidity('');
        input.classList.remove('is-invalid');
        if (url) {
            input.classList.add('is-valid');
        }
    }
}

// Setup sample repository links
function setupSampleRepoLinks() {
    document.querySelectorAll('.sample-repo').forEach(function(link) {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const url = this.getAttribute('data-url');
            const repoInput = document.getElementById('repo_url');
            if (repoInput) {
                repoInput.value = url;
                validateGitHubUrl(repoInput);
                
                // Animate the input field
                repoInput.style.transition = 'all 0.3s ease';
                repoInput.style.backgroundColor = '#e3f2fd';
                setTimeout(() => {
                    repoInput.style.backgroundColor = '';
                }, 500);
            }
        });
    });
}

// Setup animated progress bars
function setupProgressBars() {
    const progressBars = document.querySelectorAll('.progress-bar[data-value]');
    
    progressBars.forEach(function(bar) {
        const value = parseFloat(bar.getAttribute('data-value'));
        const currentWidth = parseFloat(bar.style.width) || 0;
        
        // Animate progress bar
        animateProgressBar(bar, currentWidth, value);
    });
}

// Animate progress bar to target value
function animateProgressBar(element, start, end) {
    const duration = 1000; // 1 second
    const startTime = performance.now();
    
    function updateProgress(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Easing function (ease-out)
        const easedProgress = 1 - Math.pow(1 - progress, 3);
        const currentValue = start + (end - start) * easedProgress;
        
        element.style.width = currentValue + '%';
        element.setAttribute('aria-valuenow', currentValue);
        
        if (progress < 1) {
            requestAnimationFrame(updateProgress);
        }
    }
    
    requestAnimationFrame(updateProgress);
}

// Setup export functionality
function setupExportFunctionality() {
    const exportButton = document.getElementById('exportButton');
    if (exportButton) {
        exportButton.addEventListener('click', function() {
            const exportModal = new bootstrap.Modal(document.getElementById('exportModal'));
            exportModal.show();
        });
    }
}

// Export analysis report
function exportReport(format) {
    const analysisData = window.analysisData; // Set this in the template
    
    if (!analysisData) {
        console.error('No analysis data available for export');
        return;
    }
    
    switch (format) {
        case 'json':
            exportAsJSON(analysisData);
            break;
        case 'csv':
            exportAsCSV(analysisData);
            break;
        case 'pdf':
            exportAsPDF(analysisData);
            break;
        default:
            console.error('Unknown export format:', format);
    }
}

// Export as JSON
function exportAsJSON(data) {
    const dataStr = JSON.stringify(data, null, 2);
    const dataBlob = new Blob([dataStr], {type: 'application/json'});
    
    const link = document.createElement('a');
    link.href = URL.createObjectURL(dataBlob);
    link.download = `${data.metadata.repository.replace('/', '_')}_analysis.json`;
    link.click();
}

// Export as CSV (simplified)
function exportAsCSV(data) {
    const csvContent = generateCSVContent(data);
    const dataBlob = new Blob([csvContent], {type: 'text/csv'});
    
    const link = document.createElement('a');
    link.href = URL.createObjectURL(dataBlob);
    link.download = `${data.metadata.repository.replace('/', '_')}_analysis.csv`;
    link.click();
}

// Generate CSV content
function generateCSVContent(data) {
    let csv = 'Category,Metric,Value\n';
    
    // Summary metrics
    csv += `Summary,Health Score,${data.summary.health_score}\n`;
    csv += `Summary,Test Coverage,${data.summary.test_coverage}\n`;
    csv += `Summary,Total Issues,${data.summary.total_issues}\n`;
    csv += `Summary,Critical Issues,${data.summary.critical_issues}\n`;
    
    // Test metrics
    if (data.test_analysis && data.test_analysis.coverage_metrics) {
        const metrics = data.test_analysis.coverage_metrics;
        csv += `Test Coverage,Overall,${metrics.overall}\n`;
        csv += `Test Coverage,Line Coverage,${metrics.line_coverage}\n`;
        csv += `Test Coverage,Branch Coverage,${metrics.branch_coverage}\n`;
        csv += `Test Coverage,Function Coverage,${metrics.function_coverage}\n`;
    }
    
    // Issues summary
    if (data.issues_analysis) {
        Object.keys(data.issues_analysis).forEach(category => {
            const categoryData = data.issues_analysis[category];
            if (categoryData && typeof categoryData.count === 'number') {
                csv += `Issues,${category.charAt(0).toUpperCase() + category.slice(1)},${categoryData.count}\n`;
            }
        });
    }
    
    return csv;
}

// Export as PDF (simplified - would need a PDF library in production)
function exportAsPDF(data) {
    // This is a placeholder - in a real implementation, you'd use a library like jsPDF
    alert('PDF export would be implemented with a PDF generation library like jsPDF');
}

// Utility functions
function formatFileSize(bytes) {
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    if (bytes === 0) return '0 Bytes';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

function getSeverityColor(severity) {
    const colors = {
        'critical': 'danger',
        'high': 'warning',
        'medium': 'info',
        'low': 'secondary'
    };
    return colors[severity] || 'secondary';
}

function getCoverageColor(coverage) {
    if (coverage >= 90) return 'success';
    if (coverage >= 75) return 'info';
    if (coverage >= 50) return 'warning';
    return 'danger';
}

// Copy to clipboard functionality
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        // Show success message
        showToast('Copied to clipboard!', 'success');
    }).catch(function(err) {
        console.error('Could not copy text: ', err);
        showToast('Failed to copy to clipboard', 'error');
    });
}

// Show toast notifications
function showToast(message, type = 'info') {
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type === 'success' ? 'success' : 'info'} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    // Add to toast container or create one
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    
    toastContainer.appendChild(toast);
    
    // Show toast
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remove toast element after it's hidden
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

// Search and filter functionality for issues
function filterIssues(category, severity) {
    const issueCards = document.querySelectorAll('.issue-card');
    
    issueCards.forEach(function(card) {
        const cardCategory = card.getAttribute('data-category');
        const cardSeverity = card.getAttribute('data-severity');
        
        let show = true;
        
        if (category && category !== 'all' && cardCategory !== category) {
            show = false;
        }
        
        if (severity && severity !== 'all' && cardSeverity !== severity) {
            show = false;
        }
        
        card.style.display = show ? 'block' : 'none';
    });
}

// Initialize search functionality
function initializeSearch() {
    const searchInput = document.getElementById('issueSearch');
    const categoryFilter = document.getElementById('categoryFilter');
    const severityFilter = document.getElementById('severityFilter');
    
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const issueCards = document.querySelectorAll('.issue-card');
            
            issueCards.forEach(function(card) {
                const text = card.textContent.toLowerCase();
                card.style.display = text.includes(searchTerm) ? 'block' : 'none';
            });
        });
    }
    
    if (categoryFilter) {
        categoryFilter.addEventListener('change', function() {
            filterIssues(this.value, severityFilter ? severityFilter.value : null);
        });
    }
    
    if (severityFilter) {
        severityFilter.addEventListener('change', function() {
            filterIssues(categoryFilter ? categoryFilter.value : null, this.value);
        });
    }
}