document.addEventListener('DOMContentLoaded', function () {

  // check if user logged in, otherwise send to login page
  if (!isLoggedIn()) {
    window.location.href = 'auth.html';
    return;
  }

  // setup navbar username + avatar
  const u = localStorage.getItem('username') || '';
  const navUsername = document.getElementById('nav-username');
  const navAvatar   = document.getElementById('nav-avatar');
  if (navUsername) navUsername.textContent = u;
  if (navAvatar)   navAvatar.textContent   = u.charAt(0).toUpperCase();

  // show alert message (auto hide after few seconds)
  function showAlert(msg, type = 'success') {
    const el = document.getElementById('alert');
    el.className     = `alert alert-${type}`;
    el.textContent   = msg;
    el.style.display = 'block';
    setTimeout(() => el.style.display = 'none', 3000);
  }

  // helper to show image or fallback placeholder
  function imgOrPlaceholder(src, name) {
    if (src) {
      return `<img src="http://127.0.0.1:8000${src}" alt="${name}"
               onerror="this.parentElement.innerHTML='<div class=img-placeholder><img src=assets/icons/hanger.svg alt=></div>'">`;
    }
    return `<div class="img-placeholder">
              <img src="assets/icons/hanger.svg" alt="">
            </div>`;
  }

  // build single cart item row html
  function cartItemRow(item) {
    const name  = item.product_detail?.name  ?? `Product #${item.product}`;
    const img   = item.product_detail?.image ?? null;
    const price = parseFloat(item.subtotal).toFixed(2);
    const pid   = item.product_detail?.id    ?? item.product;
    const size  = item.size || '';   // getting size if exists

    return `
      <div class="cart-item">
        <div class="cart-item-image">
          ${imgOrPlaceholder(img, name)}
        </div>
        <div class="cart-item-info">
          <h4>${name}</h4>
          <div class="item-meta">
            Qty: ${item.quantity}${size ? ` &middot; Size: ${size}` : ''}
          </div>
        </div>
        <div class="cart-item-price">$${price}</div>
        <button class="cart-remove-btn"
                data-pid="${pid}"
                data-size="${size}"
                title="Remove">✕</button>
      </div>`;
  }

  // open checkout modal
  function openModal() {
    document.getElementById('checkout-modal').classList.add('open');
  }

  // close modal and reset fields
  function closeModal() {
    document.getElementById('checkout-modal').classList.remove('open');
    document.getElementById('modal-alert').style.display = 'none';
    document.getElementById('shipping-address').value = '';
  }

  // confirm order and send to backend
  async function confirmOrder() {
    const address = document.getElementById('shipping-address').value.trim();
    const alertEl = document.getElementById('modal-alert');

    // check if address is empty
    if (!address) {
      alertEl.className     = 'alert alert-error';
      alertEl.textContent   = 'Please enter a shipping address.';
      alertEl.style.display = 'block';
      return;
    }

    try {
      const order = await placeOrder(address);
      closeModal();
      showAlert(`Order #${order.id} placed successfully!`);
      setTimeout(() => window.location.href = 'orders.html', 1800);
    } catch (err) {
      alertEl.className     = 'alert alert-error';
      alertEl.textContent   = err.message;
      alertEl.style.display = 'block';
    }
  }

  // remove single item from cart
  async function handleRemove(productId, size = null) {
    try {
      await removeFromCart(productId, size);  // passing size also
      showAlert('Item removed from cart.');
      loadCart();
    } catch (err) {
      showAlert(err.message, 'error');
    }
  }

  // clear whole cart
  async function handleClearCart() {
    if (!confirm('Remove all items from cart?')) return;
    try {
      await clearCart();
      loadCart();
    } catch (err) {
      showAlert(err.message, 'error');
    }
  }

  // load cart data and render on page
  async function loadCart() {
    const container = document.getElementById('cart-container');
    try {
      const cart  = await fetchCart();
      const items = cart.items ?? [];

      // if cart empty show empty state
      if (!items.length) {
        container.innerHTML = `
          <div class="empty-state">
            <img class="empty-state-img" src="assets/icons/empty-cart.svg" alt="">
            <h3>Your cart is empty</h3>
            <p>Looks like you haven't added anything yet</p>
            <a href="index.html" class="btn btn-primary btn-lg">Browse Products</a>
          </div>`;
        return;
      }

      container.innerHTML = `
        <div class="cart-layout">
          <div class="cart-section">
            <div class="cart-section-head">
              <h3>${items.length} Item${items.length > 1 ? 's' : ''} in Cart</h3>
              <button class="btn btn-danger btn-sm" id="clear-cart-btn">Clear Cart</button>
            </div>
            ${items.map(cartItemRow).join('')}
          </div>

          <div class="order-summary">
            <div class="summary-head"><h3>Order Summary</h3></div>
            <div class="summary-body">
              <div class="summary-row">
                <span>Subtotal (${items.length} items)</span>
                <span>$${parseFloat(cart.total_price).toFixed(2)}</span>
              </div>
              <div class="summary-row">
                <span>Shipping</span>
                <span class="free-badge">Free</span>
              </div>
              <div class="summary-row">
                <span>Tax</span>
                <span>$0.00</span>
              </div>
              <div class="summary-row total">
                <span>Total</span>
                <span>$${parseFloat(cart.total_price).toFixed(2)}</span>
              </div>
            </div>
            <div class="summary-footer">
              <button class="btn btn-primary" style="width:100%" id="checkout-btn">
                Proceed to Checkout →
              </button>
              <a href="index.html" class="btn btn-ghost" style="width:100%;text-align:center">
                Continue Shopping
              </a>
            </div>
          </div>
        </div>`;

      // attach events to buttons created dynamically
      document.getElementById('clear-cart-btn').addEventListener('click', handleClearCart);
      document.getElementById('checkout-btn').addEventListener('click', openModal);

      document.querySelectorAll('.cart-remove-btn').forEach(btn => {
        btn.addEventListener('click', function () {
          const pid  = this.dataset.pid;
          const size = this.dataset.size || null;  // get size from button
          handleRemove(pid, size);
        });
      });

    } catch (err) {
      container.innerHTML = `<div class="empty-state"><h3>${err.message}</h3></div>`;
    }
  }

  // static button event bindings
  document.getElementById('place-order-btn').addEventListener('click', confirmOrder);
  document.getElementById('cancel-order-btn').addEventListener('click', closeModal);
  document.getElementById('logout-btn').addEventListener('click', logout);

  // close modal if clicked outside
  document.getElementById('checkout-modal').addEventListener('click', function (e) {
    if (e.target === this) closeModal();
  });

  // initial load
  loadCart();

});