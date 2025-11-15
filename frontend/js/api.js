/**
 * API Client for ReComposer
 * Handles all API communication with the backend
 * 
 * Note: Backend CORS must be configured to allow frontend origin.
 * Set CORS_ORIGINS environment variable in backend to include frontend URL.
 */

const API_BASE_URL = 'http://localhost:8000';

class ApiClient {
  constructor(baseURL = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  /**
   * Get authorization headers
   */
  getHeaders() {
    const headers = {
      'Content-Type': 'application/json',
    };

    const token = localStorage.getItem('token');
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    return headers;
  }

  /**
   * Handle API response
   */
  async handleResponse(response) {
    const contentType = response.headers.get('content-type');
    
    if (!response.ok) {
      let errorMessage = 'An error occurred';
      let errorDetails = null;
      
      if (contentType && contentType.includes('application/json')) {
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorData.message || errorMessage;
          // Handle validation errors (422)
          if (response.status === 422 && Array.isArray(errorData.detail)) {
            errorDetails = errorData.detail;
            errorMessage = errorData.detail.map(e => e.msg || e.message || JSON.stringify(e)).join(', ');
          }
          // Handle single detail string
          else if (typeof errorData.detail === 'string') {
            errorMessage = errorData.detail;
          }
        } catch (parseError) {
          // If JSON parsing fails, use status text
          errorMessage = response.statusText || 'An error occurred';
        }
      } else {
        try {
          errorMessage = await response.text() || response.statusText || errorMessage;
        } catch (textError) {
          errorMessage = response.statusText || 'An error occurred';
        }
      }

      const error = new Error(errorMessage);
      error.status = response.status;
      error.details = errorDetails;
      
      // Add specific error messages for common status codes
      if (response.status === 401) {
        error.message = 'Unauthorized. Please login again.';
      } else if (response.status === 403) {
        error.message = 'Access forbidden. You do not have permission to perform this action.';
      } else if (response.status === 404) {
        error.message = 'Resource not found.';
      } else if (response.status === 429) {
        error.message = errorMessage || 'Rate limit exceeded. Please try again later.';
      } else if (response.status === 500) {
        error.message = 'Server error. Please try again later.';
      } else if (response.status === 503) {
        error.message = 'Service unavailable. Please try again later.';
      }
      
      throw error;
    }

    if (contentType && contentType.includes('application/json')) {
      return await response.json();
    }

    return await response.text();
  }

  /**
   * Make GET request
   */
  async get(endpoint) {
    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        method: 'GET',
        headers: this.getHeaders(),
      });

      return await this.handleResponse(response);
    } catch (error) {
      if (error.status === 401) {
        // Unauthorized - clear token and redirect to login
        localStorage.removeItem('token');
        if (window.location.pathname !== '/login.html' && window.location.pathname !== '/frontend/login.html') {
          window.location.href = 'login.html';
        }
      }
      throw error;
    }
  }

  /**
   * Make POST request
   */
  async post(endpoint, data) {
    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify(data),
      });

      return await this.handleResponse(response);
    } catch (error) {
      if (error.status === 401) {
        localStorage.removeItem('token');
        if (window.location.pathname !== '/login.html' && window.location.pathname !== '/frontend/login.html') {
          window.location.href = 'login.html';
        }
      }
      throw error;
    }
  }

  /**
   * Make PUT request
   */
  async put(endpoint, data) {
    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        method: 'PUT',
        headers: this.getHeaders(),
        body: JSON.stringify(data),
      });

      return await this.handleResponse(response);
    } catch (error) {
      if (error.status === 401) {
        localStorage.removeItem('token');
        if (window.location.pathname !== '/login.html' && window.location.pathname !== '/frontend/login.html') {
          window.location.href = 'login.html';
        }
      }
      throw error;
    }
  }

  /**
   * Make DELETE request
   */
  async delete(endpoint) {
    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        method: 'DELETE',
        headers: this.getHeaders(),
      });

      return await this.handleResponse(response);
    } catch (error) {
      if (error.status === 401) {
        localStorage.removeItem('token');
        if (window.location.pathname !== '/login.html' && window.location.pathname !== '/frontend/login.html') {
          window.location.href = 'login.html';
        }
      }
      throw error;
    }
  }

  // --- Rewrite API Methods ---
  
  /**
   * Rewrite an email
   */
  async rewriteEmail(emailText, tone = 'professional') {
    return await this.post('/api/rewrite', {
      email_text: emailText,
      tone: tone,
    });
  }

  /**
   * Get rewrite history/logs
   */
  async getRewriteLogs(limit = 20, offset = 0) {
    return await this.get(`/api/rewrite/logs?limit=${limit}&offset=${offset}`);
  }

  /**
   * Get usage statistics
   */
  async getUsageStats() {
    return await this.get('/api/rewrite/usage');
  }

  // --- Contacts API Methods ---

  /**
   * Get all contacts
   */
  async getContacts(limit = 100, offset = 0, search = '') {
    const params = new URLSearchParams({
      limit: limit.toString(),
      offset: offset.toString(),
    });
    if (search) {
      params.append('search', search);
    }
    return await this.get(`/api/contacts?${params.toString()}`);
  }

  /**
   * Create a new contact
   */
  async createContact(contactData) {
    return await this.post('/api/contacts', contactData);
  }

  /**
   * Update a contact
   */
  async updateContact(contactId, contactData) {
    return await this.put(`/api/contacts/${contactId}`, contactData);
  }

  /**
   * Delete a contact
   */
  async deleteContact(contactId) {
    return await this.delete(`/api/contacts/${contactId}`);
  }

  // --- Campaigns API Methods ---

  /**
   * Get all campaigns
   */
  async getCampaigns(limit = 100, offset = 0) {
    return await this.get(`/api/campaigns?limit=${limit}&offset=${offset}`);
  }

  /**
   * Get campaign details
   */
  async getCampaign(campaignId) {
    return await this.get(`/api/campaigns/${campaignId}`);
  }

  /**
   * Create a new campaign
   */
  async createCampaign(campaignData) {
    return await this.post('/api/campaigns', campaignData);
  }

  /**
   * Update a campaign
   */
  async updateCampaign(campaignId, campaignData) {
    return await this.put(`/api/campaigns/${campaignId}`, campaignData);
  }

  /**
   * Delete a campaign
   */
  async deleteCampaign(campaignId) {
    return await this.delete(`/api/campaigns/${campaignId}`);
  }

  /**
   * Launch a campaign
   */
  async launchCampaign(campaignId) {
    return await this.post(`/api/campaigns/${campaignId}/launch`, {});
  }

  /**
   * Pause a campaign
   */
  async pauseCampaign(campaignId) {
    return await this.post(`/api/campaigns/${campaignId}/pause`, {});
  }
}

// Create and export API client instance
const apiClient = new ApiClient();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = apiClient;
}
