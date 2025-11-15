/**
 * Utility Functions
 * Common helper functions used across the application
 */

const utils = {
  /**
   * Validate email address
   */
  validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  },

  /**
   * Validate password
   * Must be 8-128 characters, contain at least one letter and one number
   */
  validatePassword(password) {
    if (!password) {
      return {
        isValid: false,
        message: 'Password is required',
      };
    }

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

    // Check for at least one letter and one number
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
  },

  /**
   * Show field error
   */
  showFieldError(field, message) {
    if (!field) return;

    field.classList.add('error');
    
    // Create or update error message element
    let errorElement = field.parentNode.querySelector('.error-message');
    if (!errorElement) {
      errorElement = document.createElement('span');
      errorElement.className = 'error-message';
      field.parentNode.appendChild(errorElement);
    }
    errorElement.textContent = message;
    errorElement.setAttribute('role', 'alert');
  },

  /**
   * Clear field error
   */
  clearFieldError(field) {
    if (!field) return;

    field.classList.remove('error');
    
    const errorElement = field.parentNode.querySelector('.error-message');
    if (errorElement) {
      errorElement.textContent = '';
      errorElement.removeAttribute('role');
    }
  },

  /**
   * Show toast notification
   */
  showToast(message, type = 'info', duration = 3000) {
    // Remove existing toast if any
    const existingToast = document.querySelector('.toast');
    if (existingToast) {
      existingToast.remove();
    }

    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'polite');

    // Add to body
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
  },

  /**
   * Disable button
   */
  disableButton(button) {
    if (button) {
      button.disabled = true;
      button.setAttribute('aria-disabled', 'true');
    }
  },

  /**
   * Enable button
   */
  enableButton(button) {
    if (button) {
      button.disabled = false;
      button.removeAttribute('aria-disabled');
    }
  },

  /**
   * Format date
   */
  formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  },

  /**
   * Format date and time
   */
  formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  },

  /**
   * Debounce function
   */
  debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  },

  /**
   * Copy text to clipboard
   */
  async copyToClipboard(text) {
    try {
      await navigator.clipboard.writeText(text);
      this.showToast('Copied to clipboard!', 'success', 2000);
      return true;
    } catch (error) {
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = text;
      textArea.style.position = 'fixed';
      textArea.style.opacity = '0';
      document.body.appendChild(textArea);
      textArea.select();
      try {
        document.execCommand('copy');
        this.showToast('Copied to clipboard!', 'success', 2000);
        return true;
      } catch (err) {
        this.showToast('Failed to copy to clipboard', 'error');
        return false;
      } finally {
        document.body.removeChild(textArea);
      }
    }
  },

  /**
   * Truncate text
   */
  truncate(text, maxLength) {
    if (text.length <= maxLength) {
      return text;
    }
    return text.substring(0, maxLength) + '...';
  },

  /**
   * Escape HTML
   */
  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  },
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = utils;
}
