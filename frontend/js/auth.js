/**
 * Authentication Utilities
 * Handles JWT token storage, retrieval, and user authentication
 */

const TOKEN_KEY = 'recompose_token';

/**
 * Check if user is authenticated
 * @returns {boolean} True if token exists
 */
function isAuthenticated() {
  return !!getToken();
}

/**
 * Get JWT token from localStorage
 * @returns {string|null} JWT token or null
 */
function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

/**
 * Store JWT token in localStorage
 * @param {string} token - JWT token
 */
function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

/**
 * Remove JWT token from localStorage
 */
function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

/**
 * Get current user information
 * @returns {Promise<object>} User object
 */
async function getCurrentUser() {
  if (!isAuthenticated()) {
    throw new Error('Not authenticated');
  }

  try {
    const user = await apiClient.get('/auth/me');
    return user;
  } catch (error) {
    // If token is invalid, clear it
    clearToken();
    throw error;
  }
}

/**
 * Require authentication - redirect to login if not authenticated
 */
function requireAuth() {
  if (!isAuthenticated()) {
    window.location.href = 'login.html';
    return false;
  }
  return true;
}

/**
 * Logout user
 */
function logout() {
  clearToken();
  window.location.href = 'login.html';
}

// Export functions for use in other scripts
if (typeof window !== 'undefined') {
  window.authUtils = {
    isAuthenticated,
    getToken,
    setToken,
    clearToken,
    getCurrentUser,
    requireAuth,
    logout,
  };
}

