/**
 * Dashboard View - Document List
 */
import { getLocalDocuments, listDocuments, logout } from '../api.js';
import { navigate } from '../router.js';
import { showToast } from '../toast.js';
import {
  renderHeader,
  renderDocumentCard,
  renderEmptyState,
  renderSpinner,
  escapeHtml
} from '../components.js';

export async function renderDashboardView() {
  const app = document.getElementById('app');
  const userEmail = localStorage.getItem('docengine_user') || 'User';

  // Show loading state with cached data
  let documents = getLocalDocuments();
  renderDashboard(documents, userEmail, true);

  // Fetch fresh data from backend
  try {
    documents = await listDocuments();
    renderDashboard(documents, userEmail, false);
  } catch (error) {
    console.error('Failed to fetch documents:', error);
    // Keep showing cached data, just remove loading state
    renderDashboard(documents, userEmail, false);
  }
}

function renderDashboard(documents, userEmail, isLoading) {
  const app = document.getElementById('app');

  app.innerHTML = `
    ${renderHeader(userEmail)}
    <main class="page">
      <div class="container animate-fade-in">
        <div class="page-header">
          <div>
            <h1 class="page-title">Documents</h1>
            <p class="text-secondary mt-2">Manage your document approval workflows</p>
          </div>
          <button id="create-doc-btn" class="btn btn-primary">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="12" y1="5" x2="12" y2="19"></line>
              <line x1="5" y1="12" x2="19" y2="12"></line>
            </svg>
            New Document
          </button>
        </div>
        
        ${isLoading && documents.length === 0 ? `
          <div class="flex justify-center items-center" style="min-height: 200px;">
            ${renderSpinner(true)}
          </div>
        ` : documents.length > 0 ? `
          <div class="document-grid">
            ${documents.map(doc => renderDocumentCard(doc)).join('')}
          </div>
        ` : renderEmptyState(
    'No documents yet',
    'Create your first document to get started with the approval workflow.',
    'Create Document',
    'empty-create-btn'
  )}
      </div>
    </main>
  `;

  // Event listeners
  setupEventListeners();
}

function setupEventListeners() {
  // Logout button
  const logoutBtn = document.getElementById('logout-btn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', () => {
      logout();
      showToast('Logged out successfully', 'success');
      navigate('/login');
    });
  }

  // Create document buttons
  const createBtn = document.getElementById('create-doc-btn');
  const emptyCreateBtn = document.getElementById('empty-create-btn');

  if (createBtn) {
    createBtn.addEventListener('click', () => navigate('/create'));
  }

  if (emptyCreateBtn) {
    emptyCreateBtn.addEventListener('click', () => navigate('/create'));
  }

  // Document cards - click to view details
  const documentCards = document.querySelectorAll('.document-card');
  documentCards.forEach(card => {
    card.addEventListener('click', () => {
      const docId = card.dataset.id;
      navigate(`/document/${docId}`);
    });
  });
}
