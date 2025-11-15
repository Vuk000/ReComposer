/**
 * Authentication Utilities
 * Handles user authentication, token management, and user session
 */

const authUtils = {
  /**
   * Check if user is authenticated
   */
  isAuthenticated() {
    const token = localStorage.getItem('token');
    return !!token;
  },

  /**
   * Get stored token
   */
  getToken() {
    return localStorage.getItem('token');
  },

  /**
   * Set authentication token
   */
  setToken(token) {
    localStorage.setItem('token', token);
  },

  /**
   * Remove authentication token
   */
  removeToken() {
    localStorage.removeItem('token');
  },

  /**
   * Get current user information
   */
  async getCurrentUser() {
    if (!this.isAuthenticated()) {
      throw new Error('Not authenticated');
    }

    try {
      const response = await fetch('http://localhost:8000/auth/me', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${this.getToken()}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          this.removeToken();
          throw new Error('Session expired. Please login again.');
        }
        throw new Error('Failed to get user information');
      }

      return await response.json();
    } catch (error) {
      this.removeToken();
      throw error;
    }
  },

  /**
   * Logout user
   */
  logout() {
    this.removeToken();
    window.location.href = 'login.html';
  },

  /**
   * Require authentication - redirect to login if not authenticated
   */
  requireAuth() {
    if (!this.isAuthenticated()) {
      window.location.href = 'login.html';
      return false;
    }
    return true;
  },

  /**
   * Decode JWT token (basic implementation)
   */
  decodeToken(token) {
    try {
      const base64Url = token.split('.')[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const jsonPayload = decodeURIComponent(
        atob(base64)
          .split('')
          .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
          .join('')
      );
      return JSON.parse(jsonPayload);
    } catch (error) {
      return null;
    }
  },

  /**
   * Check if token is expired
   */
  isTokenExpired(token) {
    const decoded = this.decodeToken(token);
    if (!decoded || !decoded.exp) {
      return true;
    }

    const currentTime = Date.now() / 1000;
    return decoded.exp < currentTime;
  },
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = authUtils;
}
