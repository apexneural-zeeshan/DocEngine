/**
 * API Service Layer
 * Handles all communication with the DocEngine backend
 */

const API_BASE = '/api';

/**
 * Get stored JWT token
 */
function getToken() {
    return localStorage.getItem('docengine_token');
}

/**
 * Make an authenticated API request
 */
async function apiRequest(endpoint, options = {}) {
    const token = getToken();

    const headers = {
        'Content-Type': 'application/json',
        ...options.headers,
    };

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers,
    });

    // Handle non-JSON responses
    const contentType = response.headers.get('content-type');
    let data = null;

    if (contentType && contentType.includes('application/json')) {
        data = await response.json();
    }

    if (!response.ok) {
        const error = new Error(data?.detail || 'An error occurred');
        error.status = response.status;
        error.data = data;
        throw error;
    }

    return data;
}

/**
 * Authentication API
 */
export async function login(email, password) {
    const data = await apiRequest('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
    });

    // Store token
    localStorage.setItem('docengine_token', data.access_token);

    return data;
}

export function logout() {
    localStorage.removeItem('docengine_token');
    localStorage.removeItem('docengine_user');
    localStorage.removeItem('docengine_documents');
}

export function isAuthenticated() {
    return !!getToken();
}

/**
 * Documents API
 */
export async function createDocument(title) {
    const document = await apiRequest('/documents', {
        method: 'POST',
        body: JSON.stringify({ title }),
    });

    // Store in local documents list
    saveDocumentLocally(document);

    return document;
}

export async function getDocument(documentId) {
    return apiRequest(`/documents/${documentId}`);
}

export async function listDocuments() {
    const documents = await apiRequest('/documents');
    // Cache documents locally
    localStorage.setItem('docengine_documents', JSON.stringify(documents));
    return documents;
}

export function getLocalDocuments() {
    const stored = localStorage.getItem('docengine_documents');
    return stored ? JSON.parse(stored) : [];
}

function saveDocumentLocally(document) {
    const documents = getLocalDocuments();
    const existingIndex = documents.findIndex(d => d.id === document.id);

    if (existingIndex >= 0) {
        documents[existingIndex] = document;
    } else {
        documents.unshift(document);
    }

    localStorage.setItem('docengine_documents', JSON.stringify(documents));
}

export function updateLocalDocument(document) {
    saveDocumentLocally(document);
}

/**
 * Approvals API
 */
export async function approveStep(documentId, stepId, approverId) {
    const result = await apiRequest(`/documents/${documentId}/steps/${stepId}/approve`, {
        method: 'POST',
        body: JSON.stringify({ approver_id: approverId }),
    });

    // Update local document
    if (result.document) {
        saveDocumentLocally(result.document);
    }

    return result;
}

export async function rejectStep(documentId, stepId, approverId) {
    const result = await apiRequest(`/documents/${documentId}/steps/${stepId}/reject`, {
        method: 'POST',
        body: JSON.stringify({ approver_id: approverId }),
    });

    // Update local document
    if (result.document) {
        saveDocumentLocally(result.document);
    }

    return result;
}

/**
 * Dev API (for testing)
 */
export async function createTestUser(email, password) {
    return apiRequest(`/dev/create-user?email=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`, {
        method: 'POST',
    });
}

/**
 * Health check
 */
export async function healthCheck() {
    return apiRequest('/health');
}
