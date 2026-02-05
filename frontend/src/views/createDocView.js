/**
 * Create Document View
 */
import { createDocument, logout } from '../api.js';
import { navigate } from '../router.js';
import { showToast } from '../toast.js';
import { renderHeader } from '../components.js';

export function renderCreateDocView() {
  const app = document.getElementById('app');
  const userEmail = localStorage.getItem('docengine_user') || 'User';

  app.innerHTML = `
    ${renderHeader(userEmail)}
    <main class="page">
      <div class="container animate-fade-in" style="max-width: 600px;">
        <div class="mb-6">
          <button id="back-btn" class="btn btn-ghost">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="19" y1="12" x2="5" y2="12"></line>
              <polyline points="12 19 5 12 12 5"></polyline>
            </svg>
            Back to Documents
          </button>
        </div>
        
        <div class="card">
          <h2 class="mb-6">Create New Document</h2>
          
          <form id="create-form">
            <div class="form-group">
              <label class="form-label" for="title">Document Title</label>
              <input 
                type="text" 
                id="title" 
                class="form-input" 
                placeholder="Enter document title"
                maxlength="255"
                required
              />
              <p class="form-hint">Give your document a descriptive title</p>
            </div>
            
            <div id="create-error" class="form-error hidden"></div>
            
            <div class="flex gap-4 mt-6">
              <button type="submit" id="submit-btn" class="btn btn-primary">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                  <polyline points="14 2 14 8 20 8"></polyline>
                  <line x1="12" y1="18" x2="12" y2="12"></line>
                  <line x1="9" y1="15" x2="15" y2="15"></line>
                </svg>
                Create Document
              </button>
              <button type="button" id="cancel-btn" class="btn btn-outline">
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    </main>
  `;

  // Event listeners
  const form = document.getElementById('create-form');
  const backBtn = document.getElementById('back-btn');
  const cancelBtn = document.getElementById('cancel-btn');
  const logoutBtn = document.getElementById('logout-btn');
  const errorEl = document.getElementById('create-error');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const title = document.getElementById('title').value.trim();
    const submitBtn = document.getElementById('submit-btn');

    if (!title) {
      errorEl.textContent = 'Please enter a document title';
      errorEl.classList.remove('hidden');
      return;
    }

    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner"></span> Creating...';
    errorEl.classList.add('hidden');

    try {
      const doc = await createDocument(title);
      showToast('Document created successfully!', 'success');
      navigate(`/document/${doc.id}`);
    } catch (error) {
      errorEl.textContent = error.message || 'Failed to create document';
      errorEl.classList.remove('hidden');
      submitBtn.disabled = false;
      submitBtn.innerHTML = `
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
          <polyline points="14 2 14 8 20 8"></polyline>
          <line x1="12" y1="18" x2="12" y2="12"></line>
          <line x1="9" y1="15" x2="15" y2="15"></line>
        </svg>
        Create Document
      `;
    }
  });

  backBtn.addEventListener('click', () => navigate('/'));
  cancelBtn.addEventListener('click', () => navigate('/'));

  if (logoutBtn) {
    logoutBtn.addEventListener('click', () => {
      logout();
      showToast('Logged out successfully', 'success');
      navigate('/login');
    });
  }
}
