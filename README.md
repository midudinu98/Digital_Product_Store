# Digital_Product_Store

**A backend REST API for a Digital Product Store built using FastAPI, SQLAlchemy, SQLite/PostgreSQL, JWT Authentication, Stripe, and Pytest.**

**The API provides user authentication, product management, cart management, orders, Stripe payments, admin APIs, reports, validation, and automated tests.**

# Technology Stack
## Backend:

1. FastAPI
2. Python
3. SQLAlchemy
4. PostgreSQL / MySQL / SQLite
5. Pydantic
6. JWT Authentication
7. Pytest

# Project Structure<br>

Digital_Product_Store/<br>
│<br>
├── app/<br>
│   ├── core/<br>
│   │   ├── config.py<br>
│   │   └── database.py<br>
│   │<br>
│   ├── models/<br>
│   │   ├── user.py<br>
│   │   ├── product.py<br>
│   │   ├── cart.py<br>
│   │   ├── order.py<br>
│   │   └── payment.py<br>
│   │   └── __init__.py<br>
│   │<br>
│   ├── schemas/<br>
│   │   ├── auth.py<br>
│   │   ├── product.py<br>
│   │   ├── cart.py<br>
│   │   ├── order.py<br>
│   │   └── security.py<br>
│   │<br>
│   ├── router/<br>
│   │   ├── auth.py<br>
│   │   ├── product.py<br>
│   │   ├── cart.py<br>
│   │   ├── order.py<br>
│   │   ├── payment.py<br>
│   │   └── admin.py<br>
│   │<br>
│   ├── test/<br>
│   │   ├── conftest.py<br>
│   │   └── test_api.py<br>
│   │<br>
│   └── main.py<br>
│<br>
├── .env<br>
├── .env.example<br>
├── .gitignore<br>
├── requirements.txt<br>
└── README.md<br>

# Installation
## 1. Clone or download the project

Open a terminal in the project directory:

**cd Digital_Product_Store**

## 2. Create virtual environment

**python -m venv venv**

## 3. Activate virtual environment

**venv\Scripts\activate**

## 4. Install dependencies

**pip install -r requirements.txt**

# Environment Variables

Create a .env file in the project root.

Example:

**DATABASE_URL=sqlite:///./digital_product_store.db**
**SECRET_KEY=your-secret-key-here**
**ALGORITHM=HS256**
**ACCESS_TOKEN_EXPIRE_MINUTES=60**

**STRIPE_SECRET_KEY=your-stripe-secret-key**
**STRIPE_WEBHOOK_SECRET=your-stripe-webhook-secret**

For submission, use .env.example with placeholder values.

Never commit the real .env file or Stripe secret keys to GitHub.

# Run the Application

Start FastAPI using:

**uvicorn app.main:app --reload**

The API will run at:

**http://127.0.0.1:8000**

# Swagger Documentation

FastAPI automatically provides Swagger documentation.

Open:

**http://127.0.0.1:8000/docs**

Swagger can be used to test the API endpoints.

# Stripe Setup

This project uses Stripe Test Mode.

## Stripe Secret Key

Create a Stripe test account and obtain the test secret key from the Stripe Dashboard.

Add it to **.env:**
**
STRIPE_SECRET_KEY=sk_test_...**

## Stripe Webhook

Start the FastAPI server:

**uvicorn app.main:app --reload**

In another terminal, start Stripe CLI:

**stripe listen --events payment_intent.succeeded,payment_intent.payment_failed,checkout.session.completed --forward-to localhost:8000/payments/webhook**

Stripe CLI will provide a webhook signing secret:

**whsec_...**

Add it to **.env:**
**
STRIPE_WEBHOOK_SECRET=whsec_...**

Do not expose or commit Stripe secret keys.

## Testing Stripe Webhook

With Stripe CLI running, use:

stripe trigger payment_intent.succeeded

The event is forwarded to:

POST /payments/webhook

The webhook is responsible for updating the payment/order status.

# Running Tests

Run all tests:

**python -m pytest -v**

The test database uses SQLite and is separate from the development database.


   
