if (!isLoggedIn()) window.location.href = 'auth.html';

const u = localStorage.getItem('username') || '';
document.getElementById('nav-username').textContent = u;
document.getElementById('nav-avatar').textContent   = u.charAt(0).toUpperCase();

let stripe      = null;
let cardElement = null;

function mountStripeCard(publishableKey) {
  stripe = Stripe(publishableKey);
  const elements = stripe.elements();

  cardElement = elements.create('card', {
    style: {
      base: {
        fontSize: '16px',
        color: '#1a1a2e',
        fontFamily: 'Segoe UI, sans-serif',
        '::placeholder': { color: '#b0bec5' },
      },
      invalid: { color: '#e94560' },
    },
  });

  cardElement.mount('#stripe-card-element');
  cardElement.on('change', e => {
    document.getElementById('card-errors').textContent = e.error ? e.error.message : '';
  });
}

let selectedPayment = 'cod';

function selectPayment(method) {
  selectedPayment = method;
  document.getElementById('opt-cod').classList.toggle('selected', method === 'cod');
  document.getElementById('opt-card').classList.toggle('selected', method === 'card');
  document.getElementById('cod-section').style.display  = method === 'cod'  ? 'block' : 'none';
  document.getElementById('card-section').style.display = method === 'card' ? 'block' : 'none';
}

// show alert message
function showAlert(msg, type = 'success') {
  const el = document.getElementById('alert');
  el.className     = `alert alert-${type}`;
  el.textContent   = msg;
  el.style.display = 'block';
  setTimeout(() => el.style.display = 'none', 4000);
}

// show modal error message
function showModalAlert(msg) {
  const el = document.getElementById('modal-alert');
  el.className     = 'alert alert-error';
  el.textContent   = msg;
  el.style.display = 'block';
}

// render product image or placeholder
function imgOrPlaceholder(src, name) {
  if (src) {
    return `<img src="${src}" alt="${name}"
             onerror="this.parentElement.innerHTML='<div class=img-placeholder></div>'">`;
  }
  return `<div class="img-placeholder"></div>`;
}

// render cart item row
function cartItemRow(item) {
  const name      = item.product_detail?.name  ?? `Product #${item.product}`;
  const img       = item.product_detail?.image ?? null;
  const price     = parseFloat(item.subtotal).toFixed(2);
  const pid       = item.product_detail?.id    ?? item.product;
  const size      = item.size       || '';
  const colorId   = item.color      || '';
  const colorName = item.color_name || '';
  const colorHex  = item.color_hex  || '';

  const colorDot = colorHex
    ? `<span style="display:inline-block;width:12px;height:12px;
                    border-radius:50%;background:${colorHex};
                    border:1px solid #ccc;margin-right:4px;
                    vertical-align:middle;"></span>`
    : '';

  return `
    <div class="cart-item">
      <div class="cart-item-image">
        ${imgOrPlaceholder(img, name)}
      </div>
      <div class="cart-item-info">
        <h4>${name}</h4>
        <div class="item-meta">
          Qty: ${item.quantity}
          ${size      ? ` &middot; Size: <strong>${size}</strong>`                        : ''}
          ${colorName ? ` &middot; Color: ${colorDot}<strong>${colorName}</strong>`       : ''}
        </div>
      </div>
      <div class="cart-item-price">$${price}</div>
      <button class="cart-remove-btn"
              data-pid="${pid}"
              data-size="${size}"
              data-color-id="${colorId}"
              title="Remove">✕</button>
    </div>`;
}

async function openModal() {
  document.getElementById('checkout-modal').classList.add('open');
  selectPayment('cod');

  if (!stripe) {
    try {
      const data = await createPaymentIntent();
      mountStripeCard(data.publishable_key);
    } catch (err) {
      console.error('Stripe init failed:', err.message);
    }
  }
}

function closeModal() {
  document.getElementById('checkout-modal').classList.remove('open');
  document.getElementById('modal-alert').style.display = 'none';
  document.getElementById('shipping-address').value    = '';
  document.getElementById('card-errors').textContent   = '';
}

// confirm order placement
async function confirmOrder() {
  const address = document.getElementById('shipping-address').value.trim();
  const btn     = document.getElementById('place-order-btn');

  document.getElementById('modal-alert').style.display = 'none';

  if (!address) {
    showModalAlert('Please enter a shipping address.');
    return;
  }

  btn.textContent = 'Processing...';
  btn.disabled    = true;

  try {
    if (selectedPayment === 'cod') {
      const order = await placeOrder(address, 'cod', null);
      closeModal();
      showAlert(`Order #${order.id} placed! Cash on Delivery.`);
      setTimeout(() => window.location.href = 'orders.html', 2000);
      return;
    }

    const intentData = await createPaymentIntent();

    const { paymentIntent, error } = await stripe.confirmCardPayment(
      intentData.client_secret,
      { payment_method: { card: cardElement } }
    );

    if (error) {
      showModalAlert(error.message);
      btn.textContent = 'Place Order';
      btn.disabled    = false;
      return;
    }

    if (paymentIntent.status !== 'succeeded') {
      showModalAlert('Payment failed. Please try again.');
      btn.textContent = 'Place Order';
      btn.disabled    = false;
      return;
    }

    const order = await placeOrder(address, 'card', paymentIntent.id);
    closeModal();
    showAlert(`Order #${order.id} placed! Card payment successful.`);
    setTimeout(() => window.location.href = 'orders.html', 2000);

  } catch (err) {
    showModalAlert(err.message);
    btn.textContent = 'Place Order';
    btn.disabled    = false;
  }
}

// remove item from cart
async function handleRemove(productId, size = null, colorId = null) {
  try {
    await removeFromCart(productId, size, colorId);
    showAlert('Item removed from cart.');
    loadCart();
  } catch (err) {
    showAlert(err.message, 'error');
  }
}

// clear cart
async function handleClearCart() {
  if (!confirm('Remove all items from cart?')) return;
  try {
    await clearCart();
    loadCart();
  } catch (err) {
    showAlert(err.message, 'error');
  }
}

// load cart data
async function loadCart() {
  const container = document.getElementById('cart-container');
  try {
    const cart  = await fetchCart();
    const items = cart.items ?? [];

    if (!items.length) {
      container.innerHTML = `
        <div class="empty-state">
          <h3>Your cart is empty</h3>
          <p>No items added yet</p>
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

    document.getElementById('clear-cart-btn').addEventListener('click', handleClearCart);
    document.getElementById('checkout-btn').addEventListener('click', openModal);

    document.querySelectorAll('.cart-remove-btn').forEach(btn => {
      btn.addEventListener('click', function () {
        handleRemove(this.dataset.pid, this.dataset.size || null, this.dataset.colorId || null);
      });
    });

  } catch (err) {
    container.innerHTML = `<div class="empty-state"><h3>${err.message}</h3></div>`;
  }
}

document.getElementById('place-order-btn').addEventListener('click', confirmOrder);
document.getElementById('cancel-order-btn').addEventListener('click', closeModal);
document.getElementById('logout-btn').addEventListener('click', logout);

document.getElementById('checkout-modal').addEventListener('click', function (e) {
  if (e.target === this) closeModal();
});

loadCart();