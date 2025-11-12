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
  if (!authUtils.requireAuth()) {
    return;
  }

  // Load user info
  try {
    currentUser = await authUtils.getCurrentUser();
    document.getElementById('userName').textContent = currentUser.email.split('@')[0];
  } catch (error) {
    utils.showToast('Failed to load user information', 'error');
    authUtils.logout();
    return;
  }

  // Setup logout
  document.getElementById('logoutBtn').addEventListener('click', (e) => {
    e.preventDefault();
    authUtils.logout();
  });

  // Setup navigation
  document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const section = link.getAttribute('data-section');
      showSection(section);
    });
  });

  // Setup email assistant
  setupEmailAssistant();

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
    // Show settings section to subscribe to plan
    showSection('settings');
    utils.showToast('Please subscribe to a plan to continue', 'info', 5000);
  }

  // Show default section
  showSection('email');
});

/**
 * Show a specific section
 */
function showSection(section) {
  // Hide all sections
  document.querySelectorAll('.dashboard-section').forEach(sec => {
    sec.style.display = 'none';
  });

  // Update nav links
  document.querySelectorAll('.nav-link').forEach(link => {
    link.classList.remove('active');
  });

  // Show selected section
  const sectionElement = document.getElementById(section + '-section');
  if (sectionElement) {
    sectionElement.style.display = 'block';
    currentSection = section;

    // Update page title
    const titles = {
      email: 'Email Assistant',
      campaigns: 'Campaigns',
      contacts: 'Contacts',
      analytics: 'Analytics',
      settings: 'Settings'
    };
    document.getElementById('pageTitle').textContent = titles[section] || 'Dashboard';

    // Activate nav link
    document.querySelector(`[data-section="${section}"]`).classList.add('active');

    // Load section data
    loadSectionData(section);
  }
}

/**
 * Load data for a section
 */
async function loadSectionData(section) {
  switch (section) {
    case 'email':
      await loadUsageStats();
      await loadRewriteHistory();
      break;
    case 'campaigns':
      await loadCampaigns();
      break;
    case 'contacts':
      await loadContacts();
      break;
    case 'settings':
      await loadSubscriptionInfo();
      break;
  }
}

/**
 * Setup Email Assistant
 */
function setupEmailAssistant() {
  document.getElementById('rewriteBtn').addEventListener('click', async () => {
    const emailText = document.getElementById('emailInput').value.trim();
    const tone = document.getElementById('toneSelect').value;

    if (!emailText) {
      utils.showToast('Please enter an email to rewrite', 'error');
      return;
    }

    const button = document.getElementById('rewriteBtn');
    utils.disableButton(button);
    button.textContent = 'Rewriting...';

    try {
      const response = await apiClient.post('/api/rewrite', {
        email_text: emailText,
        tone: tone
      });

      // Show rewritten email
      document.getElementById('rewrittenText').textContent = response.rewritten_email;
      document.getElementById('rewrittenResult').style.display = 'block';

      // Reload usage stats and history
      await loadUsageStats();
      await loadRewriteHistory();

      utils.showToast('Email rewritten successfully!', 'success');
    } catch (error) {
      utils.showToast(error.message || 'Failed to rewrite email', 'error');
    } finally {
      utils.enableButton(button);
      button.textContent = 'Rewrite with AI';
    }
  });
}

/**
 * Load usage statistics
 */
async function loadUsageStats() {
  try {
    const usage = await apiClient.get('/api/rewrite/usage');
    document.getElementById('usageText').textContent = 
      `${usage.used} / ${usage.limit} rewrites used today (${usage.remaining} remaining) - ${usage.plan} plan`;
    document.getElementById('usageStats').style.display = 'block';
  } catch (error) {
    console.error('Failed to load usage stats:', error);
  }
}

/**
 * Load rewrite history
 */
async function loadRewriteHistory() {
  try {
    const response = await apiClient.get('/api/rewrite/logs?limit=10');
    const historyDiv = document.getElementById('rewriteHistory');
    
    if (response.logs && response.logs.length > 0) {
      historyDiv.innerHTML = '<ul style="list-style: none; padding: 0;">';
      response.logs.forEach(log => {
        const li = document.createElement('li');
        li.style.padding = '0.5rem';
        li.style.borderBottom = '1px solid #eee';
        li.innerHTML = `
          <strong>${log.tone}</strong> - ${utils.formatDateTime(log.created_at)}
          <div style="font-size: 0.9rem; color: #666; margin-top: 0.25rem;">${log.original_email.substring(0, 100)}...</div>
        `;
        historyDiv.querySelector('ul').appendChild(li);
      });
      historyDiv.innerHTML += '</ul>';
    } else {
      historyDiv.innerHTML = '<p style="color: #666;">No rewrite history yet.</p>';
    }
  } catch (error) {
    console.error('Failed to load rewrite history:', error);
  }
}

