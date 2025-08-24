// Smart Indian Meal Planner - Frontend JavaScript

document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Initialize form validation
    initializeFormValidation();
    
    // Initialize interactive elements
    initializeInteractiveElements();
    
    // Initialize animations
    initializeAnimations();
    
    // Initialize accessibility features
    initializeAccessibility();
}

function initializeFormValidation() {
    const form = document.getElementById('mealPlanForm');
    if (!form) return;
    
    // Real-time validation
    const inputs = form.querySelectorAll('input, select');
    inputs.forEach(input => {
        input.addEventListener('blur', validateInput);
        input.addEventListener('input', clearValidationError);
    });
    
    // Form submission
    form.addEventListener('submit', handleFormSubmission);
    
    // BMI calculation and calorie estimation
    const weightInput = document.getElementById('weight');
    const heightInput = document.getElementById('height');
    const ageInput = document.getElementById('age');
    const sexSelect = document.getElementById('sex');
    const activitySelect = document.getElementById('activity_level');
    
    if (weightInput && heightInput && ageInput && sexSelect && activitySelect) {
        [weightInput, heightInput, ageInput, sexSelect, activitySelect].forEach(input => {
            input.addEventListener('change', updateCalorieEstimate);
        });
    }
}

function validateInput(event) {
    const input = event.target || event;
    const value = input.value.trim();
    
    // Clear previous validation
    clearValidationError(input);
    
    // Validate based on input type
    switch(input.id) {
        case 'age':
            return validateAge(input, value);
        case 'weight':
            return validateWeight(input, value);
        case 'height':
            return validateHeight(input, value);
        case 'budget':
            return validateBudget(input, value);
        default:
            return validateRequired(input, value);
    }
}

function validateAge(input, value) {
    const age = parseInt(value);
    if (!age || age < 1 || age > 120) {
        showValidationError(input, 'Please enter a valid age between 1 and 120 years.');
        return false;
    }
    return true;
}

function validateWeight(input, value) {
    const weight = parseFloat(value);
    if (!weight || weight < 10 || weight > 300) {
        showValidationError(input, 'Please enter a valid weight between 10 and 300 kg.');
        return false;
    }
    return true;
}

function validateHeight(input, value) {
    const height = parseFloat(value);
    if (!height || height < 50 || height > 250) {
        showValidationError(input, 'Please enter a valid height between 50 and 250 cm.');
        return false;
    }
    return true;
}

function validateBudget(input, value) {
    const budget = parseFloat(value);
    if (!budget || budget < 10) {
        showValidationError(input, 'Budget must be at least ₹10 per day.');
        return false;
    }
    if (budget > 5000) {
        showValidationError(input, 'Budget seems unusually high. Please check the amount.');
        return false;
    }
    return true;
}

function validateRequired(input, value) {
    if (input.hasAttribute('required') && !value) {
        showValidationError(input, 'This field is required.');
        return false;
    }
    return true;
}

function showValidationError(input, message) {
    // Remove existing error
    clearValidationError(input);
    
    // Add error class
    input.classList.add('is-invalid');
    
    // Create error message
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;
    
    // Insert after input
    input.parentNode.insertBefore(errorDiv, input.nextSibling);
}

function clearValidationError(input) {
    if (typeof input === 'object' && input.target) {
        input = input.target;
    }
    
    input.classList.remove('is-invalid');
    const errorDiv = input.parentNode.querySelector('.invalid-feedback');
    if (errorDiv) {
        errorDiv.remove();
    }
}

function handleFormSubmission(event) {
    event.preventDefault();
    
    const form = event.target;
    const submitButton = form.querySelector('button[type="submit"]');
    
    // Validate all required fields
    let isValid = true;
    const inputs = form.querySelectorAll('input[required], select[required]');
    
    inputs.forEach(input => {
        const value = input.value.trim();
        
        // Check if required field is empty
        if (!value) {
            showValidationError(input, 'This field is required.');
            isValid = false;
            return;
        }
        
        // Run specific validation for certain fields
        if (input.id === 'age' || input.id === 'weight' || input.id === 'height' || input.id === 'budget') {
            if (!validateInput(input)) {
                isValid = false;
            }
        }
    });
    
    if (!isValid) {
        showNotification('Please correct the errors in the form.', 'error');
        return;
    }
    
    // Show loading state
    submitButton.classList.add('loading');
    submitButton.disabled = true;
    submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating Plan...';
    
    // Submit form
    setTimeout(() => {
        form.submit();
    }, 500);
}

