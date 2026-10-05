def register_user(client):
    response = client.post(
        "/auth/register",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "password123"
        }
    )

    return response


def login_user(client):
    response = client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "password123"
        }
    )

    return response.json()["access_token"]


# 1. Registration
def test_register_user(client):
    response = register_user(client)

    assert response.status_code in [200, 201]


# 2. Login
def test_login(client):
    register_user(client)

    response = login_user(client)

    assert response is not None
    assert isinstance(response, str)


# 3. Invalid login
def test_invalid_login(client):
    register_user(client)

    response = client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "wrongpassword"
        }
    )

    assert response.status_code == 401


# 4. Unauthorized access
def test_unauthorized_cart_access(client):
    response = client.get("/cart/")

    assert response.status_code == 401


# 5. Product listing
def test_product_listing(client, db):
    from app.models import Product

    product = Product(
        name="Python Course",
        price=999
    )

    db.add(product)
    db.commit()

    response = client.get(
        "/products/?page=1&limit=10"
    )

    assert response.status_code == 200

    data = response.json()

    assert "items" in data
    assert "page" in data
    assert "limit" in data
    assert "total" in data
    assert "total_pages" in data


# 6. Add product to cart
def test_add_to_cart(client, db):
    from app.models import Product

    register_user(client)

    token = login_user(client)

    product = Product(
        name="Python Course",
        price=999
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    response = client.post(
        "/cart/items",
        json={
            "product_id": product.id,
            "quantity": 2
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["product_id"] == product.id
    assert data["quantity"] == 2


# 7. Create order
def test_create_order(client, db):
    from app.models import Product

    register_user(client)

    token = login_user(client)

    product = Product(
        name="Python Course",
        price=999
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    client.post(
        "/cart/items",
        json={
            "product_id": product.id,
            "quantity": 2
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    response = client.post(
        "/orders/",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "order_id" in data
    assert data["status"] == "PENDING"
    assert data["total_amount"] == 1998


# 8. Empty cart checkout/order
def test_empty_cart_order(client):
    register_user(client)

    token = login_user(client)

    response = client.post(
        "/orders/",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 400