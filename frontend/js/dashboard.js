/**
 * Dashboard Functionality
 * Handles all dashboard interactions and API calls
 */

let currentUser = null;
let currentSection = 'email';
let contactsList = [];
let campaignsList = [];

// Initialize dashboard on page load
document.addEventListener('DOMContentLoaded', async () => {
  // Check authentication
  if (typeof authUtils !== 'undefined' && !authUtils.requireAuth()) {
    return;
  }

  // Load user info
  try {
    if (typeof authUtils !== 'undefined') {
      currentUser = await authUtils.getCurrentUser();
    } else {
      // Fallback if authUtils not loaded
      const token = localStorage.getItem('token');
      if (!token) {
        window.location.href = 'login.html';
        return;
      }
      const response = await fetch('http://localhost:8000/auth/me', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      if (response.ok) {
        currentUser = await response.json();
      } else {
        window.location.href = 'login.html';
        return;
      }
    }

    const userNameElement = document.getElementById('userName');
    if (userNameElement && currentUser) {
      userNameElement.textContent = currentUser.email ? currentUser.email.split('@')[0] : 'User';
    }
  } catch (error) {
    if (typeof utils !== 'undefined') {
      utils.showToast('Failed to load user information', 'error');
    }
    if (typeof authUtils !== 'undefined') {
      authUtils.logout();
    } else {
      window.location.href = 'login.html';
    }
    return;
  }

  // Setup logout
  const logoutBtn = document.getElementById('logoutBtn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', (e) => {
      e.preventDefault();
      if (typeof authUtils !== 'undefined') {
        authUtils.logout();
      } else {
        localStorage.removeItem('token');
        window.location.href = 'login.html';
      }
    });
  }

  // Setup navigation
  document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const section = link.getAttribute('data-section');
      if (section) {
        showSection(section);
      }
    });
  });

  // Setup sidebar toggle for mobile
  const sidebarToggle = document.querySelector('.sidebar-toggle');
  const sidebar = document.querySelector('.sidebar');
  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener('click', () => {
      sidebar.classList.toggle('open');
      sidebarToggle.setAttribute('aria-expanded', sidebar.classList.contains('open'));
    });
  }

  // Setup email assistant
  setupEmailAssistant();
  
  // Load rewrite history on email section
  loadRewriteHistory();

  // Setup campaigns
  setupCampaigns();

  // Setup contacts
  setupContacts();

  // Setup settings
  setupSettings();

  // Check for plan parameter in URL
  const urlParams = new URLSearchParams(window.location.search);
  const plan = urlParams.get('plan');
  if (plan) {
    showSection('settings');
    if (typeof utils !== 'undefined') {
      utils.showToast('Please subscribe to a plan to continue', 'info', 5000);
    }
  } else {
    // Show default section
    showSection('email');
  }
});

/**
 * Show a specific section
 */
function showSection(section) {
  // Hide all sections
  document.querySelectorAll('.dashboard-section').forEach(sec => {
    sec.style.display = 'none';
  });

  // Show selected section
  const targetSection = document.getElementById(`${section}-section`);
  if (targetSection) {
    targetSection.style.display = 'block';
    currentSection = section;
  }

  // Update navigation
  document.querySelectorAll('.nav-link').forEach(link => {
    link.classList.remove('active');
    if (link.getAttribute('data-section') === section) {
      link.classList.add('active');
    }
  });

  // Update page title
  const pageTitle = document.getElementById('pageTitle');
  if (pageTitle) {
    const titles = {
      email: 'Email Assistant',
      campaigns: 'Campaigns',
      contacts: 'Contacts',
      analytics: 'Analytics',
      settings: 'Settings',
    };
    pageTitle.textContent = titles[section] || 'Dashboard';
  }

  // Load section-specific data
  if (section === 'campaigns') {
    loadCampaigns();
  } else if (section === 'contacts') {
    loadContacts();
  } else if (section === 'settings') {
    loadSettings();
  }
}

/**
 * Setup Email Assistant
 */