/**
 * Setup Campaigns
 */
function setupCampaigns() {
  document.getElementById('createCampaignBtn').addEventListener('click', () => {
    showCreateCampaignModal();
  });

  document.getElementById('cancelCampaignBtn').addEventListener('click', () => {
    document.getElementById('createCampaignModal').style.display = 'none';
  });

  document.getElementById('campaignForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    await createCampaign();
  });

  document.getElementById('addEmailStepBtn').addEventListener('click', () => {
    addEmailStep();
  });
}

/**
 * Load campaigns
 */
async function loadCampaigns() {
  try {
    const response = await apiClient.get('/api/campaigns?limit=50');
    campaignsList = response.campaigns || [];
    displayCampaigns(campaignsList);
  } catch (error) {
    utils.showToast('Failed to load campaigns', 'error');
    console.error(error);
  }
}

/**
 * Display campaigns
 */
function displayCampaigns(campaigns) {
  const listDiv = document.getElementById('campaignsList');
  
  if (campaigns.length === 0) {
    listDiv.innerHTML = '<p>No campaigns yet. Create your first campaign to get started!</p>';
    return;
  }

  listDiv.innerHTML = '<table class="campaigns-table"><thead><tr><th>Campaign</th><th>Status</th><th>Recipients</th><th>Actions</th></tr></thead><tbody></tbody></table>';
  const tbody = listDiv.querySelector('tbody');

  campaigns.forEach(campaign => {
    const tr = document.createElement('tr');
    const stats = campaign.stats || {};
    tr.innerHTML = `
      <td><strong>${campaign.name}</strong></td>
      <td class="status-${campaign.status.toLowerCase()}">${campaign.status}</td>
      <td>${stats.total_recipients || 0}</td>
      <td>
        <button onclick="viewCampaign(${campaign.id})" style="margin-right: 0.5rem; padding: 0.25rem 0.5rem; background: #2F6BE8; color: #fff; border: none; border-radius: 0.2rem; cursor: pointer;">View</button>
        ${campaign.status === 'DRAFT' ? `<button onclick="launchCampaign(${campaign.id})" style="margin-right: 0.5rem; padding: 0.25rem 0.5rem; background: #4caf50; color: #fff; border: none; border-radius: 0.2rem; cursor: pointer;">Launch</button>` : ''}
        ${campaign.status === 'RUNNING' ? `<button onclick="pauseCampaign(${campaign.id})" style="margin-right: 0.5rem; padding: 0.25rem 0.5rem; background: #ff9800; color: #fff; border: none; border-radius: 0.2rem; cursor: pointer;">Pause</button>` : ''}
        ${campaign.status === 'DRAFT' ? `<button onclick="deleteCampaign(${campaign.id})" style="padding: 0.25rem 0.5rem; background: #f44336; color: #fff; border: none; border-radius: 0.2rem; cursor: pointer;">Delete</button>` : ''}
      </td>
    `;
    tbody.appendChild(tr);
  });
}

/**
 * Show create campaign modal
 */
async function showCreateCampaignModal() {
  // Load contacts for selection
  await loadContactsForCampaign();
  
  // Reset form
  document.getElementById('campaignName').value = '';
  document.getElementById('campaignDescription').value = '';
  document.getElementById('emailSteps').innerHTML = '';
  addEmailStep(); // Add first step by default
  
  document.getElementById('createCampaignModal').style.display = 'block';
}

/**
 * Load contacts for campaign selection
 */
