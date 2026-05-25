// if user already logged in, redirect to home page
if (isLoggedIn()) {
  window.location.href = 'index.html';
}

// switch between login and register tabs
function showTab(tab) {
  const isLogin = tab === 'login';

  document.getElementById('login-form').style.display    = isLogin ? 'block' : 'none';
  document.getElementById('register-form').style.display = isLogin ? 'none'  : 'block';

  document.getElementById('tab-login').classList.toggle('active', isLogin);
  document.getElementById('tab-register').classList.toggle('active', !isLogin);

  document.getElementById('alert').style.display = 'none';
}

// show message on screen
function showAlert(msg, type = 'error') {
  const el = document.getElementById('alert');
  el.className     = `alert alert-${type}`;
  el.textContent   = msg;
  el.style.display = 'block';
}

// handle login button click
async function handleLogin() {
  const email    = document.getElementById('login-email').value.trim();
  const password = document.getElementById('login-password').value;

  // check empty fields
  if (!email || !password) {
    return showAlert('Please fill in all fields.');
  }

  const btn = document.getElementById('login-btn');
  btn.textContent = 'Signing in...';
  btn.disabled    = true;

  try {
    // call login function from api.js
    await login(email, password);
    window.location.href = 'index.html';

  } catch (err) {
    showAlert(err.message);
    btn.textContent = 'Sign In';
    btn.disabled    = false;
  }
}

// handle register button click
async function handleRegister() {
  const username  = document.getElementById('reg-username').value.trim();
  const email     = document.getElementById('reg-email').value.trim();
  const password  = document.getElementById('reg-password').value;
  const password2 = document.getElementById('reg-password2').value;

  // check missing fields
  if (!username || !email || !password || !password2) {
    return showAlert('Please fill in all fields.');
  }

  // check password match
  if (password !== password2) {
    return showAlert('Passwords do not match');
  }

  const btn = document.getElementById('register-btn');
  btn.textContent = 'Creating account...';
  btn.disabled    = true;

  try {
    await register(username, email, password, password2);
    showAlert('Account created! Please sign in.', 'success');
    showTab('login');

    // auto fill email after registration
    document.getElementById('login-email').value = email;

  } catch (err) {
    showAlert(err.message);
  } finally {
    btn.textContent = 'Create Account';
    btn.disabled    = false;
  }
}

// tab click events
document.getElementById('tab-login').onclick    = () => showTab('login');
document.getElementById('tab-register').onclick = () => showTab('register');

document.getElementById('login-btn').onclick    = handleLogin;
document.getElementById('register-btn').onclick = handleRegister;

// allow enter key to submit form
document.addEventListener('keydown', e => {
  if (e.key !== 'Enter') return;
  const loginVisible = document.getElementById('login-form').style.display !== 'none';
  loginVisible ? handleLogin() : handleRegister();
});