function setupEmailAssistant() {
  const rewriteBtn = document.getElementById('rewriteBtn');
  const emailInput = document.getElementById('emailInput');
  const toneSelect = document.getElementById('toneSelect');
  const rewrittenResult = document.getElementById('rewrittenResult');
  const rewrittenText = document.getElementById('rewrittenText');
  const copyBtn = document.getElementById('copyBtn');
  const usageStats = document.getElementById('usageStats');

  if (rewriteBtn) {
    rewriteBtn.addEventListener('click', async () => {
      const emailText = emailInput ? emailInput.value.trim() : '';
      const tone = toneSelect ? toneSelect.value : 'professional';

      if (!emailText) {
        if (typeof utils !== 'undefined') {
          utils.showToast('Please enter an email to rewrite', 'error');
        }
        return;
      }

      // Disable button and show loading
      if (typeof utils !== 'undefined') {
        utils.disableButton(rewriteBtn);
      } else {
        rewriteBtn.disabled = true;
      }

      const btnText = rewriteBtn.querySelector('.btn-text');
      const btnLoader = rewriteBtn.querySelector('.btn-loader');
      if (btnText) btnText.style.display = 'none';
      if (btnLoader) btnLoader.style.display = 'flex';

      try {
        // Use the correct API endpoint
        const response = await apiClient.rewriteEmail(emailText, tone);

        if (rewrittenText) {
          rewrittenText.textContent = response.rewritten_email || '';
        }

        if (rewrittenResult) {
          rewrittenResult.style.display = 'block';
        }

        // Load usage stats
        try {
          const usageResponse = await apiClient.getUsageStats();
          if (usageStats && usageResponse) {
            const usageText = document.getElementById('usageText');
            if (usageText) {
              // Backend returns: used, limit, remaining, plan
              usageText.textContent = `Used: ${usageResponse.used || 0} / ${usageResponse.limit || 'N/A'} rewrites today`;
            }
            usageStats.style.display = 'block';
          }
        } catch (usageError) {
          // Usage stats are optional, don't fail if they can't be loaded
          console.warn('Failed to load usage stats:', usageError);
        }

        if (typeof utils !== 'undefined') {
          utils.showToast('Email rewritten successfully!', 'success');
        }

        // Reload rewrite history
        loadRewriteHistory();

      } catch (error) {
        let errorMessage = 'Failed to rewrite email';
        if (error.message) {
          errorMessage = error.message;
        } else if (error.status === 429) {
          errorMessage = 'Rate limit exceeded. Please try again later.';
        } else if (error.status === 422) {
          errorMessage = 'Invalid input. Please check your email text and tone selection.';
        }
        
        if (typeof utils !== 'undefined') {
          utils.showToast(errorMessage, 'error');
        } else {
          alert(errorMessage);
        }
      } finally {
        if (typeof utils !== 'undefined') {
          utils.enableButton(rewriteBtn);
        } else {
          rewriteBtn.disabled = false;
        }
        if (btnText) btnText.style.display = 'inline';
        if (btnLoader) btnLoader.style.display = 'none';
      }
    });
  }

  // Copy button
  if (copyBtn) {
    copyBtn.addEventListener('click', () => {
      if (rewrittenText && rewrittenText.textContent) {
        if (typeof utils !== 'undefined') {
          utils.copyToClipboard(rewrittenText.textContent);
        } else {
          navigator.clipboard.writeText(rewrittenText.textContent).then(() => {
            alert('Copied to clipboard!');
          });
        }
      }
    });
  }
}

/**
 * Load rewrite history from API
 */
