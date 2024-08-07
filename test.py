import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from db.database import get_db, Base
from models import models

# Configura la base de datos de pruebas
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"  # Usamos SQLite para pruebas
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

# Sobrescribe la dependencia de la base de datos
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# Datos de prueba
test_user = {"username": "admin", "password": "admin"}

@pytest.fixture(scope="module")
def create_test_user():
    response = client.post("/register/", data=test_user)
    assert response.status_code == 303

def test_login(create_test_user):
    response = client.post("/login/", data=test_user)
    assert response.status_code == 200
    assert "access_token" in response.cookies

def test_register():
    new_user = {"username": "testuser", "password": "testpass"}
    response = client.post("/register/", data=new_user)
    assert response.status_code == 303  # Redirección después del registro

def test_login_invalid_user():
    response = client.post("/login/", data={"username": "invalid", "password": "invalid"})
    assert response.status_code == 200
    assert "error" in response.text

def test_login_invalid_password():
    response = client.post("/login/", data={"username": "admin", "password": "wrongpass"})
    assert response.status_code == 200
    assert "error" in response.text

# Pruebas para miembros
def test_create_member():
    response = client.post("/miembros/crear", data={"nombre": "John Doe", "edad": 30})
    assert response.status_code == 200
    assert "Miembro creado" in response.text

def test_edit_member():
    response = client.post("/miembros/editar/1", data={"nombre": "John Smith", "edad": 31})
    assert response.status_code == 200
    assert "Miembro editado" in response.text

# Pruebas para entrenamientos
def test_create_training():
    response = client.post("/entrenamientos/crear", data={
        "title": "Training 1",
        "description": "Description 1",
        "date": "2023-08-01",
        "miembros": [1]  # Asegúrate de que el miembro con ID 1 existe
    })
    assert response.status_code == 200
    assert "Entrenamiento creado" in response.text

def test_edit_training():
    response = client.post("/entrenamientos/editar/1", data={
        "title": "Training 1 Updated",
        "description": "Description 1 Updated",
        "date": "2023-08-02",
        "miembros": [1]  # Asegúrate de que el miembro con ID 1 existe
    })
    assert response.status_code == 200
    assert "Entrenamiento editado" in response.text

# Pruebas para competiciones
def test_create_competition():
    response = client.post("/competiciones/crear", data={
        "name": "Competition 1",
        "location": "Location 1",
        "date": "2023-08-01",
        "miembros": [1]  # Asegúrate de que el miembro con ID 1 existe
    })
    assert response.status_code == 200
    assert "Competencia creada" in response.text

def test_edit_competition():
    response = client.post("/competiciones/editar/1", data={
        "name": "Competition 1 Updated",
        "location": "Location 1 Updated",
        "date": "2023-08-02",
        "miembros": [1]  # Asegúrate de que el miembro con ID 1 existe
    })
    assert response.status_code == 200
    assert "Competencia editada" in response.text

if __name__ == "__main__":
    pytest.main()
