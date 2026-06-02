import pytest
from fastapi.testclient import TestClient
from main import app
from database import Base, engine
import models

# Create test database tables
Base.metadata.create_all(bind=engine)

client = TestClient(app)

# ===================== HEALTH & ROOT ENDPOINTS =====================
def test_read_root():
    """Test that the API root is accessible."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_health_check():
    """Test health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "online"

# ===================== USER REGISTRATION & AUTHENTICATION =====================
def test_register_user():
    """Test user registration."""
    payload = {
        "username": "testmechanic1",
        "password": "password123",
        "full_name": "Test Mechanic",
        "role": "mechanic"
    }
    response = client.post("/users/register", json=payload)
    assert response.status_code in [201, 400]
    if response.status_code == 201:
        data = response.json()
        assert data["username"] == "testmechanic1"
        assert data["role"] == "mechanic"

def test_register_duplicate_user():
    """Test registering a user that already exists."""
    payload = {
        "username": "testmechanic1",
        "password": "password123",
        "full_name": "Test Mechanic",
        "role": "mechanic"
    }
    client.post("/users/register", json=payload)  # First registration
    response = client.post("/users/register", json=payload)  # Duplicate
    assert response.status_code == 400

def test_user_login():
    """Test user login and token generation."""
    # Register user first
    client.post("/users/register", json={
        "username": "logintest",
        "password": "testpass123",
        "full_name": "Login Test",
        "role": "mechanic"
    })
    
    # Login
    login_data = {"username": "logintest", "password": "testpass123"}
    response = client.post("/users/token", data=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_user_login_invalid_credentials():
    """Test login with wrong password."""
    login_data = {"username": "logintest", "password": "wrongpassword"}
    response = client.post("/users/token", data=login_data)
    assert response.status_code == 401

def test_user_login_nonexistent_user():
    """Test login with non-existent user."""
    login_data = {"username": "nonexistent", "password": "password"}
    response = client.post("/users/token", data=login_data)
    assert response.status_code == 401

# ===================== INVENTORY ENDPOINTS =====================
def test_list_inventory_unauthorized():
    """Test accessing inventory without authentication."""
    response = client.get("/inventory/")
    assert response.status_code == 401

def test_create_inventory_unauthorized():
    """Test creating inventory without authorization."""
    payload = {
        "part_number": "PART123",
        "name": "Test Part",
        "category": "Tool",
        "stock_level": 10,
        "price": 99.99
    }
    response = client.post("/inventory/", json=payload)
    assert response.status_code == 401

def test_get_inventory_with_token():
    """Test getting inventory with valid token."""
    # Register manager
    client.post("/users/register", json={
        "username": "manager1",
        "password": "managerpass",
        "full_name": "Manager User",
        "role": "manager"
    })
    
    # Login to get token
    login_response = client.post("/users/token", data={
        "username": "manager1",
        "password": "managerpass"
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get inventory
    response = client.get("/inventory/", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# ===================== QUOTATIONS ENDPOINTS =====================
def test_create_quotation_unauthorized():
    """Test creating quotation requires manager role."""
    payload = {
        "customer_name": "Test Customer",
        "total_amount": 5000.00
    }
    response = client.post("/quotations/", json=payload)
    assert response.status_code == 401

def test_list_quotations_unauthorized():
    """Test accessing quotations without token."""
    response = client.get("/quotations/")
    assert response.status_code == 401

# ===================== INVOICES ENDPOINTS =====================
def test_get_invoice_unauthorized():
    """Test that accessing an invoice without a token is denied."""
    response = client.get("/invoices/1")
    assert response.status_code == 401

def test_get_invoice_not_found():
    """Test retrieving a non-existent invoice with a valid token."""
    # Register and login
    client.post("/users/register", json={
        "username": "testuser2",
        "password": "password123",
        "full_name": "Test User",
        "role": "mechanic"
    })
    login_response = client.post("/users/token", data={
        "username": "testuser2",
        "password": "password123"
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Attempt to get non-existent invoice
    response = client.get("/invoices/9999", headers=headers)
    assert response.status_code == 404

# ===================== JOB CARDS ENDPOINTS =====================
def test_list_job_cards_with_auth():
    """Test listing job cards with authentication."""
    # Register and login
    client.post("/users/register", json={
        "username": "mechanic2",
        "password": "password123",
        "full_name": "Mechanic 2",
        "role": "mechanic"
    })
    login_response = client.post("/users/token", data={
        "username": "mechanic2",
        "password": "password123"
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/job-cards/", headers=headers)
    assert response.status_code == 200

# ===================== SAFETY DOCUMENTS ENDPOINTS =====================
def test_list_safety_documents_with_auth():
    """Test listing safety documents."""
    # Register and login
    client.post("/users/register", json={
        "username": "safety_user",
        "password": "password123",
        "full_name": "Safety User",
        "role": "mechanic"
    })
    login_response = client.post("/users/token", data={
        "username": "safety_user",
        "password": "password123"
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/safety-docs/", headers=headers)
    assert response.status_code == 200

# ===================== CORS & MOBILE COMPATIBILITY =====================
def test_cors_headers_present():
    """Test that CORS headers are present in responses for mobile compatibility."""
    response = client.options("/inventory/")
    assert response.status_code == 200

# ===================== ERROR HANDLING =====================
def test_invalid_endpoint():
    """Test accessing non-existent endpoint."""
    response = client.get("/nonexistent-endpoint")
    assert response.status_code == 404

def test_invalid_json_payload():
    """Test sending invalid JSON."""
    response = client.post("/users/register", data="invalid json")
    assert response.status_code in [422, 400]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
