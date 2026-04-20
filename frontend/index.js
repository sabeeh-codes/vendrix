let activeGender = '';

// setup navbar based on login state
function initNav() {
  const loggedIn = isLoggedIn();
  const username = localStorage.getItem('username') || '';

  const logoutBtn = document.getElementById('logout-btn');
  const loginLink = document.getElementById('nav-login');
  const navUser   = document.getElementById('nav-user');

  if (logoutBtn) logoutBtn.style.display = loggedIn ? 'inline-block' : 'none';
  if (loginLink) loginLink.style.display  = loggedIn ? 'none' : 'inline-block';
  if (navUser)   navUser.style.display    = loggedIn ? 'flex' : 'none';

  // show username and first letter as avatar
  if (loggedIn && username) {
    const navUsername = document.getElementById('nav-username');
    const navAvatar   = document.getElementById('nav-avatar');
    if (navUsername) navUsername.textContent = username;
    if (navAvatar)   navAvatar.textContent   = username.charAt(0).toUpperCase();
  }
}

// small toast popup message
function showToast(msg) {
  const el = document.getElementById('toast');
  el.textContent   = msg;
  el.style.display = 'block';
  setTimeout(() => el.style.display = 'none', 2500);
}

// alert message (error/success)
function showAlert(msg, type = 'error') {
  const el = document.getElementById('alert');
  el.className     = `alert alert-${type}`;
  el.textContent   = msg;
  el.style.display = 'block';
  setTimeout(() => el.style.display = 'none', 3000);
}

// set selected gender filter and reload products
function setGender(gender, el) {
  activeGender = gender;
  document.querySelectorAll('.gender-pill').forEach(p => p.classList.remove('active'));
  el.classList.add('active');
  loadProducts();
}

// handle size button selection for product
function selectSize(btn, productId) {
  document.querySelectorAll(`#sizes-${productId} .size-btn`).forEach(b => {
    b.classList.remove('selected');
  });
  btn.classList.add('selected');
  document.getElementById(`size-${productId}`).value = btn.dataset.size;
}

// increase/decrease quantity (with limits)
function changeQty(productId, delta, maxStock = 99) {
  const input   = document.getElementById(`qty-${productId}`);
  const display = document.getElementById(`qty-display-${productId}`);
  let current   = parseInt(input.value) || 1;
  current       = Math.min(Math.max(1, current + delta), maxStock);
  input.value   = current;
  display.textContent = current;
}

// load categories into dropdown
async function loadCategories() {
  try {
    const data = await fetchCategories();
    const sel  = document.getElementById('category');
    (data.results ?? data).forEach(cat => {
      const opt = document.createElement('option');
      opt.value       = cat.id;
      opt.textContent = cat.name;
      sel.appendChild(opt);
    });
  } catch (e) {
    console.error('Category load failed', e);
  }
}

// load products from API and render
async function loadProducts() {
  const container = document.getElementById('products-container');
  container.innerHTML = `
    <div class="loading">
      <div class="loading-spinner"></div>
      Loading products...
    </div>`;

  // collect filter values
  const params = {
    search:    document.getElementById('search').value.trim(),
    category:  document.getElementById('category').value,
    min_price: document.getElementById('min-price').value,
    max_price: document.getElementById('max-price').value,
    ordering:  document.getElementById('ordering').value,
    gender:    activeGender
  };

  try {
    const data     = await fetchProducts(params);
    const products = data.results ?? data;

    // if no products found
    if (!products.length) {
      container.innerHTML = `
        <div class="empty-state">
          <h3>No products found</h3>
          <p>Try adjusting filters</p>
        </div>`;
      return;
    }

    // render products in grid (fixed size cards)
    container.innerHTML = `
      <div class="products-grid" style="display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,220px));gap:20px;justify-content:start;">
        ${products.map(productCard).join('')}
      </div>`;

  } catch (err) {
    container.innerHTML = `<p>Error: ${err.message}</p>`;
  }
}