async function loadRewriteHistory() {
  const historyContainer = document.getElementById('rewriteHistory');
  if (!historyContainer) return;

  try {
    const response = await apiClient.getRewriteLogs(10, 0);
    
    if (!response.logs || response.logs.length === 0) {
      historyContainer.innerHTML = '<p style="color: #666; padding: 1rem;">No rewrite history yet.</p>';
      return;
    }

    historyContainer.innerHTML = '';
    
    response.logs.forEach(log => {
      const historyItem = document.createElement('div');
      historyItem.className = 'history-item';
      historyItem.style.cssText = 'padding: 1rem; border: 1px solid #e5e7eb; border-radius: 0.5rem; margin-bottom: 0.75rem; background: #f9fafb;';

      const headerDiv = document.createElement('div');
      headerDiv.style.cssText = 'display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem; padding-bottom: 0.5rem; border-bottom: 1px solid #e5e7eb;';
      
      const toneBadge = document.createElement('span');
      toneBadge.style.cssText = 'padding: 0.25rem 0.5rem; background: #2F6BE8; color: white; border-radius: 0.25rem; font-size: 0.75rem; text-transform: capitalize;';
      toneBadge.textContent = log.tone || 'professional';
      
      const dateSpan = document.createElement('span');
      dateSpan.style.cssText = 'color: #666; font-size: 0.85rem;';
      if (log.created_at && typeof utils !== 'undefined') {
        dateSpan.textContent = utils.formatDateTime(log.created_at);
      } else if (log.created_at) {
        dateSpan.textContent = new Date(log.created_at).toLocaleString();
      }

      headerDiv.appendChild(toneBadge);
      headerDiv.appendChild(dateSpan);

      const originalDiv = document.createElement('div');
      originalDiv.style.cssText = 'margin-bottom: 0.5rem;';
      const originalText = log.original_email || '';
      originalDiv.innerHTML = `<strong style="color: #111;">Original:</strong> <span style="color: #666;">${utils && utils.escapeHtml ? utils.escapeHtml(originalText) : originalText.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</span>`;

      const rewrittenDiv = document.createElement('div');
      const rewrittenText = log.rewritten_email || '';
      rewrittenDiv.innerHTML = `<strong style="color: #111;">Rewritten:</strong> <span style="color: #111;">${utils && utils.escapeHtml ? utils.escapeHtml(rewrittenText) : rewrittenText.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</span>`;

      historyItem.appendChild(headerDiv);
      historyItem.appendChild(originalDiv);
      historyItem.appendChild(rewrittenDiv);

      historyContainer.appendChild(historyItem);
    });

  } catch (error) {
    console.error('Failed to load rewrite history:', error);
    const errorMessage = error.status === 401 
      ? 'Please login to view rewrite history'
      : 'Failed to load rewrite history. Please try again.';
    historyContainer.innerHTML = `<p style="color: #ef4444; padding: 1rem;">${errorMessage}</p>`;
    if (typeof utils !== 'undefined' && error.status !== 401) {
      utils.showToast('Failed to load rewrite history', 'error');
    }
  }
}

/**
 * Setup Campaigns
 */
function setupCampaigns() {
  const createBtn = document.getElementById('createCampaignBtn');
  const modal = document.getElementById('createCampaignModal');
  const closeBtn = document.getElementById('closeCampaignModal');
  const cancelBtn = document.getElementById('cancelCampaignBtn');
  const campaignForm = document.getElementById('campaignForm');
  const addEmailStepBtn = document.getElementById('addEmailStepBtn');

  if (createBtn && modal) {
    createBtn.addEventListener('click', () => {
      modal.style.display = 'flex';
      resetCampaignForm();
      loadContactsForCampaign();
    });
  }

  if (closeBtn && modal) {
    closeBtn.addEventListener('click', () => {
      modal.style.display = 'none';
    });
  }

  if (cancelBtn && modal) {
    cancelBtn.addEventListener('click', () => {
      modal.style.display = 'none';
    });
  }

  if (addEmailStepBtn) {
    addEmailStepBtn.addEventListener('click', () => {
      addEmailStep();
    });
  }

  if (campaignForm) {
    campaignForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      await createCampaignFromForm();
    });
  }

  // Close modal on overlay click
  if (modal) {
    const overlay = modal.querySelector('.modal-overlay');
    if (overlay) {
      overlay.addEventListener('click', () => {
        modal.style.display = 'none';
      });
    }
  }
}

/**
 * Reset campaign form
 */
function resetCampaignForm() {
  const campaignName = document.getElementById('campaignName');
  const campaignDescription = document.getElementById('campaignDescription');
  const emailSteps = document.getElementById('emailSteps');
  
  if (campaignName) campaignName.value = '';
  if (campaignDescription) campaignDescription.value = '';
  if (emailSteps) {
    emailSteps.innerHTML = '';
    // Add first email step
    addEmailStep();
  }
}

/**
 * Add email step to campaign form
 */