async function loadContactsForCampaign() {
  try {
    const response = await apiClient.get('/api/contacts?limit=1000');
    const checkboxesDiv = document.getElementById('contactsCheckboxes');
    checkboxesDiv.innerHTML = '';
    
    if (response.contacts && response.contacts.length > 0) {
      response.contacts.forEach(contact => {
        const label = document.createElement('label');
        label.style.display = 'block';
        label.style.padding = '0.25rem';
        label.innerHTML = `
          <input type="checkbox" name="contact" value="${contact.id}" style="margin-right: 0.5rem;">
          ${contact.name} (${contact.email})
        `;
        checkboxesDiv.appendChild(label);
      });
    } else {
      checkboxesDiv.innerHTML = '<p>No contacts available. Please add contacts first.</p>';
    }
  } catch (error) {
    console.error('Failed to load contacts:', error);
  }
}

/**
 * Add email step to campaign form
 */
function addEmailStep() {
  const stepsDiv = document.getElementById('emailSteps');
  const stepNumber = stepsDiv.children.length + 1;
  const stepDiv = document.createElement('div');
  stepDiv.style.border = '1px solid #ddd';
  stepDiv.style.padding = '1rem';
  stepDiv.style.marginBottom = '1rem';
  stepDiv.style.borderRadius = '0.3rem';
  stepDiv.innerHTML = `
    <h4>Step ${stepNumber}</h4>
    <label>Subject</label>
    <input type="text" class="step-subject" required style="width: 100%; padding: 0.5rem; margin-bottom: 0.5rem;">
    <label>Body Template</label>
    <textarea class="step-body" required style="width: 100%; padding: 0.5rem; min-height: 100px; margin-bottom: 0.5rem;"></textarea>
    <label>Delay (days)</label>
    <input type="number" class="step-delay-days" value="0" min="0" style="width: 100px; padding: 0.5rem; margin-right: 0.5rem;">
    <label>Delay (hours)</label>
    <input type="number" class="step-delay-hours" value="0" min="0" max="23" style="width: 100px; padding: 0.5rem;">
    <button type="button" onclick="this.parentElement.remove()" style="float: right; background: #f44336; color: #fff; border: none; padding: 0.25rem 0.5rem; border-radius: 0.2rem; cursor: pointer;">Remove</button>
  `;
  stepsDiv.appendChild(stepDiv);
}

/**
 * Create campaign
 */
async function createCampaign() {
  const name = document.getElementById('campaignName').value.trim();
  const description = document.getElementById('campaignDescription').value.trim();
  
  // Get selected contacts
  const selectedContacts = Array.from(document.querySelectorAll('#contactsCheckboxes input[type="checkbox"]:checked'))
    .map(cb => parseInt(cb.value));

  if (selectedContacts.length === 0) {
    utils.showToast('Please select at least one contact', 'error');
    return;
  }

  // Get email steps
  const steps = [];
  const stepDivs = document.getElementById('emailSteps').children;
  for (let i = 0; i < stepDivs.length; i++) {
    const stepDiv = stepDivs[i];
    const subject = stepDiv.querySelector('.step-subject').value.trim();
    const body = stepDiv.querySelector('.step-body').value.trim();
    const delayDays = parseInt(stepDiv.querySelector('.step-delay-days').value) || 0;
    const delayHours = parseInt(stepDiv.querySelector('.step-delay-hours').value) || 0;

    if (!subject || !body) {
      utils.showToast('Please fill in all email step fields', 'error');
      return;
    }

    steps.push({
      step_number: i + 1,
      subject: subject,
      body_template: body,
      delay_days: delayDays,
      delay_hours: delayHours
    });
  }

  if (steps.length === 0) {
    utils.showToast('Please add at least one email step', 'error');
    return;
  }

  try {
    await apiClient.post('/api/campaigns', {
      name: name,
      description: description,
      contact_ids: selectedContacts,
      email_steps: steps
    });

    utils.showToast('Campaign created successfully!', 'success');
    document.getElementById('createCampaignModal').style.display = 'none';
    await loadCampaigns();
  } catch (error) {
    utils.showToast(error.message || 'Failed to create campaign', 'error');
  }
}

/**
 * View campaign
 */
async function viewCampaign(campaignId) {
  try {
    const campaign = await apiClient.get(`/api/campaigns/${campaignId}`);
    const recipients = await apiClient.get(`/api/campaigns/${campaignId}/recipients`);
    
    // Show campaign details in a modal or alert for now
    alert(`Campaign: ${campaign.name}\nStatus: ${campaign.status}\nRecipients: ${recipients.total}`);
  } catch (error) {
    utils.showToast('Failed to load campaign details', 'error');
  }
}

/**
 * Launch campaign
 */
