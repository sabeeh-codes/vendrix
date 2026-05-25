'use strict';

const BASE_URL    = 'http://127.0.0.1:8000';
const sliderState = {};
let   activeGender = '';

function fixUrl(url) {
  if (!url) return null;
  if (url.startsWith('http')) return url;
  return BASE_URL + url;
}

function initNav() {
  const loggedIn = isLoggedIn();
  const username = localStorage.getItem('username') || '';

  const logoutBtn = document.getElementById('logout-btn');
  const loginLink = document.getElementById('nav-login');
  const navUser   = document.getElementById('nav-user');

  if (logoutBtn) logoutBtn.style.display = loggedIn ? 'inline-block' : 'none';
  if (loginLink) loginLink.style.display  = loggedIn ? 'none'        : 'inline-block';
  if (navUser)   navUser.style.display    = loggedIn ? 'flex'        : 'none';

  if (loggedIn && username) {
    const un = document.getElementById('nav-username');
    const av = document.getElementById('nav-avatar');
    if (un) un.textContent = username;
    if (av) av.textContent = username.charAt(0).toUpperCase();
  }
}

function showToast(msg) {
  const el = document.getElementById('toast');
  if (!el) return;
  el.textContent   = msg;
  el.style.display = 'block';
  clearTimeout(el._t);
  el._t = setTimeout(() => el.style.display = 'none', 2500);
}

function showAlert(msg, type = 'error') {
  const el = document.getElementById('alert');
  if (!el) return;
  el.className     = `alert alert-${type}`;
  el.textContent   = msg;
  el.style.display = 'block';
  clearTimeout(el._t);
  el._t = setTimeout(() => el.style.display = 'none', 3500);
}

function setGender(gender, el) {
  activeGender = gender;
  document.querySelectorAll('.gender-pill').forEach(p => p.classList.remove('active'));
  el.classList.add('active');
  loadProducts();
}

async function loadCategories() {
  try {
    const data = await fetchCategories();
    const sel  = document.getElementById('category');
    (data.results ?? data).forEach(cat => {
      const opt       = document.createElement('option');
      opt.value       = cat.id;
      opt.textContent = cat.name;
      sel.appendChild(opt);
    });
  } catch (e) {
    console.warn('Categories failed to load:', e);
  }
}

function selectSize(btn, productId) {
  const sizeSection = btn.closest('.card-sizes');
  if (!sizeSection) return;
  sizeSection.querySelectorAll('.size-btn').forEach(b => b.classList.remove('selected'));
  btn.classList.add('selected');
  const hidden = sizeSection.querySelector('.size-hidden');
  if (hidden) hidden.value = btn.dataset.size;
}

function selectColor(btn, productId) {
  const card = btn.closest('.product-card');
  if (!card) return;

  card.querySelectorAll('.color-circle-btn').forEach(b => {
    b.classList.remove('selected');
    b.style.outline       = 'none';
    b.style.outlineOffset = '0';
    b.style.transform     = 'scale(1)';
  });

  btn.classList.add('selected');
  btn.style.outline       = '2.5px solid #e94560';
  btn.style.outlineOffset = '2px';
  btn.style.transform     = 'scale(1.2)';

  const colorHidden = card.querySelector('.color-hidden');
  const nameLabel   = card.querySelector('.color-name-label');

  if (colorHidden) colorHidden.value = btn.dataset.color;
  if (nameLabel)   nameLabel.textContent = btn.dataset.color;
}

function changeQty(productId, delta, maxStock) {
  const card = document.querySelector(`.product-card[data-product-id="${productId}"]`);
  if (!card) return;

  const hiddenEl  = card.querySelector('.qty-hidden');
  const displayEl = card.querySelector('.qty-num');
  if (!hiddenEl) return;

  const limit  = (maxStock !== undefined && maxStock !== null) ? maxStock : 99;
  let current  = parseInt(hiddenEl.value) || 1;
  current      = Math.min(Math.max(1, current + delta), limit);

  hiddenEl.value = current;
  if (displayEl) displayEl.textContent = current;
}

function slideImage(productId, direction) {
  const slider = document.getElementById(`slider-${productId}`);
  if (!slider) return;
  const slides = slider.querySelectorAll('.slide');
  const dots   = slider.querySelectorAll('.dot');
  if (!slides.length) return;

  if (sliderState[productId] === undefined) sliderState[productId] = 0;

  slides[sliderState[productId]].classList.remove('active');
  if (dots[sliderState[productId]]) dots[sliderState[productId]].classList.remove('active');

  sliderState[productId] = (sliderState[productId] + direction + slides.length) % slides.length;

  slides[sliderState[productId]].classList.add('active');
  if (dots[sliderState[productId]]) dots[sliderState[productId]].classList.add('active');
}

