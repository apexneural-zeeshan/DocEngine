/**
 * Simple Hash-based Router for SPA
 */

const routes = new Map();
let currentRoute = null;
let beforeEachGuard = null;

/**
 * Register a route
 */
export function addRoute(path, handler) {
    routes.set(path, handler);
}

/**
 * Set a navigation guard
 */
export function setBeforeEach(guard) {
    beforeEachGuard = guard;
}

/**
 * Navigate to a route
 */
export function navigate(path, replace = false) {
    if (replace) {
        window.location.replace(`#${path}`);
    } else {
        window.location.hash = path;
    }
}

/**
 * Get current route path
 */
export function getCurrentPath() {
    return window.location.hash.slice(1) || '/';
}

/**
 * Parse route and extract params
 */
function matchRoute(path) {
    // Check for exact match first
    if (routes.has(path)) {
        return { handler: routes.get(path), params: {} };
    }

    // Check for parameterized routes
    for (const [routePath, handler] of routes) {
        const routeParts = routePath.split('/');
        const pathParts = path.split('/');

        if (routeParts.length !== pathParts.length) continue;

        const params = {};
        let match = true;

        for (let i = 0; i < routeParts.length; i++) {
            if (routeParts[i].startsWith(':')) {
                params[routeParts[i].slice(1)] = pathParts[i];
            } else if (routeParts[i] !== pathParts[i]) {
                match = false;
                break;
            }
        }

        if (match) {
            return { handler, params };
        }
    }

    return null;
}

/**
 * Handle route change
 */
async function handleRouteChange() {
    const path = getCurrentPath();

    // Run guard
    if (beforeEachGuard) {
        const result = await beforeEachGuard(path);
        if (result === false) return;
        if (typeof result === 'string' && result !== path) {
            navigate(result, true);
            return;
        }
    }

    const matched = matchRoute(path);

    if (matched) {
        currentRoute = path;
        await matched.handler(matched.params);
    } else {
        // 404 - redirect to home
        navigate('/', true);
    }
}

/**
 * Initialize router
 */
export function initRouter() {
    window.addEventListener('hashchange', handleRouteChange);

    // Handle initial route
    if (!window.location.hash) {
        window.location.hash = '/';
    } else {
        handleRouteChange();
    }
}
