if (!isLoggedIn()) window.location.href = 'auth.html';

const u = localStorage.getItem('username') || '';
document.getElementById('nav-username').textContent = u;
document.getElementById('nav-avatar').textContent   = u.charAt(0).toUpperCase();

const STATUS_BADGE = {
  pending:   'badge-pending',
  confirmed: 'badge-confirmed',
  shipped:   'badge-shipped',
  delivered: 'badge-delivered',
  cancelled: 'badge-cancelled',
};

const PAYMENT_STATUS_LABEL = {
  unpaid: { label: ' Unpaid', color: '#721c24', bg: '#f8d7da' },
  paid:   { label: ' Paid',   color: '#155724', bg: '#d4edda' },
  failed: { label: ' Failed', color: '#721c24', bg: '#f8d7da' },
};

function imgOrPlaceholder(src, name) {
  if (src) {
    return `<img src="${src}" alt="${name}"
             onerror="this.parentElement.innerHTML='<div class=img-placeholder></div>'">`;
  }
  return `<div class="img-placeholder"></div>`;
}

async function handleCancel(orderId) {
  if (!confirm(`Cancel order #${orderId}? Stock will be restored.`)) return;
  try {
    await cancelOrder(orderId);
    showToast(`Order #${orderId} cancelled.`);
    loadOrders();
  } catch (err) {
    showToast(err.message);
  }
}

function showToast(msg) {
  let toast = document.getElementById('toast');
  if (!toast) {
    toast           = document.createElement('div');
    toast.id        = 'toast';
    toast.className = 'toast';
    document.body.appendChild(toast);
  }
  toast.textContent   = msg;
  toast.style.display = 'block';
  setTimeout(() => toast.style.display = 'none', 3000);
}

async function loadOrders() {
  const container = document.getElementById('orders-container');
  try {
    const data   = await fetchOrders();
    const orders = data.results ?? data;

    if (!orders.length) {
      container.innerHTML = `
        <div class="empty-state">
          <h3>No orders yet</h3>
          <p>Start shopping to place your first order</p>
          <a href="index.html" class="btn btn-primary btn-lg">Browse Products</a>
        </div>`;
      return;
    }

    container.innerHTML = orders.map(orderCard).join('');

  } catch (err) {
    container.innerHTML = `<div class="empty-state"><h3>${err.message}</h3></div>`;
  }
}

function orderCard(order) {
  const badge = STATUS_BADGE[order.status] ?? 'badge-pending';

  const date = new Date(order.created_at).toLocaleDateString('en-US', {
    year: 'numeric', month: 'long', day: 'numeric',
  });

  const payMethodBadge = order.payment_method === 'card'
    ? `<span style="background:#e8eaf6;color:#1a237e;padding:3px 10px;
                    border-radius:12px;font-size:0.78rem;font-weight:700;">
         💳 Credit / Debit Card
       </span>`
    : `<span style="background:#fff3cd;color:#856404;padding:3px 10px;
                    border-radius:12px;font-size:0.78rem;font-weight:700;">
         💵 Cash on Delivery
       </span>`;

  const ps = PAYMENT_STATUS_LABEL[order.payment_status] ?? PAYMENT_STATUS_LABEL.unpaid;
  const payStatusBadge = `
    <span style="background:${ps.bg};color:${ps.color};padding:3px 10px;
                 border-radius:12px;font-size:0.78rem;font-weight:700;">
      ${ps.label}
    </span>`;

  const stripeRow = order.payment_method === 'card' && order.stripe_payment_intent_id
    ? `<div style="font-size:0.82rem;color:var(--text-muted);margin-top:6px;">
         Stripe ID:
         <strong style="font-family:monospace;font-size:0.78rem;">
           ${order.stripe_payment_intent_id}
         </strong>
       </div>`
    : '';

  const canCancel = ['pending', 'confirmed'].includes(order.status)
    && order.payment_status !== 'paid';

  const cancelBtn = canCancel
    ? `<button class="btn btn-danger btn-sm" onclick="handleCancel(${order.id})">
         Cancel Order
       </button>`
    : '';

  const itemsHtml = order.items.map(item => {
    // size pill
    const sizePart = item.size
      ? `<span style="background:#f0f0f0;padding:2px 8px;border-radius:4px;
                      font-size:0.75rem;font-weight:700;">
           ${item.size}
         </span>`
      : '';

    // color circle + name
    const colorCircle = item.color_hex
      ? `<span style="display:inline-block;width:12px;height:12px;
                      border-radius:50%;background:${item.color_hex};
                      border:1.5px solid #ccc;margin-right:4px;
                      vertical-align:middle;flex-shrink:0;"></span>`
      : '';

    const colorPart = item.color_name
      ? `<span style="display:flex;align-items:center;gap:2px;">
           ${colorCircle}
           <span style="font-size:0.75rem;font-weight:700;">${item.color_name}</span>
         </span>`
      : '';

    return `
      <div class="order-item-row">
        <div class="order-item-img">
          ${imgOrPlaceholder(item.product_image ?? null, item.product_name)}
        </div>
        <div class="order-item-name">
          ${item.product_name}
          <div style="display:flex;gap:6px;flex-wrap:wrap;align-items:center;margin-top:4px;">
            <span style="font-size:0.75rem;color:var(--text-muted);">
              Qty: <strong>${item.quantity}</strong>
            </span>
            ${sizePart}
            ${colorPart}
          </div>
        </div>
        <div class="order-item-price">
          $${parseFloat(item.subtotal).toFixed(2)}
        </div>
      </div>`;
  }).join('');

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
        <div style="display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin-bottom:14px;">
          ${payMethodBadge}
          ${payStatusBadge}
        </div>

        ${stripeRow}

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
        <div style="display:flex;align-items:center;gap:14px;">
          ${cancelBtn}
          <span class="order-total">$${parseFloat(order.total_price).toFixed(2)}</span>
        </div>
      </div>
    </div>`;
}

document.getElementById('logout-btn').addEventListener('click', logout);

loadOrders();