function goToSlide(productId, index) {
  const slider = document.getElementById(`slider-${productId}`);
  if (!slider) return;
  const slides = slider.querySelectorAll('.slide');
  const dots   = slider.querySelectorAll('.dot');
  if (!slides.length) return;

  if (sliderState[productId] === undefined) sliderState[productId] = 0;

  slides[sliderState[productId]].classList.remove('active');
  if (dots[sliderState[productId]]) dots[sliderState[productId]].classList.remove('active');

  sliderState[productId] = index;
  slides[index].classList.add('active');
  if (dots[index]) dots[index].classList.add('active');
}

async function loadProducts() {
  const container = document.getElementById('products-container');
  container.innerHTML = `
    <div class="loading">
      <div class="loading-spinner"></div>
      Loading products...
    </div>`;

  const params    = {};
  const search    = document.getElementById('search').value.trim();
  const category  = document.getElementById('category').value;
  const minPrice  = document.getElementById('min-price').value;
  const maxPrice  = document.getElementById('max-price').value;
  const ordering  = document.getElementById('ordering').value;

  if (search)       params.search    = search;
  if (category)     params.category  = category;
  if (minPrice)     params.min_price = minPrice;
  if (maxPrice)     params.max_price = maxPrice;
  if (ordering)     params.ordering  = ordering;
  if (activeGender) params.gender    = activeGender;

  try {
    const data     = await fetchProducts(params);
    const products = data.results ?? data;

    if (!products.length) {
      container.innerHTML = `
        <div class="empty-state">
          <img class="empty-state-img" src="assets/icons/empty-box.svg" alt="">
          <h3>No products found</h3>
          <p>Try adjusting your filters</p>
          <button class="btn btn-primary" onclick="resetFilters()">Clear Filters</button>
        </div>`;
      return;
    }

    container.innerHTML = `<div class="products-grid">${products.map(productCard).join('')}</div>`;

  } catch (err) {
    container.innerHTML = `
      <div class="empty-state">
        <h3>Failed to load products</h3>
        <p>${err.message}</p>
      </div>`;
  }
}

function productCard(p) {
  const pid = p.id;

  // Images
  const allImages = [];
  if (p.images && p.images.length) {
    // sort primary image first, then by order
    const sorted = [...p.images].sort((a, b) => {
      if (a.is_primary && !b.is_primary) return -1;
      if (!a.is_primary && b.is_primary) return 1;
      return (a.order ?? 0) - (b.order ?? 0);
    });
    sorted.forEach(img => {
      const url = fixUrl(img.image);
      if (url) allImages.push(url);
    });
  }
  if (!allImages.length && p.image) {
    allImages.push(fixUrl(p.image));
  }

  const imageSlider = allImages.length
    ? `<div class="slider" id="slider-${pid}">
         <div class="slides">
           ${allImages.map((src, i) => `
             <div class="slide ${i === 0 ? 'active' : ''}">
               <img src="${src}" alt="${p.name}" loading="lazy"
                    style="width:100%;height:200px;object-fit:contain;
                           background:#f5f5f5;display:block;">
             </div>`).join('')}
         </div>
         ${allImages.length > 1 ? `
           <button class="slide-btn slide-prev"
             onclick="slideImage(${pid}, -1)">&#8249;</button>
           <button class="slide-btn slide-next"
             onclick="slideImage(${pid}, 1)">&#8250;</button>
           <div class="slide-dots">
             ${allImages.map((_, i) => `
               <span class="dot ${i === 0 ? 'active' : ''}"
                 onclick="goToSlide(${pid}, ${i})"></span>`).join('')}
           </div>` : ''}
       </div>`
    : `<div class="no-image"
             style="height:200px;display:flex;align-items:center;
                    justify-content:center;background:#f5f5f5;">
         <span style="color:#aaa;font-size:12px;">No Image</span>
       </div>`;

  // Sizes
  const sizeArray   = Array.isArray(p.sizes) ? p.sizes : [];
  const sizeSection = sizeArray.length
    ? `<div class="card-sizes">
         <span class="card-label">Size</span>
         <div class="size-options">
           ${sizeArray.map((s, i) => `
             <button type="button"
               class="size-btn ${i === 0 ? 'selected' : ''}"
               data-size="${s}"
               onclick="selectSize(this, ${pid})">
               ${s}
             </button>`).join('')}
         </div>
         <input type="hidden" class="size-hidden" value="${sizeArray[0] || ''}">
       </div>`
    : '';

  // Colors
  const colorArray   = Array.isArray(p.colors) ? p.colors : [];
  const colorSection = colorArray.length
    ? `<div class="card-colors">
         <span class="card-label">
           Color —
           <span class="color-name-label"
                 style="font-weight:700;color:var(--dark);">
             ${colorArray[0].name}
           </span>
         </span>
         <div class="color-options">
           ${colorArray.map((c, i) => `
             <button type="button"
               class="color-circle-btn ${i === 0 ? 'selected' : ''}"
               data-color="${c.name}"
               data-color-id="${c.id}"
               title="${c.name}"
               onclick="selectColor(this, ${pid})"
               style="background:${c.hex_code};border:1.5px solid #bbb;
                      outline:${i === 0 ? '2.5px solid #e94560' : 'none'};
                      outline-offset:${i === 0 ? '2px' : '0'};
                      transform:${i === 0 ? 'scale(1.2)' : 'scale(1)'};">
             </button>`).join('')}
         </div>
         <input type="hidden" class="color-hidden"   value="${colorArray[0].name}">
         <input type="hidden" class="color-id-hidden" value="${colorArray[0].id}">
       </div>`
    : '';

  // Quantity
  const qtySection = `
    <div class="card-qty">
      <span class="card-label">Qty</span>
      <div class="qty-controls">
        <button type="button" class="qty-btn"
          onclick="changeQty(${pid}, -1)">−</button>
        <span class="qty-num">1</span>
        <button type="button" class="qty-btn"
          onclick="changeQty(${pid}, 1, ${p.stock ?? 0})">+</button>
        <input type="hidden" class="qty-hidden" value="1">
      </div>
    </div>`;

  const isNew = (Date.now() - new Date(p.created_at).getTime()) < 7 * 24 * 60 * 60 * 1000;

  return `
    <div class="product-card" data-product-id="${pid}">
      <div class="product-image-wrap">
        ${imageSlider}
        ${isNew && p.stock > 0 ? '<span class="product-badge badge-new">New</span>' : ''}
        ${p.stock <= 0          ? '<span class="product-badge badge-out">Out of stock</span>' : ''}
      </div>
      <div class="card-body">
        <div style="display:flex;justify-content:space-between;
                    align-items:center;margin-bottom:4px;">
          <span class="product-category">${p.category_name || ''}</span>
          ${p.gender
            ? `<span class="gender-badge gender-${p.gender}">
                 ${p.gender.charAt(0).toUpperCase() + p.gender.slice(1)}
               </span>`
            : ''}
        </div>
        <h3>${p.name}</h3>
        <p class="product-desc">${p.description || ''}</p>
        ${sizeSection}
        ${colorSection}
        ${qtySection}
      </div>
      <div class="card-footer">
        <div class="price">
          <span class="amount">$${parseFloat(p.price).toFixed(2)}</span>
          ${p.stock > 0 ? `<span class="stock-left">${p.stock} left</span>` : ''}
        </div>
        ${p.stock > 0
          ? `<button class="btn btn-primary btn-sm add-cart-btn"
               data-id="${pid}">Add to Cart</button>`
          : `<span class="out-of-stock">Out of stock</span>`}
      </div>
    </div>`;
}

