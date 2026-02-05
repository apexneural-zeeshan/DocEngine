/**
 * Document Detail View with Approval Workflow
 */
import { getDocument, getLocalDocuments, updateLocalDocument, logout } from '../api.js';
import { navigate } from '../router.js';
import { showToast } from '../toast.js';
import {
  renderHeader,
  renderStatusBadge,
  renderSpinner,
  escapeHtml
} from '../components.js';

export async function renderDocumentView(params) {
  const app = document.getElementById('app');
  const userEmail = localStorage.getItem('docengine_user') || 'User';
  const documentId = params.id;

  // Show loading first
  app.innerHTML = `
    ${renderHeader(userEmail)}
    <main class="page">
      <div class="container">
        <div class="flex justify-center items-center" style="min-height: 300px;">
          ${renderSpinner(true)}
        </div>
      </div>
    </main>
  `;

  setupLogout();

  // Try to get from local storage first
  let document = getLocalDocuments().find(d => d.id === documentId);

  // Try to fetch from API if not found locally
  if (!document) {
    try {
      document = await getDocument(documentId);
      if (document) {
        updateLocalDocument(document);
      }
    } catch (error) {
      console.error('Failed to fetch document:', error);
    }
  }

  if (!document) {
    renderNotFound();
    return;
  }

  renderDocumentDetails(document);
}

function renderNotFound() {
  const app = document.getElementById('app');
  const userEmail = localStorage.getItem('docengine_user') || 'User';

  app.innerHTML = `
    ${renderHeader(userEmail)}
    <main class="page">
      <div class="container animate-fade-in" style="text-align: center; padding: 4rem 1rem;">
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="margin: 0 auto 1rem; color: var(--color-text-muted);">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="12" y1="8" x2="12" y2="12"></line>
          <line x1="12" y1="16" x2="12.01" y2="16"></line>
        </svg>
        <h2 class="mb-2">Document Not Found</h2>
        <p class="text-muted mb-6">The document you're looking for doesn't exist or has been removed.</p>
        <button id="go-home-btn" class="btn btn-primary">Go to Dashboard</button>
      </div>
    </main>
  `;

  setupLogout();
  document.getElementById('go-home-btn')?.addEventListener('click', () => navigate('/'));
}

function renderDocumentDetails(doc) {
  const app = document.getElementById('app');
  const userEmail = localStorage.getItem('docengine_user') || 'User';

  const createdDate = new Date(doc.created_at).toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });

  app.innerHTML = `
    ${renderHeader(userEmail)}
    <main class="page">
      <div class="container animate-fade-in" style="max-width: 800px;">
        <div class="mb-6">
          <button id="back-btn" class="btn btn-ghost">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="19" y1="12" x2="5" y2="12"></line>
              <polyline points="12 19 5 12 12 5"></polyline>
            </svg>
            Back to Documents
          </button>
        </div>
        
        <div class="card mb-6">
          <div class="flex justify-between items-start mb-4">
            <div>
              <h1 class="page-title mb-2">${escapeHtml(doc.title)}</h1>
              <p class="text-secondary">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="display: inline; vertical-align: -2px;">
                  <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                  <line x1="16" y1="2" x2="16" y2="6"></line>
                  <line x1="8" y1="2" x2="8" y2="6"></line>
                  <line x1="3" y1="10" x2="21" y2="10"></line>
                </svg>
                ${createdDate}
              </p>
            </div>
            ${renderStatusBadge(doc.status)}
          </div>
          
          <div class="flex gap-2">
            <span class="text-sm text-muted">Document ID:</span>
            <code class="text-sm" style="font-family: monospace; color: var(--color-text-secondary);">${doc.id}</code>
          </div>
        </div>
        
        <div class="card">
          <h3 class="mb-4">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="display: inline; vertical-align: -4px; margin-right: 8px;">
              <polyline points="9 11 12 14 22 4"></polyline>
              <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path>
            </svg>
            Approval Workflow
          </h3>
          
          ${renderWorkflowStatus(doc.status)}
        </div>
      </div>
    </main>
  `;

  setupLogout();
  document.getElementById('back-btn')?.addEventListener('click', () => navigate('/'));
}

function renderWorkflowStatus(status) {
  const statusInfo = {
    PENDING: {
      icon: '<svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>',
      title: 'Awaiting Approval',
      description: 'This document is currently pending review. Approval steps will appear here once they are assigned.',
      color: 'var(--color-warning)'
    },
    APPROVED: {
      icon: '<svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>',
      title: 'Approved',
      description: 'This document has been approved by all required approvers.',
      color: 'var(--color-success)'
    },
    REJECTED: {
      icon: '<svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>',
      title: 'Rejected',
      description: 'This document has been rejected during the approval process.',
      color: 'var(--color-danger)'
    }
  };

  const info = statusInfo[status] || statusInfo.PENDING;

  return `
    <div class="text-center" style="padding: 2rem 1rem;">
      <div style="color: ${info.color}; margin-bottom: 1rem;">
        ${info.icon}
      </div>
      <h4 class="mb-2">${info.title}</h4>
      <p class="text-muted">${info.description}</p>
    </div>
  `;
}

function setupLogout() {
  const logoutBtn = document.getElementById('logout-btn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', () => {
      logout();
      showToast('Logged out successfully', 'success');
      navigate('/login');
    });
  }
}
