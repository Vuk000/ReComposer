/**
 * API Client for ReComposer Backend
 * Handles all API communication with the FastAPI backend
 */

const API_BASE_URL = 'http://localhost:8000';

/**
 * Get JWT token from localStorage
 */
function getToken() {
  return localStorage.getItem('recompose_token');
}

/**
 * Generic API request function
 * @param {string} method - HTTP method (GET, POST, PUT, DELETE)
 * @param {string} endpoint - API endpoint (e.g., '/auth/login')
 * @param {object|null} data - Request body data (null for GET requests)
 * @returns {Promise<object>} Response data
 */
async function apiRequest(method, endpoint, data = null) {
  const url = `${API_BASE_URL}${endpoint}`;
  const options = {
    method: method,
    headers: {
      'Content-Type': 'application/json',
    },
  };

  // Add authentication token if available
  const token = getToken();
  if (token) {
    options.headers['Authorization'] = `Bearer ${token}`;
  }

  // Add request body for POST/PUT requests
  if (data && (method === 'POST' || method === 'PUT')) {
    options.body = JSON.stringify(data);
  }

  try {
    const response = await fetch(url, options);
    const responseData = await response.json().catch(() => ({}));

    // Handle different response statuses
    if (!response.ok) {
      // Handle 401 Unauthorized - redirect to login
      if (response.status === 401) {
        localStorage.removeItem('recompose_token');
        if (window.location.pathname !== '/login.html' && window.location.pathname !== '/frontend/login.html') {
          window.location.href = 'login.html';
        }
        throw new Error('Authentication required. Please log in.');
      }

      // Handle 403 Forbidden
      if (response.status === 403) {
        throw new Error(responseData.detail || 'Access forbidden. You do not have permission to perform this action.');
      }

      // Handle 429 Too Many Requests (rate limit)
      if (response.status === 429) {
        throw new Error(responseData.detail || 'Rate limit exceeded. Please try again later.');
      }

      // Handle 503 Service Unavailable
      if (response.status === 503) {
        throw new Error(responseData.detail || 'Service temporarily unavailable. Please try again later.');
      }

      // Handle validation errors (422)
      if (response.status === 422) {
        const errors = responseData.detail || [];
        if (Array.isArray(errors) && errors.length > 0) {
          const errorMessages = errors.map(err => err.msg || err.message || 'Validation error').join(', ');
          throw new Error(errorMessages);
        }
        throw new Error(responseData.detail || 'Validation error');
      }

      // Generic error handling
      throw new Error(responseData.detail || `Request failed: ${response.statusText}`);
    }

    return responseData;
  } catch (error) {
    // Re-throw API errors
    if (error.message) {
      throw error;
    }
    // Handle network errors
    throw new Error('Network error. Please check your connection and try again.');
  }
}

/**
 * API Client object with convenience methods
 */
const apiClient = {
  /**
   * GET request
   * @param {string} endpoint - API endpoint
   * @returns {Promise<object>} Response data
   */
  async get(endpoint) {
    return apiRequest('GET', endpoint);
  },

  /**
   * POST request
   * @param {string} endpoint - API endpoint
   * @param {object} data - Request body data
   * @returns {Promise<object>} Response data
   */
  async post(endpoint, data) {
    return apiRequest('POST', endpoint, data);
  },

  /**
   * PUT request
   * @param {string} endpoint - API endpoint
   * @param {object} data - Request body data
   * @returns {Promise<object>} Response data
   */
  async put(endpoint, data) {
    return apiRequest('PUT', endpoint, data);
  },

  /**
   * DELETE request
   * @param {string} endpoint - API endpoint
   * @returns {Promise<object>} Response data
   */
  async delete(endpoint) {
    return apiRequest('DELETE', endpoint);
  },

  /**
   * Get base URL
   * @returns {string} Base URL
   */
  getBaseUrl() {
    return API_BASE_URL;
  },
};

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
  module.exports = apiClient;
}