async function launchCampaign(campaignId) {
  if (!confirm('Are you sure you want to launch this campaign?')) {
    return;
  }

  try {
    await apiClient.post(`/api/campaigns/${campaignId}/launch`);
    utils.showToast('Campaign launched successfully!', 'success');
    await loadCampaigns();
  } catch (error) {
    utils.showToast(error.message || 'Failed to launch campaign', 'error');
  }
}

/**
 * Pause campaign
 */
async function pauseCampaign(campaignId) {
  try {
    await apiClient.post(`/api/campaigns/${campaignId}/pause`);
    utils.showToast('Campaign paused successfully!', 'success');
    await loadCampaigns();
  } catch (error) {
    utils.showToast(error.message || 'Failed to pause campaign', 'error');
  }
}

/**
 * Delete campaign
 */
async function deleteCampaign(campaignId) {
  if (!confirm('Are you sure you want to delete this campaign? This action cannot be undone.')) {
    return;
  }

  try {
    await apiClient.delete(`/api/campaigns/${campaignId}`);
    utils.showToast('Campaign deleted successfully!', 'success');
    await loadCampaigns();
  } catch (error) {
    utils.showToast(error.message || 'Failed to delete campaign', 'error');
  }
}

// Make functions available globally for onclick handlers
window.viewCampaign = viewCampaign;
window.launchCampaign = launchCampaign;
window.pauseCampaign = pauseCampaign;
window.deleteCampaign = deleteCampaign;

/**
 * Setup Contacts
 */
function setupContacts() {
  document.getElementById('createContactBtn').addEventListener('click', () => {
    showCreateContactModal();
  });

  document.getElementById('contactSearch').addEventListener('input', (e) => {
    filterContacts(e.target.value);
  });
}

/**
 * Load contacts
 */
async function loadContacts() {
  try {
    const response = await apiClient.get('/api/contacts?limit=1000');
    contactsList = response.contacts || [];
    displayContacts(contactsList);
  } catch (error) {
    utils.showToast('Failed to load contacts', 'error');
    console.error(error);
  }
}

/**
 * Display contacts
 */