function addEmailStep() {
  const emailSteps = document.getElementById('emailSteps');
  if (!emailSteps) return;

  const stepNumber = emailSteps.children.length + 1;
  
  const stepDiv = document.createElement('div');
  stepDiv.className = 'email-step';
  stepDiv.style.cssText = 'padding: 1rem; border: 1px solid #e5e7eb; border-radius: 0.5rem; margin-bottom: 1rem; background: #f9fafb;';

  stepDiv.innerHTML = `
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
      <strong>Step ${stepNumber}</strong>
      <button type="button" class="remove-step-btn" style="background: #ef4444; color: white; border: none; padding: 0.25rem 0.5rem; border-radius: 0.25rem; cursor: pointer; font-size: 0.85rem;">Remove</button>
    </div>
    <div class="form-group" style="margin-bottom: 0.75rem;">
      <label>Subject</label>
      <input type="text" class="step-subject" placeholder="Email subject" required style="width: 100%; padding: 0.5rem; border: 1px solid #ccc; border-radius: 0.375rem;">
    </div>
    <div class="form-group" style="margin-bottom: 0.75rem;">
      <label>Body Template</label>
      <textarea class="step-body" placeholder="Email body (use {{name}} for personalization)" rows="4" required style="width: 100%; padding: 0.5rem; border: 1px solid #ccc; border-radius: 0.375rem;"></textarea>
    </div>
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem;">
      <div class="form-group">
        <label>Delay Days</label>
        <input type="number" class="step-delay-days" value="0" min="0" style="width: 100%; padding: 0.5rem; border: 1px solid #ccc; border-radius: 0.375rem;">
      </div>
      <div class="form-group">
        <label>Delay Hours</label>
        <input type="number" class="step-delay-hours" value="0" min="0" max="23" style="width: 100%; padding: 0.5rem; border: 1px solid #ccc; border-radius: 0.375rem;">
      </div>
    </div>
  `;

  // Add remove button handler
  const removeBtn = stepDiv.querySelector('.remove-step-btn');
  if (removeBtn) {
    removeBtn.addEventListener('click', () => {
      stepDiv.remove();
      // Renumber steps
      renumberEmailSteps();
    });
  }

  emailSteps.appendChild(stepDiv);
}

/**
 * Renumber email steps
 */
function renumberEmailSteps() {
  const emailSteps = document.getElementById('emailSteps');
  if (!emailSteps) return;

  Array.from(emailSteps.children).forEach((step, index) => {
    const stepNumber = index + 1;
    const strong = step.querySelector('strong');
    if (strong) {
      strong.textContent = `Step ${stepNumber}`;
    }
  });
}

/**
 * Create campaign from form
 */
async function createCampaignFromForm() {
  const campaignName = document.getElementById('campaignName');
  const campaignDescription = document.getElementById('campaignDescription');
  const contactsCheckboxes = document.querySelectorAll('#contactsCheckboxes input[type="checkbox"]:checked');
  const emailSteps = document.getElementById('emailSteps');

  if (!campaignName || !campaignName.value.trim()) {
    if (typeof utils !== 'undefined') {
      utils.showToast('Campaign name is required', 'error');
    }
    return;
  }

  const selectedContactIds = Array.from(contactsCheckboxes).map(cb => parseInt(cb.value));
  if (selectedContactIds.length === 0) {
    if (typeof utils !== 'undefined') {
      utils.showToast('Please select at least one contact', 'error');
    }
    return;
  }

  const steps = Array.from(emailSteps.children).map((stepDiv, index) => {
    const subject = stepDiv.querySelector('.step-subject')?.value.trim();
    const body = stepDiv.querySelector('.step-body')?.value.trim();
    const delayDays = parseInt(stepDiv.querySelector('.step-delay-days')?.value || '0');
    const delayHours = parseInt(stepDiv.querySelector('.step-delay-hours')?.value || '0');

    if (!subject || !body) {
      throw new Error(`Step ${index + 1} is incomplete. Please fill in subject and body.`);
    }

    return {
      step_number: index + 1,
      subject: subject,
      body_template: body,
      delay_days: delayDays,
      delay_hours: delayHours,
    };
  });

  if (steps.length === 0) {
    if (typeof utils !== 'undefined') {
      utils.showToast('Please add at least one email step', 'error');
    }
    return;
  }

  const campaignData = {
    name: campaignName.value.trim(),
    description: campaignDescription?.value.trim() || null,
    contact_ids: selectedContactIds,
    email_steps: steps,
  };

  try {
    await apiClient.createCampaign(campaignData);
    if (typeof utils !== 'undefined') {
      utils.showToast('Campaign created successfully!', 'success');
    }
    
    const modal = document.getElementById('createCampaignModal');
    if (modal) modal.style.display = 'none';
    
    loadCampaigns();
  } catch (error) {
    const errorMessage = error.message || 'Failed to create campaign';
    if (typeof utils !== 'undefined') {
      utils.showToast(errorMessage, 'error');
    } else {
      alert(errorMessage);
    }
  }
}

