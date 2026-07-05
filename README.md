# FastAPI Boilerplate Service

A production-ready FastAPI boilerplate with authentication, blog, and eCommerce modules.

## Tech Stack

- **FastAPI** — Web framework
- **SQLAlchemy** — ORM
- **MySQL/MariaDB** — Database
- **PyMySQL** — Database driver
- **JWT** — Token-based authentication (python-jose)
- **Passlib + bcrypt** — Password hashing
- **Pydantic** — Request/response validation

## Project Structure

```
app/
├── core/               # Config, database, security, dependencies
│   ├── config.py          Environment variables
│   ├── database.py        SQLAlchemy engine & session
│   ├── security.py        Password hashing & JWT helpers
│   └── dependencies.py    Auth dependencies (get_current_user, get_optional_user)
├── models/             # SQLAlchemy ORM models
│   ├── user.py
│   ├── refresh_token.py
│   ├── blog.py
│   ├── category.py
│   ├── product.py
│   ├── cart.py
│   ├── cart_item.py
│   ├── order.py
│   └── order_item.py
├── schemas/            # Pydantic request/response models
│   ├── user.py
│   ├── blog.py
│   ├── category.py
│   ├── product.py
│   ├── cart.py
│   ├── order.py
│   └── common.py          PaginatedResponse generic
├── repositories/       # Data access layer
│   ├── blog_repository.py
│   ├── category_repository.py
│   ├── product_repository.py
│   ├── cart_repository.py
│   └── order_repository.py
├── services/           # Business logic layer
│   ├── auth_service.py
│   ├── blog_service.py
│   ├── category_service.py
│   ├── product_service.py
│   ├── cart_service.py
│   └── order_service.py
├── routers/            # API route handlers
│   ├── auth.py
│   ├── blogs.py
│   ├── categories.py
│   ├── products.py
│   ├── cart.py
│   └── orders.py
└── main.py             # FastAPI app entry point
```

## Environment Variables

Copy `.env` and configure:

```env
DB_HOST=localhost
DB_PORT=3307
DB_DATABASE=your_db
DB_USERNAME=root
DB_PASSWORD=

SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

## Installation

```bash
pip install -r requirements.txt
```

If there's no `requirements.txt`, install manually:

```bash
pip install fastapi uvicorn sqlalchemy pymysql python-jose[cryptography] passlib[bcrypt] bcrypt python-dotenv python-multipart pydantic[email]
```

## Run

```bash
uvicorn app.main:app --reload
```

Server starts at `http://localhost:8809` (configurable in `main.py`).

## API Documentation

Once running, visit:

- Swagger UI: `http://localhost:8809/docs`
- ReDoc: `http://localhost:8809/redoc`

---

## Authentication

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/auth/register` | — | Register a new user |
| POST | `/auth/login` | — | Login, returns access + refresh tokens |
| POST | `/auth/signup` | — | Alias for register |
| POST | `/auth/signin` | — | Alias for login |
| GET | `/auth/me` | Bearer | Current user profile |
| POST | `/auth/refresh` | — | Refresh access token |
| POST | `/auth/signout` | — | Returns logout message |

**Roles**: `is_admin` field on User — default is `False`. Set to `True` directly in the database for admin access.

---

## Blog

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/blogs` | Required | Create blog (authenticated user becomes owner) |
| GET | `/blogs` | Optional | List blogs (active only for non-admins) |
| GET | `/blogs/{id}` | Optional | Get blog detail |
| PUT | `/blogs/{id}` | Required | Update blog (owner or admin) |
| PATCH | `/blogs/{id}/deactivate` | Required | Admin only |
| PATCH | `/blogs/{id}/activate` | Required | Admin only |

---

## Categories

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/categories` | Required | Admin only |
| GET | `/categories` | Optional | List active categories |
| GET | `/categories/{id}` | Optional | Get category |
| PUT | `/categories/{id}` | Required | Admin only |
| PATCH | `/categories/{id}/activate` | Required | Admin only |
| PATCH | `/categories/{id}/deactivate` | Required | Admin only |

---

## Products

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/products` | Required | Admin only |
| GET | `/products` | Optional | Paginated list; supports `?search=&category_id=&page=&per_page=` |
| GET | `/products/{id}` | Optional | Get product |
| PUT | `/products/{id}` | Required | Admin only |
| PATCH | `/products/{id}/activate` | Required | Admin only |
| PATCH | `/products/{id}/deactivate` | Required | Admin only |

---

## Cart

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/cart` | Required | View own cart |
| POST | `/cart/items` | Required | Add item (`product_id`, `quantity`) |
| PUT | `/cart/items/{id}` | Required | Update item quantity |
| DELETE | `/cart/items/{id}` | Required | Remove item |
| DELETE | `/cart` | Required | Clear entire cart |

---

## Orders

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/orders` | Required | Place order (from own cart) |
| GET | `/orders` | Required | Own orders; Admin sees all |
| GET | `/orders/{id}` | Required | Owner or Admin |
| PATCH | `/orders/{id}/status` | Required | Admin only; valid statuses: `pending`, `paid`, `processing`, `shipped`, `delivered`, `cancelled` |

---

## Business Rules

### Stock & Cart
- Cannot add inactive products to cart
- Quantity cannot exceed available stock
- Placing an order decrements stock atomically

### Order Lifecycle
1. Cart items are validated for availability and stock
2. Order is created with `pending` status
3. OrderItems are created with snapshot of unit prices
4. Stock is reduced
5. Cart is cleared

### Ownership & Permissions
- **Admin** (`is_admin=True`): full access to categories, products, and all orders
- **Customer** (`is_admin=False`): manages own cart and orders
- **Blog**: owner or admin can update; admin-only status toggle
