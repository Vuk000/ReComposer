/**
 * Utility Functions
 * Shared helper functions for the frontend
 */

/**
 * Show toast notification
 * @param {string} message - Message to display
 * @param {string} type - Type of toast ('success', 'error', 'info')
 * @param {number} duration - Duration in milliseconds (default: 3000)
 */
function showToast(message, type = 'info', duration = 3000) {
  // Remove existing toast if any
  const existingToast = document.querySelector('.toast');
  if (existingToast) {
    existingToast.remove();
  }

  // Create toast element
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  document.body.appendChild(toast);

  // Show toast
  setTimeout(() => {
    toast.classList.add('show');
  }, 10);

  // Hide and remove toast after duration
  setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => {
      toast.remove();
    }, 300);
  }, duration);
}

/**
 * Show loading spinner
 * @param {HTMLElement} element - Element to show spinner in
 * @returns {HTMLElement} Spinner element
 */
function showSpinner(element) {
  const spinner = document.createElement('div');
  spinner.className = 'spinner';
  element.appendChild(spinner);
  return spinner;
}

/**
 * Hide loading spinner
 * @param {HTMLElement} spinner - Spinner element to remove
 */
function hideSpinner(spinner) {
  if (spinner && spinner.parentNode) {
    spinner.parentNode.removeChild(spinner);
  }
}

/**
 * Format date to readable string
 * @param {string|Date} date - Date to format
 * @returns {string} Formatted date string
 */
function formatDate(date) {
  const d = new Date(date);
  return d.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

/**
 * Format datetime to readable string
 * @param {string|Date} date - Date to format
 * @returns {string} Formatted datetime string
 */
function formatDateTime(date) {
  const d = new Date(date);
  return d.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

/**
 * Get URL parameter value
 * @param {string} name - Parameter name
 * @returns {string|null} Parameter value or null
 */
function getUrlParameter(name) {
  const urlParams = new URLSearchParams(window.location.search);
  return urlParams.get(name);
}

/**
 * Validate email format
 * @param {string} email - Email to validate
 * @returns {boolean} True if valid email
 */
function validateEmail(email) {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
}

/**
 * Validate password strength (matching backend requirements)
 * @param {string} password - Password to validate
 * @returns {object} Validation result with isValid and message
 */
function validatePassword(password) {
  if (password.length < 8) {
    return {
      isValid: false,
      message: 'Password must be at least 8 characters long',
    };
  }
  if (password.length > 128) {
    return {
      isValid: false,
      message: 'Password must be at most 128 characters long',
    };
  }
  const hasLetter = /[a-zA-Z]/.test(password);
  const hasNumber = /[0-9]/.test(password);
  if (!hasLetter || !hasNumber) {
    return {
      isValid: false,
      message: 'Password must contain at least one letter and one number',
    };
  }
  return {
    isValid: true,
    message: '',
  };
}

/**
 * Show error message in form field
 * @param {HTMLElement} field - Form field element
 * @param {string} message - Error message
 */
function showFieldError(field, message) {
  // Remove existing error
  const existingError = field.parentNode.querySelector('.error-message');
  if (existingError) {
    existingError.remove();
  }

  // Add error message
  const errorDiv = document.createElement('div');
  errorDiv.className = 'error-message show';
  errorDiv.textContent = message;
  field.parentNode.appendChild(errorDiv);
  field.style.borderColor = '#d32f2f';
}

/**
 * Clear error message from form field
 * @param {HTMLElement} field - Form field element
 */
function clearFieldError(field) {
  const errorDiv = field.parentNode.querySelector('.error-message');
  if (errorDiv) {
    errorDiv.remove();
  }
  field.style.borderColor = '';
}

/**
 * Disable form button
 * @param {HTMLElement} button - Button element
 */
function disableButton(button) {
  button.disabled = true;
  button.style.opacity = '0.6';
  button.style.cursor = 'not-allowed';
}

/**
 * Enable form button
 * @param {HTMLElement} button - Button element
 */
function enableButton(button) {
  button.disabled = false;
  button.style.opacity = '1';
  button.style.cursor = 'pointer';
}

// Export functions for use in other scripts
if (typeof window !== 'undefined') {
  window.utils = {
    showToast,
    showSpinner,
    hideSpinner,
    formatDate,
    formatDateTime,
    getUrlParameter,
    validateEmail,
    validatePassword,
    showFieldError,
    clearFieldError,
    disableButton,
    enableButton,
  };
}