/**
 * Load campaigns from API
 */
async function loadCampaigns() {
  const campaignsList = document.getElementById('campaignsList');
  if (!campaignsList) return;

  // Show loading state
  campaignsList.innerHTML = '<div class="empty-state"><p>Loading campaigns...</p></div>';

  try {
    const response = await apiClient.getCampaigns(100, 0);
    
    if (!response.campaigns || response.campaigns.length === 0) {
      campaignsList.innerHTML = '<div class="empty-state"><p>No campaigns yet. Create your first campaign to get started!</p></div>';
      return;
    }

    campaignsList.innerHTML = '';
    
    response.campaigns.forEach(campaign => {
      const campaignCard = document.createElement('div');
      campaignCard.className = 'campaign-card';
      campaignCard.style.cssText = 'padding: 1.5rem; border: 1px solid #e5e7eb; border-radius: 0.5rem; background: #fff; margin-bottom: 1rem;';

      const headerDiv = document.createElement('div');
      headerDiv.style.cssText = 'display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;';

      const titleDiv = document.createElement('div');
      titleDiv.style.cssText = 'flex: 1;';

      const nameDiv = document.createElement('div');
      nameDiv.style.cssText = 'font-weight: 600; font-size: 1.1rem; margin-bottom: 0.25rem; color: #111;';
      nameDiv.textContent = campaign.name || 'Unnamed Campaign';

      const statusBadge = document.createElement('span');
      const statusColors = {
        'draft': '#666',
        'active': '#10b981',
        'paused': '#f59e0b',
        'completed': '#6366f1',
      };
      statusBadge.style.cssText = `display: inline-block; padding: 0.25rem 0.75rem; background: ${statusColors[campaign.status?.toLowerCase()] || '#666'}; color: white; border-radius: 0.25rem; font-size: 0.75rem; text-transform: capitalize; margin-top: 0.5rem;`;
      statusBadge.textContent = campaign.status || 'draft';

      titleDiv.appendChild(nameDiv);
      titleDiv.appendChild(statusBadge);

      const actionsDiv = document.createElement('div');
      actionsDiv.style.cssText = 'display: flex; gap: 0.5rem;';

      if (campaign.status === 'draft') {
        const launchBtn = document.createElement('button');
        launchBtn.textContent = 'Launch';
        launchBtn.className = 'btn-primary';
        launchBtn.style.cssText = 'padding: 0.5rem 1rem; font-size: 0.9rem;';
        launchBtn.onclick = () => launchCampaign(campaign.id);
        actionsDiv.appendChild(launchBtn);
      } else if (campaign.status === 'active') {
        const pauseBtn = document.createElement('button');
        pauseBtn.textContent = 'Pause';
        pauseBtn.className = 'btn-secondary';
        pauseBtn.style.cssText = 'padding: 0.5rem 1rem; font-size: 0.9rem;';
        pauseBtn.onclick = () => pauseCampaign(campaign.id);
        actionsDiv.appendChild(pauseBtn);
      }

      const deleteBtn = document.createElement('button');
      deleteBtn.textContent = 'Delete';
      deleteBtn.style.cssText = 'padding: 0.5rem 1rem; font-size: 0.9rem; background: #ef4444; color: white; border: none; border-radius: 0.375rem; cursor: pointer;';
      deleteBtn.onclick = () => {
        if (confirm(`Are you sure you want to delete "${campaign.name}"?`)) {
          deleteCampaign(campaign.id);
        }
      };
      actionsDiv.appendChild(deleteBtn);

      headerDiv.appendChild(titleDiv);
      headerDiv.appendChild(actionsDiv);

      const descDiv = document.createElement('div');
      descDiv.style.cssText = 'color: #666; margin-bottom: 1rem;';
      descDiv.textContent = campaign.description || 'No description';

      const stepsDiv = document.createElement('div');
      stepsDiv.style.cssText = 'color: #888; font-size: 0.9rem;';
      stepsDiv.textContent = `${campaign.email_steps?.length || 0} email step(s)`;

      campaignCard.appendChild(headerDiv);
      campaignCard.appendChild(descDiv);
      campaignCard.appendChild(stepsDiv);

      campaignsList.appendChild(campaignCard);
    });

  } catch (error) {
    console.error('Failed to load campaigns:', error);
    let errorMessage = 'Failed to load campaigns. Please try again.';
    if (error.status === 401) {
      errorMessage = 'Please login to view campaigns';
    } else if (error.message) {
      errorMessage = error.message;
    }
    campaignsList.innerHTML = `<div class="empty-state"><p style="color: #ef4444;">${errorMessage}</p></div>`;
    if (typeof utils !== 'undefined' && error.status !== 401) {
      utils.showToast(errorMessage, 'error');
    }
  }
}

