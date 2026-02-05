/**
 * DocEngine Frontend - Main Application Entry
 */
import './style.css';
import { addRoute, setBeforeEach, initRouter, navigate } from './router.js';
import { isAuthenticated } from './api.js';
import { renderLoginView } from './views/loginView.js';
import { renderDashboardView } from './views/dashboardView.js';
import { renderCreateDocView } from './views/createDocView.js';
import { renderDocumentView } from './views/documentView.js';

// Define routes
addRoute('/login', () => {
  if (isAuthenticated()) {
    navigate('/', true);
    return;
  }
  renderLoginView();
});

addRoute('/', () => {
  renderDashboardView();
});

addRoute('/create', () => {
  renderCreateDocView();
});

addRoute('/document/:id', (params) => {
  renderDocumentView(params);
});

// Navigation guard - protect routes
setBeforeEach((path) => {
  // Public routes
  if (path === '/login') {
    return true;
  }

  // Protected routes - require authentication
  if (!isAuthenticated()) {
    return '/login';
  }

  return true;
});

// Initialize the router
initRouter();

console.log('DocEngine Frontend initialized');
