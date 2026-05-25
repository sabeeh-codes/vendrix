# 🛍️ Vendrix — Full-Stack eCommerce Platform

A full-stack eCommerce web application built with **Django REST Framework** backend and **Vanilla JavaScript** frontend. Features complete shopping flow including product browsing, cart management, and secure Stripe card payments.

---

## 🚀 Live Demo

> Open `frontend/index.html` in your browser after running the backend server.

---

## ✨ Features

### 🛒 Shopping
- Product grid with image slider (multiple images per product)
- Filter by gender (Men, Women, Kids, Unisex)
- Filter by category, price range, and search
- Color and size variant selection
- Quantity control with stock validation
- Real-time stock tracking

### 💳 Payments
- **Cash on Delivery** — admin marks paid on delivery
- **Credit/Debit Card** — automatic Stripe payment processing
- Stripe test mode integration (no real charges)
- Payment status tracking

### 📦 Orders
- Full order history with status tracking
- Order cancellation with automatic stock restoration
- Color swatches and size display per order item

### 🔐 Authentication
- JWT-based authentication (access + refresh tokens)
- User registration and login
- Protected routes

### ⚙️ Admin Panel
- Jazzmin-themed Django admin
- Product management with image gallery
- Order status management (confirm, ship, deliver, cancel)
- Color and category management
- Direct delete buttons for products

---

## 🏗️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 5.2, Django REST Framework |
| Database | PostgreSQL |
| Authentication | JWT (SimpleJWT) |
| Payments | Stripe (Test Mode) |
| Admin | Jazzmin |
| Frontend | Vanilla JavaScript, HTML5, CSS3 |
| Filtering | django-filters |

---

## 📁 Project Structure

vendrix/
├── config/              # Django settings, URLs, WSGI
├── users/               # Custom user model, JWT auth
├── products/            # Products, Categories, Colors
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── filters.py
│   └── admin.py
├── orders/              # Cart, Orders, Stripe payments
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── admin.py
├── frontend/            # Vanilla JS frontend
│   ├── index.html       # Product listing
│   ├── cart.html        # Cart + Checkout
│   ├── orders.html      # Order history
│   ├── auth.html        # Login / Register
│   ├── api.js           # API calls
│   └── style.css        # Styles
├── .env.example         # Environment variable template
├── requirements.txt
└── manage.py


---

## ⚙️ Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/your-username/vendrix.git
cd vendrix
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/Scripts/activate   # Windows
source venv/bin/activate        # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
```bash
cp .env.example .env
```
Edit `.env` and fill in your values:
```env
SECRET_KEY=your-secret-key
DB_NAME=vendrix_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
```

### 5. Set up PostgreSQL database
```sql
CREATE DATABASE vendrix_db;
```

### 6. Run migrations
```bash
python manage.py migrate
```

### 7. Create admin user
```bash
python manage.py createsuperuser
```

### 8. Run the server
```bash
python manage.py runserver
```

### 9. Open the frontend
Open `frontend/index.html` in your browser.

---

## 🔑 API Endpoints

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register/` | Register new user |
| POST | `/api/auth/login/` | Login + get JWT tokens |

### Products
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/products/` | List all products |
| GET | `/api/products/?gender=men` | Filter by gender |
| GET | `/api/products/?category=1` | Filter by category |
| GET | `/api/categories/` | List all categories |

### Cart
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/cart/` | View cart |
| POST | `/api/cart/add/` | Add item to cart |
| DELETE | `/api/cart/remove/{id}/` | Remove item |
| DELETE | `/api/cart/clear/` | Clear cart |

### Orders
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/orders/` | My orders |
| POST | `/api/orders/place/` | Place order |
| POST | `/api/orders/create-payment-intent/` | Stripe payment |
| POST | `/api/orders/{id}/cancel/` | Cancel order |

---

## 💳 Stripe Test Cards

| Card Number | Description |
|-------------|-------------|
| `4242 4242 4242 4242` | Payment succeeds |
| `4000 0000 0000 0002` | Payment declined |

Use any future expiry date and any 3-digit CVV.

---

## 🛠️ Environment Variables

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Django secret key |
| `DEBUG` | Debug mode (True/False) |
| `DB_NAME` | PostgreSQL database name |
| `DB_USER` | PostgreSQL username |
| `DB_PASSWORD` | PostgreSQL password |
| `DB_HOST` | Database host |
| `DB_PORT` | Database port |
| `STRIPE_SECRET_KEY` | Stripe secret key (sk_test_...) |
| `STRIPE_PUBLISHABLE_KEY` | Stripe publishable key (pk_test_...) |

---

## 👨‍💻 Author

**Muhammad Sabeeh**
- GitHub: [@your-username](https://github.com/your-username)

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).