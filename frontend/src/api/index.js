const ACCESS_KEY = 'aicv.access_token';
const REFRESH_KEY = 'aicv.refresh_token';

export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

export const tokens = {
  get access() {
    return localStorage.getItem(ACCESS_KEY);
  },
  get refresh() {
    return localStorage.getItem(REFRESH_KEY);
  },
  set({ access, refresh }) {
    localStorage.setItem(ACCESS_KEY, access);
    localStorage.setItem(REFRESH_KEY, refresh);
  },
  clear() {
    localStorage.removeItem(ACCESS_KEY);
    localStorage.removeItem(REFRESH_KEY);
  },
};

let authExpiredHandler = null;
export function setAuthExpiredHandler(fn) {
  authExpiredHandler = fn;
}

async function toApiError(response) {
  const type = response.headers.get('content-type') || '';
  if (type.includes('json')) {
    const data = await response.json().catch(() => ({}));
    return new ApiError(data.detail || `Server error (${response.status})`, response.status);
  }
  return new ApiError(`Server error (${response.status})`, response.status);
}

export async function tryRefresh() {
  const refresh = tokens.refresh;
  if (!refresh) return false;
  try {
    const response = await authFetch('/api/v1/auth/refresh', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refresh }),
    }, { allowRefresh: false });
    if (!response.ok) return false;
    const data = await response.json();
    tokens.set({ access: data.access_token, refresh: data.refresh_token });
    return true;
  } catch {
    return false;
  }
}

async function authFetch(path, options = {}, { allowRefresh = true } = {}) {
  const headers = new Headers(options.headers || {});
  if (tokens.access && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${tokens.access}`);
  }
  const response = await fetch(path, { ...options, headers });

  if (response.status !== 401 || !allowRefresh) return response;

  const recovered = await tryRefresh();
  if (recovered) {
    const retryHeaders = new Headers(options.headers || {});
    retryHeaders.set('Authorization', `Bearer ${tokens.access}`);
    return authFetch(path, { ...options, headers: retryHeaders }, { allowRefresh: false });
  }

  tokens.clear();
  if (authExpiredHandler) authExpiredHandler();
  return response;
}

export async function login(email, password) {
  const response = await authFetch('/api/v1/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  }, { allowRefresh: false });
  if (!response.ok) throw await toApiError(response);
  return response.json();
}

export async function register(email, password, fullName) {
  const response = await authFetch('/api/v1/auth/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password, full_name: fullName || undefined }),
  }, { allowRefresh: false });
  if (!response.ok) throw await toApiError(response);
  return response.json();
}

export async function getMe() {
  const response = await authFetch('/api/v1/auth/me');
  if (!response.ok) throw await toApiError(response);
  return response.json();
}

export async function apiGet(path) {
  const response = await authFetch(path);
  if (!response.ok) throw await toApiError(response);
  return response.json();
}

export async function apiPostForm(path, formData) {
  const response = await authFetch(path, { method: 'POST', body: formData });
  if (!response.ok) throw await toApiError(response);
  return response.json();
}

export async function apiPostJson(path, data) {
  const response = await authFetch(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data ?? {}),
  });
  if (!response.ok) throw await toApiError(response);
  return response.json();
}
