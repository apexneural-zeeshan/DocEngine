/**
 * Login View
 */
import { login } from '../api.js';
import { navigate } from '../router.js';
import { showToast } from '../toast.js';
import { logoSvg } from '../components.js';

export function renderLoginView() {
  const app = document.getElementById('app');

  app.innerHTML = `
    <div class="login-page">
      <div class="card login-card animate-fade-in-up">
        <div class="login-header">
          <div class="login-logo">
            ${logoSvg}
            <span>DocEngine</span>
          </div>
          <p class="login-subtitle">Document Approval Workflow</p>
        </div>
        
        <form id="login-form">
          <div class="form-group">
            <label class="form-label" for="email">Email</label>
            <input 
              type="email" 
              id="email" 
              class="form-input" 
              placeholder="Enter your email"
              autocomplete="email"
              required
            />
          </div>
          
          <div class="form-group">
            <label class="form-label" for="password">Password</label>
            <input 
              type="password" 
              id="password" 
              class="form-input" 
              placeholder="Enter your password"
              autocomplete="current-password"
              required
            />
          </div>
          
          <div id="login-error" class="form-error hidden"></div>
          
          <button type="submit" id="login-btn" class="btn btn-primary btn-lg w-full mt-4">
            Sign In
          </button>
        </form>
        
        <div class="mt-6 text-center">
          <p class="text-sm text-muted">
            Need a test account? 
            <button id="create-test-user-btn" class="btn btn-ghost btn-sm">Create Test User</button>
          </p>
        </div>
      </div>
    </div>
  `;

  // Event listeners
  const form = document.getElementById('login-form');
  const errorEl = document.getElementById('login-error');
  const createTestBtn = document.getElementById('create-test-user-btn');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    const submitBtn = document.getElementById('login-btn');

    if (!email || !password) {
      errorEl.textContent = 'Please fill in all fields';
      errorEl.classList.remove('hidden');
      return;
    }

    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner"></span> Signing in...';
    errorEl.classList.add('hidden');

    try {
      await login(email, password);

      // Store user email for display
      localStorage.setItem('docengine_user', email);

      showToast('Welcome back!', 'success');
      navigate('/');
    } catch (error) {
      errorEl.textContent = error.message || 'Invalid credentials';
      errorEl.classList.remove('hidden');
      submitBtn.disabled = false;
      submitBtn.textContent = 'Sign In';
    }
  });

  createTestBtn.addEventListener('click', async () => {
    const email = 'test@docengine.com';
    const password = 'password123';

    try {
      const { createTestUser } = await import('../api.js');
      await createTestUser(email, password);

      // Auto-fill credentials
      document.getElementById('email').value = email;
      document.getElementById('password').value = password;

      showToast(`Test user created: ${email}`, 'success');
    } catch (error) {
      if (error.status === 500) {
        // User might already exist
        document.getElementById('email').value = email;
        document.getElementById('password').value = password;
        showToast('User may already exist. Try signing in.', 'warning');
      } else {
        showToast('Failed to create test user', 'error');
      }
    }
  });
}