document.getElementById('products-container').addEventListener('click', async e => {
  const btn = e.target.closest('.add-cart-btn');
  if (!btn) return;

  if (!isLoggedIn()) { showAlert('Please login to add items to cart.'); return; }

  const card = btn.closest('.product-card');
  if (!card) return;

  const sizeInput    = card.querySelector('.size-hidden');
  const colorInput   = card.querySelector('.color-hidden');
  const colorIdInput = card.querySelector('.color-id-hidden');
  const qtyInput     = card.querySelector('.qty-hidden');

  const size     = sizeInput    ? sizeInput.value.trim()               : null;
  const color    = colorInput   ? colorInput.value.trim()              : null;
  const color_id = colorIdInput ? parseInt(colorIdInput.value) || null : null;
  const quantity = qtyInput     ? parseInt(qtyInput.value)    || 1     : 1;
  const pid      = btn.dataset.id;

  if (sizeInput  && !size)    { showAlert('Please select a size.');  return; }
  if (colorInput && !color_id){ showAlert('Please select a color.'); return; }

  btn.disabled    = true;
  btn.textContent = 'Adding...';

  try {
    await addToCart(pid, quantity, size || null, color_id);
    showToast('Added to cart! 🛒');
  } catch (err) {
    showAlert(err.message);
  } finally {
    btn.disabled    = false;
    btn.textContent = 'Add to Cart';
  }
});

function resetFilters() {
  document.getElementById('search').value    = '';
  document.getElementById('category').value  = '';
  document.getElementById('min-price').value = '';
  document.getElementById('max-price').value = '';
  document.getElementById('ordering').value  = '-created_at';
  activeGender = '';
  document.querySelectorAll('.gender-pill').forEach((p, i) => p.classList.toggle('active', i === 0));
  loadProducts();
}

document.getElementById('logout-btn')?.addEventListener('click', logout);
document.getElementById('search-btn')?.addEventListener('click', loadProducts);
document.getElementById('reset-btn')?.addEventListener('click', resetFilters);
document.getElementById('search')?.addEventListener('keydown', e => { if (e.key === 'Enter') loadProducts(); });
document.querySelectorAll('.gender-pill').forEach(btn => {
  btn.addEventListener('click', () => setGender(btn.dataset.gender, btn));
});

initNav();
loadCategories();
loadProducts();