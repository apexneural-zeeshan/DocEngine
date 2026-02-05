/**
 * UI Components - Reusable HTML templates
 */

/**
 * Document icon SVG
 */
export const documentIcon = `
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
    <polyline points="14 2 14 8 20 8"></polyline>
    <line x1="16" y1="13" x2="8" y2="13"></line>
    <line x1="16" y1="17" x2="8" y2="17"></line>
    <polyline points="10 9 9 9 8 9"></polyline>
  </svg>
`;

/**
 * Logo SVG
 */
export const logoSvg = `
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
    <path d="M14 2v6h6"></path>
    <path d="M9 15l2 2 4-4"></path>
  </svg>
`;

/**
 * Render page header with navigation
 */
export function renderHeader(userEmail = null) {
    return `
    <header class="header">
      <div class="container header-content">
        <a href="#/" class="header-logo">
          ${logoSvg}
          <span>DocEngine</span>
        </a>
        ${userEmail ? `
          <nav class="header-nav">
            <span class="header-user">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                <circle cx="12" cy="7" r="4"></circle>
              </svg>
              ${escapeHtml(userEmail)}
            </span>
            <button id="logout-btn" class="btn btn-ghost btn-sm">Logout</button>
          </nav>
        ` : ''}
      </div>
    </header>
  `;
}

/**
 * Render status badge
 */
export function renderStatusBadge(status) {
    const statusLower = status.toLowerCase();
    const icon = getStatusIcon(statusLower);

    return `
    <span class="badge badge-${statusLower}">
      ${icon}
      ${status}
    </span>
  `;
}

function getStatusIcon(status) {
    switch (status) {
        case 'pending':
            return '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>';
        case 'approved':
            return '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>';
        case 'rejected':
            return '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>';
        default:
            return '';
    }
}

/**
 * Render document card
 */
export function renderDocumentCard(document) {
    const date = new Date(document.created_at).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
    });

    return `
    <div class="card card-clickable document-card" data-id="${document.id}">
      <div class="card-header">
        <h3 class="card-title">${escapeHtml(document.title)}</h3>
        ${renderStatusBadge(document.status)}
      </div>
      <div class="card-meta">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
          <line x1="16" y1="2" x2="16" y2="6"></line>
          <line x1="8" y1="2" x2="8" y2="6"></line>
          <line x1="3" y1="10" x2="21" y2="10"></line>
        </svg>
        Created ${date}
      </div>
    </div>
  `;
}

/**
 * Render empty state
 */
export function renderEmptyState(title, description, actionText = null, actionId = null) {
    return `
    <div class="empty-state animate-fade-in">
      <svg class="empty-state-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <path d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
      </svg>
      <h3 class="empty-state-title">${escapeHtml(title)}</h3>
      <p class="empty-state-description">${escapeHtml(description)}</p>
      ${actionText ? `<button id="${actionId}" class="btn btn-primary">${escapeHtml(actionText)}</button>` : ''}
    </div>
  `;
}

/**
 * Render loading spinner
 */
export function renderSpinner(large = false) {
    return `<div class="spinner ${large ? 'spinner-lg' : ''}"></div>`;
}

/**
 * Render loading overlay
 */
export function renderLoadingOverlay() {
    return `
    <div class="loading-overlay">
      ${renderSpinner(true)}
    </div>
  `;
}

/**
 * Escape HTML to prevent XSS
 */
export function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
