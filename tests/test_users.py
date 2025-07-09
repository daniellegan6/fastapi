from app import schemas
import pytest
from jose import jwt
from app.config import settings

# def test_root(client):
#     response = client.get("/")
#     assert response.json().get("message") == "This is my first API!!!"
#     assert response.status_code == 200

def test_create_user(client):
    response = client.post("/users/",json={"email":"test3@gmail.com", "password":"123"})
    
    new_user = schemas.UserResponse(**response.json())
    assert new_user.email == "test3@gmail.com"
    assert response.status_code == 201

def test_login_user(client, test_user):
    response = client.post("/login",data={"username": test_user["email"], "password":test_user["password"]})
    login_response = schemas.Token(**response.json())
    payload = jwt.decode(login_response.access_token, settings.secret_key, algorithms=[settings.algorithm])
    id = payload.get("user_id")
    assert id == test_user["id"]
    assert login_response.token_type == "bearer"
    assert response.status_code == 200

@pytest.mark.parametrize("email, password, status_code", [
    ("wrongemail@gmail.com", "123", 403),
    ("test3@gmail.com", "wrong_password", 403),
    ("wrongemail@gmail.com", "wrong_password", 403),
    ("test3@gmail.com", None, 403),
    (None, "123", 403)
])      
def test_incorrect_login(client, test_user, email, password, status_code):
    res = client.post("/login", data={"username": email, "password": password})

    assert res.status_code == status_code
    assert res.json().get("detail") == "Invalid Credentials"