function updateCalorieEstimate() {
    const age = parseInt(document.getElementById('age').value);
    const weight = parseFloat(document.getElementById('weight').value);
    const height = parseFloat(document.getElementById('height').value);
    const sex = document.getElementById('sex').value;
    const activity = document.getElementById('activity_level').value;
    
    if (age && weight && height && sex && activity) {
        const calories = calculateCalorieNeeds(age, weight, height, sex, activity);
        const protein = Math.round(weight * 1.0);
        
        showCalorieEstimate(calories, protein);
    }
}

function calculateCalorieNeeds(age, weight, height, sex, activity) {
    // Mifflin-St Jeor Equation
    let bmr;
    if (sex === 'male') {
        bmr = 10 * weight + 6.25 * height - 5 * age + 5;
    } else {
        bmr = 10 * weight + 6.25 * height - 5 * age - 161;
    }
    
    const activityMultipliers = {
        'sedentary': 1.2,
        'lightly_active': 1.375,
        'moderately_active': 1.55,
        'very_active': 1.725,
        'extremely_active': 1.9
    };
    
    const multiplier = activityMultipliers[activity] || 1.55;
    return Math.round(bmr * multiplier);
}

function showCalorieEstimate(calories, protein) {
    // Remove existing estimate
    const existingEstimate = document.querySelector('.calorie-estimate');
    if (existingEstimate) {
        existingEstimate.remove();
    }
    
    // Create estimate display
    const estimateDiv = document.createElement('div');
    estimateDiv.className = 'calorie-estimate alert alert-info mt-2';
    estimateDiv.innerHTML = `
        <i class="fas fa-info-circle"></i>
        <strong>Estimated Daily Needs:</strong> ${calories} calories, ${protein}g protein
    `;
    
    // Insert after activity level field
    const activityField = document.getElementById('activity_level').parentNode;
    activityField.appendChild(estimateDiv);
}

function initializeInteractiveElements() {
    // Pantry items selection
    initializePantrySelection();
    
    // Smooth scrolling for navigation
    initializeSmoothScrolling();
    
    // Tooltip initialization
    initializeTooltips();
    
    // Budget slider
    initializeBudgetSlider();
}

function initializePantrySelection() {
    const pantryItems = document.querySelectorAll('.pantry-item');
    
    pantryItems.forEach(item => {
        const checkbox = item.querySelector('input[type="checkbox"]');
        const label = item.querySelector('label');
        
        item.addEventListener('click', function(e) {
            if (e.target !== checkbox) {
                checkbox.checked = !checkbox.checked;
                updatePantryItemState(item, checkbox.checked);
            }
        });
        
        checkbox.addEventListener('change', function() {
            updatePantryItemState(item, this.checked);
        });
    });
}

function updatePantryItemState(item, checked) {
    if (checked) {
        item.classList.add('selected');
        item.style.background = 'var(--primary-orange)';
        item.style.color = 'white';
    } else {
        item.classList.remove('selected');
        item.style.background = '';
        item.style.color = '';
    }
}

function initializeSmoothScrolling() {
    const links = document.querySelectorAll('a[href^="#"]');
    
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            const targetSection = document.querySelector(targetId);
            
            if (targetSection) {
                targetSection.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
}

function initializeTooltips() {
    // Add tooltips to form labels
    const tooltips = {
        'activity_level': 'Choose the option that best describes your typical daily activity level',
        'budget': 'Set your maximum daily food budget in Indian Rupees',
        'dietary_preference': 'Select your dietary restrictions or preferences'
    };
    
    Object.keys(tooltips).forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.setAttribute('title', tooltips[id]);
            element.setAttribute('data-bs-toggle', 'tooltip');
        }
    });
    
    // Initialize Bootstrap tooltips if available
    if (typeof bootstrap !== 'undefined') {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}

