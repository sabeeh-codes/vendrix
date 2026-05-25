const API_BASE = 'http://127.0.0.1:8000/api';

const getToken = () => localStorage.getItem('access_token');

function saveTokens(access, refresh) {
  localStorage.setItem('access_token', access);
  localStorage.setItem('refresh_token', refresh);
}

function clearTokens() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('username');
  localStorage.removeItem('email');
}

function isLoggedIn() {
  return !!getToken();
}

function authHeaders() {
  return {
    'Content-Type':  'application/json',
    'Authorization': `Bearer ${getToken()}`,
  };
}

function publicHeaders() {
  return { 'Content-Type': 'application/json' };
}

async function apiFetch(url, options = {}) {
  const res = await fetch(url, options);

  let data = {};
  try { data = await res.json(); } catch {}

  if (res.status === 401) {
    clearTokens();
    window.location.href = 'auth.html';
    throw new Error('Session expired. Please login again.');
  }

  if (!res.ok) {
    const messages = [];
    for (const key in data) {
      const val = data[key];
      if (Array.isArray(val)) messages.push(...val);
      else if (typeof val === 'string') messages.push(val);
    }
    throw new Error(messages.join(' ') || data.detail || 'Something went wrong.');
  }

  return data;
}

// Auth
async function register(username, email, password, password2) {
  return apiFetch(`${API_BASE}/auth/register/`, {
    method:  'POST',
    headers: publicHeaders(),
    body:    JSON.stringify({ username, email, password, password2 }),
  });
}

async function login(email, password) {
  const data = await apiFetch(`${API_BASE}/auth/login/`, {
    method:  'POST',
    headers: publicHeaders(),
    body:    JSON.stringify({ email, password }),
  });
  saveTokens(data.access, data.refresh);
  localStorage.setItem('username', data.username || '');
  localStorage.setItem('email',    data.email    || '');
  return data;
}

function logout() {
  clearTokens();
  window.location.href = 'auth.html';
}

// Products
async function fetchProducts(params = {}) {
  const q = new URLSearchParams(params).toString();
  return apiFetch(`${API_BASE}/products/?${q}`, { headers: publicHeaders() });
}

async function fetchCategories() {
  return apiFetch(`${API_BASE}/categories/`, { headers: publicHeaders() });
}

// Cart
async function fetchCart() {
  return apiFetch(`${API_BASE}/cart/`, { headers: authHeaders() });
}

// color = color name string (example: "Blue"), backend resolves by name
async function addToCart(product_id, quantity = 1, size = null, color = null) {
  return apiFetch(`${API_BASE}/cart/add/`, {
    method:  'POST',
    headers: authHeaders(),
    body:    JSON.stringify({ product_id, quantity, size, color }),
  });
}

async function removeFromCart(product_id, size = null) {
  const url = size
    ? `${API_BASE}/cart/remove/${product_id}/?size=${encodeURIComponent(size)}`
    : `${API_BASE}/cart/remove/${product_id}/`;
  return apiFetch(url, {
    method:  'DELETE',
    headers: authHeaders(),
  });
}

async function clearCart() {
  return apiFetch(`${API_BASE}/cart/clear/`, {
    method:  'DELETE',
    headers: authHeaders(),
  });
}

// Stripe
async function createPaymentIntent() {
  return apiFetch(`${API_BASE}/orders/create-payment-intent/`, {
    method:  'POST',
    headers: authHeaders(),
  });
}

// Orders
async function placeOrder(shipping_address, payment_method = 'cod', stripe_payment_intent_id = null) {
  return apiFetch(`${API_BASE}/orders/place/`, {
    method:  'POST',
    headers: authHeaders(),
    body:    JSON.stringify({ shipping_address, payment_method, stripe_payment_intent_id }),
  });
}

async function fetchOrders() {
  return apiFetch(`${API_BASE}/orders/`, { headers: authHeaders() });
}

async function fetchOrderDetail(order_id) {
  return apiFetch(`${API_BASE}/orders/${order_id}/`, { headers: authHeaders() });
}

async function cancelOrder(order_id) {
  return apiFetch(`${API_BASE}/orders/${order_id}/cancel/`, {
    method:  'POST',
    headers: authHeaders(),
  });
}