// create single product card html
function productCard(p) {
  const imgSrc = p.image || '';

  // show image or fallback if missing
  const imageHTML = imgSrc
    ? `<img src="${imgSrc}" alt="${p.name}"
           style="width:100%;height:200px;object-fit:contain;background:#f5f5f5;display:block;">`
    : `<div style="height:200px;display:flex;align-items:center;justify-content:center;background:#f5f5f5;">
         <span style="color:#aaa;font-size:12px;">No Image</span>
       </div>`;

  // size buttons if product has sizes
  const sizeButtons = (p.sizes && p.sizes.length)
    ? `<div style="margin-bottom:8px;">
         <span style="font-size:10px;font-weight:700;letter-spacing:1px;color:#888;">SIZE</span>
         <div id="sizes-${p.id}" style="display:flex;gap:5px;flex-wrap:wrap;margin-top:4px;">
           ${p.sizes.map((s, i) => `
             <button type="button"
               class="size-btn ${i === 0 ? 'selected' : ''}"
               data-size="${s}"
               onclick="selectSize(this, ${p.id})"
               style="padding:3px 9px;font-size:11px;border-radius:4px;">
               ${s}
             </button>`).join('')}
         </div>
         <input type="hidden" id="size-${p.id}" value="${p.sizes[0]}">
       </div>`
    : '';

  // quantity selector UI
  const quantityControl = `
    <div style="margin-bottom:8px;">
      <span style="font-size:10px;font-weight:700;letter-spacing:1px;color:#888;">QUANTITY</span>
      <div style="display:flex;align-items:center;gap:6px;margin-top:4px;">
        <button type="button" class="qty-btn"
          onclick="changeQty(${p.id}, -1)"
          style="width:24px;height:24px;font-size:14px;line-height:1;">−</button>
        <span id="qty-display-${p.id}"
          style="min-width:18px;text-align:center;font-size:13px;">1</span>
        <button type="button" class="qty-btn"
          onclick="changeQty(${p.id}, 1, ${p.stock})"
          style="width:24px;height:24px;font-size:14px;line-height:1;">+</button>
        <input type="hidden" id="qty-${p.id}" value="1">
      </div>
    </div>`;

  return `
    <div class="product-card"
         style="width:220px;font-size:13px;border-radius:10px;overflow:hidden;
                box-shadow:0 2px 8px rgba(0,0,0,0.08);background:#fff;">
      <div style="position:relative;">
        ${imageHTML}
        ${p.stock <= 0
          ? '<span class="product-badge badge-out" style="position:absolute;top:8px;left:8px;">Out of stock</span>'
          : ''}
      </div>
      <div style="padding:10px 12px 6px;">
        <span class="product-category"
              style="font-size:10px;font-weight:700;letter-spacing:1px;">
          ${p.category_name || ''}
        </span>
        <h3 style="font-size:13px;font-weight:700;margin:3px 0 4px;line-height:1.3;">
          ${p.name}
        </h3>
        <p style="font-size:11px;color:#777;margin:0 0 8px;line-height:1.4;
                  display:-webkit-box;-webkit-line-clamp:2;
                  -webkit-box-orient:vertical;overflow:hidden;">
          ${p.description || ''}
        </p>
        ${sizeButtons}
        ${quantityControl}
      </div>
      <div style="padding:8px 12px 12px;display:flex;align-items:center;justify-content:space-between;">
        <span style="font-size:16px;font-weight:800;color:#e63946;">
          $${parseFloat(p.price).toFixed(2)}
        </span>
        ${p.stock > 0
          ? `<button class="btn btn-primary btn-sm add-cart-btn" data-id="${p.id}"
               style="font-size:11px;padding:6px 12px;border-radius:20px;">
               Add to Cart
             </button>`
          : `<span style="font-size:11px;color:#aaa;">Out of stock</span>`
        }
      </div>
    </div>`;
}

// handle add to cart clicks (using event delegation)
document.getElementById('products-container').addEventListener('click', async function (e) {
  const btn = e.target.closest('.add-cart-btn');
  if (!btn) return;

  // must be logged in to add items
  if (!isLoggedIn()) {
    showAlert('Login required');
    return;
  }

  const productId = btn.dataset.id;
  const sizeEl    = document.getElementById(`size-${productId}`);
  const qtyEl     = document.getElementById(`qty-${productId}`);
  const size      = sizeEl ? sizeEl.value : null;
  const quantity  = qtyEl  ? parseInt(qtyEl.value) : 1;

  // basic validation
  if (sizeEl && !size)           { showAlert('Please select a size'); return; }
  if (!quantity || quantity < 1) { showAlert('Invalid quantity');      return; }

  btn.disabled    = true;
  btn.textContent = 'Adding...';

  try {
    await addToCart(productId, quantity, size);
    showToast('Added to cart!');
  } catch (err) {
    showAlert(err.message);
  } finally {
    btn.disabled    = false;
    btn.textContent = 'Add to Cart';
  }
});

// reset all filters back to default
function resetFilters() {
  document.getElementById('search').value    = '';
  document.getElementById('category').value  = '';
  document.getElementById('min-price').value = '';
  document.getElementById('max-price').value = '';
  document.getElementById('ordering').value  = '-created_at';
  activeGender = '';
  document.querySelectorAll('.gender-pill').forEach((p, i) => {
    p.classList.toggle('active', i === 0);
  });
  loadProducts();
}

// button event listeners
document.getElementById('logout-btn').addEventListener('click', logout);
document.getElementById('search-btn').addEventListener('click', loadProducts);
document.getElementById('reset-btn').addEventListener('click', resetFilters);

// allow enter key to trigger search
document.getElementById('search').addEventListener('keydown', e => {
  if (e.key === 'Enter') loadProducts();
});

// gender filter buttons
document.querySelectorAll('.gender-pill').forEach(btn => {
  btn.addEventListener('click', () => setGender(btn.dataset.gender, btn));
});

// initial setup
initNav();
loadCategories();
loadProducts();