/**
 * Launch a campaign
 */
async function launchCampaign(campaignId) {
  try {
    await apiClient.launchCampaign(campaignId);
    if (typeof utils !== 'undefined') {
      utils.showToast('Campaign launched successfully!', 'success');
    }
    loadCampaigns();
  } catch (error) {
    const errorMessage = error.message || 'Failed to launch campaign';
    if (typeof utils !== 'undefined') {
      utils.showToast(errorMessage, 'error');
    } else {
      alert(errorMessage);
    }
  }
}

/**
 * Pause a campaign
 */
async function pauseCampaign(campaignId) {
  try {
    await apiClient.pauseCampaign(campaignId);
    if (typeof utils !== 'undefined') {
      utils.showToast('Campaign paused successfully!', 'success');
    }
    loadCampaigns();
  } catch (error) {
    const errorMessage = error.message || 'Failed to pause campaign';
    if (typeof utils !== 'undefined') {
      utils.showToast(errorMessage, 'error');
    } else {
      alert(errorMessage);
    }
  }
}

/**
 * Delete a campaign
 */
async function deleteCampaign(campaignId) {
  try {
    await apiClient.deleteCampaign(campaignId);
    if (typeof utils !== 'undefined') {
      utils.showToast('Campaign deleted successfully!', 'success');
    }
    loadCampaigns();
  } catch (error) {
    const errorMessage = error.message || 'Failed to delete campaign';
    if (typeof utils !== 'undefined') {
      utils.showToast(errorMessage, 'error');
    } else {
      alert(errorMessage);
    }
  }
}

/**
 * Setup Contacts
 */
function setupContacts() {
  const createBtn = document.getElementById('createContactBtn');
  const searchInput = document.getElementById('contactSearch');

  if (createBtn) {
    createBtn.addEventListener('click', () => {
      showCreateContactModal();
    });
  }

  if (searchInput && typeof utils !== 'undefined') {
    const debouncedSearch = utils.debounce((searchTerm) => {
      loadContacts(searchTerm);
    }, 300);

    searchInput.addEventListener('input', (e) => {
      debouncedSearch(e.target.value);
    });
  }
}

/**
 * Load contacts from API
 */