function displayContacts(contacts) {
  const listDiv = document.getElementById('contactsList');
  
  if (contacts.length === 0) {
    listDiv.innerHTML = '<p>No contacts yet. Add your first contact to get started!</p>';
    return;
  }

  listDiv.innerHTML = '<table style="width: 100%; border-collapse: collapse;"><thead><tr><th>Name</th><th>Email</th><th>Company</th><th>Actions</th></tr></thead><tbody></tbody></table>';
  const tbody = listDiv.querySelector('tbody');

  contacts.forEach(contact => {
    const tr = document.createElement('tr');
    tr.style.borderBottom = '1px solid #eee';
    tr.innerHTML = `
      <td style="padding: 0.5rem;">${contact.name}</td>
      <td style="padding: 0.5rem;">${contact.email}</td>
      <td style="padding: 0.5rem;">${contact.company || '-'}</td>
      <td style="padding: 0.5rem;">
        <button onclick="editContact(${contact.id})" style="margin-right: 0.5rem; padding: 0.25rem 0.5rem; background: #2F6BE8; color: #fff; border: none; border-radius: 0.2rem; cursor: pointer;">Edit</button>
        <button onclick="deleteContact(${contact.id})" style="padding: 0.25rem 0.5rem; background: #f44336; color: #fff; border: none; border-radius: 0.2rem; cursor: pointer;">Delete</button>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

/**
 * Filter contacts
 */
function filterContacts(searchTerm) {
  const filtered = contactsList.filter(contact => {
    const term = searchTerm.toLowerCase();
    return contact.name.toLowerCase().includes(term) ||
           contact.email.toLowerCase().includes(term) ||
           (contact.company && contact.company.toLowerCase().includes(term));
  });
  displayContacts(filtered);
}

/**
 * Show create contact modal
 */
function showCreateContactModal() {
  const name = prompt('Contact Name:');
  if (!name) return;

  const email = prompt('Contact Email:');
  if (!email || !utils.validateEmail(email)) {
    utils.showToast('Please enter a valid email address', 'error');
    return;
  }

  const company = prompt('Company (optional):') || '';

  createContact({ name, email, company });
}

/**
 * Create contact
 */
async function createContact(contactData) {
  try {
    await apiClient.post('/api/contacts', contactData);
    utils.showToast('Contact created successfully!', 'success');
    await loadContacts();
  } catch (error) {
    utils.showToast(error.message || 'Failed to create contact', 'error');
  }
}

/**
 * Edit contact
 */
async function editContact(contactId) {
  try {
    const contact = await apiClient.get(`/api/contacts/${contactId}`);
    const name = prompt('Contact Name:', contact.name);
    if (!name) return;

    const email = prompt('Contact Email:', contact.email);
    if (!email || !utils.validateEmail(email)) {
      utils.showToast('Please enter a valid email address', 'error');
      return;
    }

    const company = prompt('Company:', contact.company || '') || null;

    await apiClient.put(`/api/contacts/${contactId}`, { name, email, company });
    utils.showToast('Contact updated successfully!', 'success');
    await loadContacts();
  } catch (error) {
    utils.showToast(error.message || 'Failed to update contact', 'error');
  }
}

/**
 * Delete contact
 */
async function deleteContact(contactId) {
  if (!confirm('Are you sure you want to delete this contact?')) {
    return;
  }

  try {
    await apiClient.delete(`/api/contacts/${contactId}`);
    utils.showToast('Contact deleted successfully!', 'success');
    await loadContacts();
  } catch (error) {
    utils.showToast(error.message || 'Failed to delete contact', 'error');
  }
}

// Make functions available globally
window.editContact = editContact;
window.deleteContact = deleteContact;

/**
 * Setup Settings
 */
function setupSettings() {
  // Settings functionality is handled in loadSubscriptionInfo
}

/**
 * Load subscription information
 */
async function loadSubscriptionInfo() {
  try {
    const status = await apiClient.get('/billing/status');
    const infoDiv = document.getElementById('subscriptionInfo');
    
    const planName = status.plan === 'pro' ? 'Pro ($49.99/mo)' : 'Standard ($14.99/mo)';
    infoDiv.innerHTML = `
      <p><strong>Current Plan:</strong> ${planName}</p>
      <p><strong>Status:</strong> ${status.status}</p>
      ${status.subscription_id ? `<p><strong>Subscription ID:</strong> ${status.subscription_id}</p>` : ''}
      <div style="margin-top: 1rem;">
        <button onclick="subscribeToPlan('standard')" style="margin-right: 0.5rem; padding: 0.5rem 1rem; background: #2F6BE8; color: #fff; border: none; border-radius: 0.3rem; cursor: pointer;">Subscribe to Standard</button>
        <button onclick="subscribeToPlan('pro')" style="padding: 0.5rem 1rem; background: #2F6BE8; color: #fff; border: none; border-radius: 0.3rem; cursor: pointer;">Subscribe to Pro</button>
      </div>
      ${status.subscription_id ? `<button onclick="cancelSubscription()" style="margin-top: 0.5rem; padding: 0.5rem 1rem; background: #f44336; color: #fff; border: none; border-radius: 0.3rem; cursor: pointer;">Cancel Subscription</button>` : ''}
    `;
  } catch (error) {
    const infoDiv = document.getElementById('subscriptionInfo');
    if (error.message.includes('503')) {
      infoDiv.innerHTML = '<p>Billing is currently disabled. Please contact support for subscription management.</p>';
    } else {
      infoDiv.innerHTML = `<p>Error loading subscription information: ${error.message}</p>`;
    }
  }
}

/**
 * Subscribe to plan
 */
async function subscribeToPlan(plan) {
  if (!confirm(`Subscribe to ${plan} plan?`)) {
    return;
  }

  try {
    await apiClient.post('/billing/subscribe', { plan: plan });
    utils.showToast(`Successfully subscribed to ${plan} plan!`, 'success');
    await loadSubscriptionInfo();
  } catch (error) {
    utils.showToast(error.message || 'Failed to subscribe', 'error');
  }
}

/**
 * Cancel subscription
 */
async function cancelSubscription() {
  if (!confirm('Are you sure you want to cancel your subscription? You will retain access until the end of the billing period.')) {
    return;
  }

  try {
    await apiClient.post('/billing/cancel');
    utils.showToast('Subscription cancelled successfully', 'success');
    await loadSubscriptionInfo();
  } catch (error) {
    utils.showToast(error.message || 'Failed to cancel subscription', 'error');
  }
}

// Make functions available globally
window.subscribeToPlan = subscribeToPlan;
window.cancelSubscription = cancelSubscription;

