from fastapi import FastAPI, Depends, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from models import models
from db.database import engine, get_db
from schemas import schemas
from utils.auth import (
    get_password_hash,
    authenticate_user,
    create_access_token
)
import os
from dotenv import load_dotenv
from starlette.responses import RedirectResponse
from routes import products, sales, vendors

# Cargar variables de entorno desde el archivo .env
load_dotenv()

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Configura Jinja2Templates
templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
templates = Jinja2Templates(directory=templates_dir)

# Configura archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Incluir rutas
app.include_router(products.router, prefix="/productos", tags=["productos"])
app.include_router(sales.router, prefix="/ventas", tags=["ventas"])
app.include_router(vendors.router, prefix="/vendedores", tags=["vendedores"])

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(username=user.username, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/login/")
async def login_post(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = authenticate_user(db, username, password)
    if not user:
        return templates.TemplateResponse("auth/login.html", {"request": request, "error": "Invalid credentials"})
    access_token = create_access_token(data={"sub": user.username})
    response = templates.TemplateResponse("home.html", {"request": request, "username": user.username})
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return response

@app.get("/login/")
def login_form(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})

@app.get("/")
async def home(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/login")
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=400, detail="Invalid credentials")
    except JWTError:
        return RedirectResponse(url="/login")
    
    productos = db.query(models.Producto).all()
    return templates.TemplateResponse("home.html", {"request": request, "productos": productos, "user": username})

@app.get("/register/")
def register_form(request: Request):
    return templates.TemplateResponse("auth/register.html", {"request": request})

@app.post("/register/")
async def register_post(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == username).first()
    if user:
        return templates.TemplateResponse("auth/register.html", {"request": request, "error": "Username already exists"})
    
    hashed_password = get_password_hash(password)
    new_user = models.User(username=username, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return RedirectResponse(url="/login", status_code=303)
