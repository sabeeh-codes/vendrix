// if not logged in, redirect to login page
if (!isLoggedIn()) window.location.href = 'auth.html';

// set username and avatar in navbar
const u = localStorage.getItem('username') || '';
document.getElementById('nav-username').textContent = u;
document.getElementById('nav-avatar').textContent   = u.charAt(0).toUpperCase();

// map order status to badge class
const STATUS_BADGE = {
  pending:   'badge-pending',
  confirmed: 'badge-confirmed',
  shipped:   'badge-shipped',
  delivered: 'badge-delivered',
  cancelled: 'badge-cancelled',
};

// helper to show image or fallback if missing/broken
function imgOrPlaceholder(src, name) {
  if (src) {
    return `<img
      src="http://127.0.0.1:8000${src}"
      alt="${name}"
      onerror="this.parentElement.innerHTML='<div class=\\'img-placeholder\\'><img src=\\'assets/icons/hanger.svg\\' alt=\\'\\'/></div>'"
    >`;
  }
  return `<div class="img-placeholder">
            <img src="assets/icons/hanger.svg" alt="">
          </div>`;
}

// load all orders from API
async function loadOrders() {
  const container = document.getElementById('orders-container');
  try {
    const data   = await fetchOrders();
    const orders = data.results ?? data;

    // if no orders found
    if (!orders.length) {
      container.innerHTML = `
        <div class="empty-state">
          <img class="empty-state-img" src="assets/icons/empty-box.svg" alt="">
          <h3>No orders yet</h3>
          <p>Start shopping to place your first order</p>
          <a href="index.html" class="btn btn-primary btn-lg">Browse Products</a>
        </div>`;
      return;
    }

    // render all orders
    container.innerHTML = orders.map(orderCard).join('');

  } catch (err) {
    container.innerHTML = `<div class="empty-state"><h3>${err.message}</h3></div>`;
  }
}

// create single order card html
function orderCard(order) {
  const badge = STATUS_BADGE[order.status] ?? 'badge-pending';

  // format order date nicely
  const date  = new Date(order.created_at).toLocaleDateString('en-US', {
    year: 'numeric', month: 'long', day: 'numeric',
  });

  // build items list inside order
  const itemsHtml = order.items.map(item => `
    <div class="order-item-row">
      <div class="order-item-img">
        ${imgOrPlaceholder(item.product_image ?? null, item.product_name)}
      </div>
      <div class="order-item-name">
        ${item.product_name}
        <div style="font-size:0.82rem;color:var(--text-muted);margin-top:2px;">
          Qty: ${item.quantity}
        </div>
      </div>
      <div class="order-item-price">$${parseFloat(item.subtotal).toFixed(2)}</div>
    </div>`).join('');

  return `
    <div class="order-card">
      <div class="order-card-head">
        <div class="order-id-wrap">
          <h3>Order #${order.id}</h3>
          <div class="order-date">${date}</div>
        </div>
        <span class="badge ${badge}">${order.status}</span>
      </div>

      <div class="order-card-body">
        <div class="order-address">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
               stroke="currentColor" stroke-width="2"
               style="flex-shrink:0;color:var(--text-muted)">
            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"/>
            <circle cx="12" cy="10" r="3"/>
          </svg>
          ${order.shipping_address}
        </div>
        <div class="order-items-list">
          ${itemsHtml}
        </div>
      </div>

      <div class="order-card-foot">
        <span class="order-count">${order.items.length} item(s)</span>
        <span class="order-total">Total: $${parseFloat(order.total_price).toFixed(2)}</span>
      </div>
    </div>`;
}

// initial load when page opens
loadOrders();