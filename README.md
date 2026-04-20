# Vendrix — E-Commerce Clothing Store

A full-stack e-commerce web app built with Django REST Framework and Vanilla JS.

## Tech Stack
- **Backend:** Python, Django, DRF, PostgreSQL, JWT
- **Frontend:** HTML, CSS, Vanilla JavaScript
- **Admin:** Django Jazzmin

## Features
- JWT Authentication (Register/Login/Logout)
- Product listing with search, category, price, gender filters
- Size selector and quantity controls
- Shopping cart (add, remove, clear)
- Order placement and tracking
- Modern Admin panel

## Setup

### Backend
```bash
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Frontend
```bash
cd frontend
python -m http.server 5500
```

Open `http://127.0.0.1:5500`

## Admin Panel
`http://127.0.0.1:8000/admin/`

## Author
**sabeeh-codes**