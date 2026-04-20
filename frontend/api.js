const API_BASE = 'http://127.0.0.1:8000/api';

// getting token from local storage (if user logged in)
const getToken = () => localStorage.getItem('access_token');

// save both tokens after login
function saveTokens(access, refresh) {
  localStorage.setItem('access_token', access);
  localStorage.setItem('refresh_token', refresh);
}

// remove everything related to user session
function clearTokens() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('username');
  localStorage.removeItem('email');
}

// just checks if token exists or not
function isLoggedIn() {
  return !!getToken();
}

// adding auth headers if token is there
const authHeaders = () => {
  const token = getToken();
  return {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` })
  };
};

// headers for public requests (no auth needed)
const publicHeaders = () => ({
  'Content-Type': 'application/json'
});

// common fetch function to avoid repeating code
async function apiFetch(url, options = {}) {
  const res = await fetch(url, options);

  let data = {};
  try {
    data = await res.json(); // try to convert response to json
  } catch {}

  // if unauthorized, clear data and send user to login page
  if (res.status === 401) {
    clearTokens();
    window.location.href = 'auth.html';
    throw new Error('Session expired. Please login again.');
  }

  // if request failed, show error message
  if (!res.ok) {
    throw new Error(
      Object.values(data).flat().join(' ') ||
      data.detail ||
      'Request failed'
    );
  }

  return data;
}

// register new user
async function register(username, email, password, password2) {
  return apiFetch(`${API_BASE}/auth/register/`, {
    method: 'POST',
    headers: publicHeaders(),
    body: JSON.stringify({ username, email, password, password2 })
  });
}

// login user with email + password
async function login(email, password) {
  const data = await apiFetch(`${API_BASE}/auth/login/`, {
    method: 'POST',
    headers: publicHeaders(),
    body: JSON.stringify({ email, password })   // sending email here, not username
  });

  saveTokens(data.access, data.refresh);

  // storing username and email from backend response
  localStorage.setItem('username', data.username);
  localStorage.setItem('email',    data.email);

  return data;
}

// logout user and clear session
function logout() {
  clearTokens();
  window.location.href = 'auth.html';
}

// get all products (can pass filters in params)
async function fetchProducts(params = {}) {
  const query = new URLSearchParams(params).toString();
  return apiFetch(`${API_BASE}/products/?${query}`, {
    headers: publicHeaders()
  });
}

// get product categories list
async function fetchCategories() {
  return apiFetch(`${API_BASE}/categories/`, {
    headers: publicHeaders()
  });
}

// get current user's cart
async function fetchCart() {
  return apiFetch(`${API_BASE}/cart/`, {
    headers: authHeaders()
  });
}

// add product to cart with optional size
async function addToCart(product_id, quantity = 1, size = null) {
  return apiFetch(`${API_BASE}/cart/add/`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify({ product_id, quantity, size })
  });
}

// remove product from cart (size optional)
async function removeFromCart(product_id, size = null) {
  const url = size
    ? `${API_BASE}/cart/remove/${product_id}/?size=${size}`
    : `${API_BASE}/cart/remove/${product_id}/`;

  return apiFetch(url, {
    method: 'DELETE',
    headers: authHeaders()
  });
}

// clear whole cart
async function clearCart() {
  return apiFetch(`${API_BASE}/cart/clear/`, {
    method: 'DELETE',
    headers: authHeaders()
  });
}

// place order with shipping address
async function placeOrder(shipping_address) {
  return apiFetch(`${API_BASE}/orders/place/`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify({ shipping_address })
  });
}

// get all orders of logged in user
async function fetchOrders() {
  return apiFetch(`${API_BASE}/orders/`, {
    headers: authHeaders()
  });
}