async function loadContacts(searchTerm = '') {
  const contactsList = document.getElementById('contactsList');
  if (!contactsList) return;

  // Show loading state
  contactsList.innerHTML = '<div class="empty-state"><p>Loading contacts...</p></div>';

  try {
    const response = await apiClient.getContacts(100, 0, searchTerm);
    
    if (!response.contacts || response.contacts.length === 0) {
      contactsList.innerHTML = '<div class="empty-state"><p>No contacts yet. Add your first contact to start building campaigns!</p></div>';
      return;
    }

    contactsList.innerHTML = '';
    
    response.contacts.forEach(contact => {
      const contactCard = document.createElement('div');
      contactCard.className = 'contact-card';
      contactCard.style.cssText = 'padding: 1.5rem; border: 1px solid #e5e7eb; border-radius: 0.5rem; background: #fff; transition: box-shadow 0.2s;';
      contactCard.style.cssText += 'cursor: pointer;';
      contactCard.onmouseover = () => contactCard.style.boxShadow = '0 4px 6px rgba(0,0,0,0.1)';
      contactCard.onmouseout = () => contactCard.style.boxShadow = 'none';

      const nameDiv = document.createElement('div');
      nameDiv.style.cssText = 'font-weight: 600; font-size: 1.1rem; margin-bottom: 0.5rem; color: #111;';
      nameDiv.textContent = contact.name || 'Unnamed Contact';

      const emailDiv = document.createElement('div');
      emailDiv.style.cssText = 'color: #666; margin-bottom: 0.5rem;';
      emailDiv.textContent = contact.email || '';

      const companyDiv = document.createElement('div');
      companyDiv.style.cssText = 'color: #888; font-size: 0.9rem; margin-bottom: 0.5rem;';
      if (contact.company) {
        companyDiv.textContent = contact.company;
      } else {
        companyDiv.style.display = 'none';
      }

      const actionsDiv = document.createElement('div');
      actionsDiv.style.cssText = 'display: flex; gap: 0.5rem; margin-top: 1rem; padding-top: 1rem; border-top: 1px solid #e5e7eb;';

      const editBtn = document.createElement('button');
      editBtn.textContent = 'Edit';
      editBtn.className = 'btn-secondary';
      editBtn.style.cssText = 'padding: 0.5rem 1rem; font-size: 0.9rem;';
      editBtn.onclick = (e) => {
        e.stopPropagation();
        showEditContactModal(contact);
      };

      const deleteBtn = document.createElement('button');
      deleteBtn.textContent = 'Delete';
      deleteBtn.style.cssText = 'padding: 0.5rem 1rem; font-size: 0.9rem; background: #ef4444; color: white; border: none; border-radius: 0.375rem; cursor: pointer;';
      deleteBtn.onclick = async (e) => {
        e.stopPropagation();
        if (confirm(`Are you sure you want to delete ${contact.name}?`)) {
          await deleteContact(contact.id);
        }
      };

      actionsDiv.appendChild(editBtn);
      actionsDiv.appendChild(deleteBtn);

      contactCard.appendChild(nameDiv);
      contactCard.appendChild(emailDiv);
      if (contact.company) {
        contactCard.appendChild(companyDiv);
      }
      contactCard.appendChild(actionsDiv);

      contactsList.appendChild(contactCard);
    });

  } catch (error) {
    console.error('Failed to load contacts:', error);
    let errorMessage = 'Failed to load contacts. Please try again.';
    if (error.status === 401) {
      errorMessage = 'Please login to view contacts';
    } else if (error.message) {
      errorMessage = error.message;
    }
    contactsList.innerHTML = `<div class="empty-state"><p style="color: #ef4444;">${errorMessage}</p></div>`;
    if (typeof utils !== 'undefined' && error.status !== 401) {
      utils.showToast(errorMessage, 'error');
    }
  }
}

/**
 * Show create contact modal
 */
function showCreateContactModal() {
  const name = prompt('Contact Name:');
  if (!name) return;

  const email = prompt('Email Address:');
  if (!email) return;

  const company = prompt('Company (optional):') || null;

  createContact({
    name: name.trim(),
    email: email.trim(),
    company: company ? company.trim() : null,
  });
}

/**
 * Show edit contact modal
 */
function showEditContactModal(contact) {
  const name = prompt('Contact Name:', contact.name || '');
  if (name === null) return;

  const email = prompt('Email Address:', contact.email || '');
  if (email === null) return;

  const company = prompt('Company (optional):', contact.company || '') || null;

  updateContact(contact.id, {
    name: name.trim(),
    email: email.trim(),
    company: company ? company.trim() : null,
  });
}

/**
 * Create a new contact
 */
async function createContact(contactData) {
  try {
    await apiClient.createContact(contactData);
    if (typeof utils !== 'undefined') {
      utils.showToast('Contact created successfully!', 'success');
    }
    loadContacts();
  } catch (error) {
    const errorMessage = error.message || 'Failed to create contact';
    if (typeof utils !== 'undefined') {
      utils.showToast(errorMessage, 'error');
    } else {
      alert(errorMessage);
    }
  }
}