function initializeBudgetSlider() {
    const budgetInput = document.getElementById('budget');
    if (!budgetInput) return;
    
    // Create range slider
    const sliderContainer = document.createElement('div');
    sliderContainer.className = 'budget-slider mt-2';
    
    const slider = document.createElement('input');
    slider.type = 'range';
    slider.className = 'form-range';
    slider.min = '10';
    slider.max = '1000';
    slider.step = '10';
    slider.value = budgetInput.value || '100';
    
    sliderContainer.appendChild(slider);
    budgetInput.parentNode.appendChild(sliderContainer);
    
    // Sync slider and input
    slider.addEventListener('input', function() {
        budgetInput.value = this.value;
        budgetInput.dispatchEvent(new Event('input'));
    });
    
    budgetInput.addEventListener('input', function() {
        if (this.value >= 10 && this.value <= 1000) {
            slider.value = this.value;
        }
    });
}

function initializeAnimations() {
    // Intersection Observer for fade-in animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Observe elements for animation
    const animatedElements = document.querySelectorAll('.form-section, .feature-card, .meal-card');
    animatedElements.forEach(el => observer.observe(el));
    
    // Hover animations for interactive elements
    addHoverAnimations();
}

function addHoverAnimations() {
    const interactiveElements = document.querySelectorAll('.meal-card, .feature-card, .alternative-item');
    
    interactiveElements.forEach(element => {
        element.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
        });
        
        element.addEventListener('mouseleave', function() {
            this.style.transform = '';
        });
    });
}

function initializeAccessibility() {
    // Keyboard navigation for custom elements
    initializeKeyboardNavigation();
    
    // ARIA labels and descriptions
    initializeAriaLabels();
    
    // Focus management
    initializeFocusManagement();
}

function initializeKeyboardNavigation() {
    const pantryItems = document.querySelectorAll('.pantry-item');
    
    pantryItems.forEach(item => {
        item.setAttribute('tabindex', '0');
        item.setAttribute('role', 'checkbox');
        
        item.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                const checkbox = this.querySelector('input[type="checkbox"]');
                checkbox.checked = !checkbox.checked;
                updatePantryItemState(this, checkbox.checked);
            }
        });
    });
}

function initializeAriaLabels() {
    // Add ARIA labels to form sections
    const formSections = document.querySelectorAll('.form-section');
    formSections.forEach((section, index) => {
        const title = section.querySelector('.section-title');
        if (title) {
            const titleText = title.textContent.trim();
            section.setAttribute('aria-labelledby', `section-title-${index}`);
            title.id = `section-title-${index}`;
        }
    });
    
    // Add descriptions to complex inputs
    const complexInputs = {
        'budget': 'Enter your maximum daily food budget in Indian Rupees',
        'activity_level': 'Select your typical daily activity level to calculate calorie needs'
    };
    
    Object.keys(complexInputs).forEach(id => {
        const input = document.getElementById(id);
        if (input) {
            const descriptionId = `${id}-description`;
            input.setAttribute('aria-describedby', descriptionId);
            
            // Create description element if it doesn't exist
            if (!document.getElementById(descriptionId)) {
                const description = document.createElement('div');
                description.id = descriptionId;
                description.className = 'sr-only';
                description.textContent = complexInputs[id];
                input.parentNode.appendChild(description);
            }
        }
    });
}

function initializeFocusManagement() {
    // Focus trap for form sections
    const form = document.getElementById('mealPlanForm');
    if (!form) return;
    
    // Ensure first input is focusable
    const firstInput = form.querySelector('input, select');
    if (firstInput) {
        firstInput.addEventListener('focus', function() {
            this.scrollIntoView({ behavior: 'smooth', block: 'center' });
        });
    }
    
    // Manage focus for validation errors
    document.addEventListener('invalid', function(e) {
        e.target.focus();
        e.target.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }, true);
}

function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existingNotifications = document.querySelectorAll('.notification');
    existingNotifications.forEach(n => n.remove());
    
    // Create notification
    const notification = document.createElement('div');
    notification.className = `notification alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Insert at top of page
    const container = document.querySelector('.container-fluid');
    container.insertBefore(notification, container.firstChild);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

// Utility functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Export functions for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        calculateCalorieNeeds,
        validateAge,
        validateWeight,
        validateHeight,
        validateBudget
    };
}