/**
 * Update a contact
 */
async function updateContact(contactId, contactData) {
  try {
    await apiClient.updateContact(contactId, contactData);
    if (typeof utils !== 'undefined') {
      utils.showToast('Contact updated successfully!', 'success');
    }
    loadContacts();
  } catch (error) {
    const errorMessage = error.message || 'Failed to update contact';
    if (typeof utils !== 'undefined') {
      utils.showToast(errorMessage, 'error');
    } else {
      alert(errorMessage);
    }
  }
}

/**
 * Delete a contact
 */
async function deleteContact(contactId) {
  try {
    await apiClient.deleteContact(contactId);
    if (typeof utils !== 'undefined') {
      utils.showToast('Contact deleted successfully!', 'success');
    }
    loadContacts();
  } catch (error) {
    const errorMessage = error.message || 'Failed to delete contact';
    if (typeof utils !== 'undefined') {
      utils.showToast(errorMessage, 'error');
    } else {
      alert(errorMessage);
    }
  }
}

/**
 * Load contacts for campaign selection
 */
async function loadContactsForCampaign() {
  const checkboxesContainer = document.getElementById('contactsCheckboxes');
  if (!checkboxesContainer) return;

  checkboxesContainer.innerHTML = '<p style="color: #666; padding: 1rem;">Loading contacts...</p>';

  try {
    const response = await apiClient.getContacts(1000, 0);
    
    if (!response.contacts || response.contacts.length === 0) {
      checkboxesContainer.innerHTML = '<p style="color: #666; padding: 1rem;">No contacts available. Please add contacts first.</p>';
      return;
    }

    checkboxesContainer.innerHTML = '';
    
    response.contacts.forEach(contact => {
      const label = document.createElement('label');
      label.style.cssText = 'display: flex; align-items: center; gap: 0.5rem; padding: 0.5rem; cursor: pointer;';

      const checkbox = document.createElement('input');
      checkbox.type = 'checkbox';
      checkbox.value = contact.id;
      checkbox.name = 'contact_ids';
      checkbox.style.cssText = 'cursor: pointer;';

      const contactInfo = document.createElement('span');
      contactInfo.textContent = `${contact.name} (${contact.email})`;
      if (contact.company) {
        contactInfo.textContent += ` - ${contact.company}`;
      }

      label.appendChild(checkbox);
      label.appendChild(contactInfo);
      checkboxesContainer.appendChild(label);
    });

  } catch (error) {
    console.error('Failed to load contacts for campaign:', error);
    checkboxesContainer.innerHTML = '<p style="color: #ef4444; padding: 1rem;">Failed to load contacts.</p>';
  }
}

/**
 * Setup Settings
 */
function setupSettings() {
  // Settings setup logic
}

/**
 * Load settings
 */
async function loadSettings() {
  const subscriptionInfo = document.getElementById('subscriptionInfo');
  if (!subscriptionInfo) return;

  subscriptionInfo.innerHTML = '<p>Loading subscription information...</p>';

  try {
    // Try to get user info to show subscription status
    if (typeof authUtils !== 'undefined') {
      const user = await authUtils.getCurrentUser();
      if (user) {
        const plan = user.subscription_plan || 'none';
        const planDisplay = plan === 'standard' ? 'Standard ($14.99/mo)' : 
                           plan === 'pro' ? 'Pro ($49.99/mo)' : 
                           'No active subscription';
        
        subscriptionInfo.innerHTML = `
          <div style="padding: 1rem;">
            <p><strong>Current Plan:</strong> ${planDisplay}</p>
            <p style="margin-top: 0.5rem; color: #666; font-size: 0.9rem;">
              ${plan === 'none' ? 'Subscribe to a plan to unlock all features.' : 'Manage your subscription from here.'}
            </p>
          </div>
        `;
      }
    } else {
      subscriptionInfo.innerHTML = '<p>Subscription information unavailable.</p>';
    }
  } catch (error) {
    console.error('Failed to load settings:', error);
    const errorMessage = error.status === 401 
      ? 'Please login to view subscription information'
      : 'Failed to load subscription information';
    subscriptionInfo.innerHTML = `<p style="color: #ef4444;">${errorMessage}</p>`;
  }
}
