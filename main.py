from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.templating import Jinja2Templates
from jinja2 import FileSystemLoader
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import os
from typing import List

from db.database import engine, get_db
from schemas import schemas
from models import models

models.Base.metadata.create_all(bind=engine)

# Obtén la ruta absoluta del directorio 'templates'
templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

# Configura Jinja2Templates con un FileSystemLoader personalizado
templates = Jinja2Templates(directory=templates_dir)
templates.env.loader = FileSystemLoader(templates_dir)

app = FastAPI()

# Configura archivos estáticos (CSS, JS, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")


# Ruta para la página principal
@app.get("/")
async def home(request: Request, db: Session = Depends(get_db)):
    productos = db.query(models.Producto).all()
    return templates.TemplateResponse("home.html", {"request": request, "productos": productos})

# Rutas para los Productos
@app.get("/productos/")
async def lista_productos(request: Request, db: Session = Depends(get_db)):
    productos = db.query(models.Producto).all()
    return templates.TemplateResponse("productos/lista.html", {"request": request, "productos": productos})

@app.get("/productos/crear")
async def crear_producto_form(request: Request):
    return templates.TemplateResponse("productos/crear.html", {"request": request})

@app.post("/productos/crear")
async def crear_producto(request: Request, nombre: str = Form(...), precio: float = Form(...), stock: int = Form(...), db: Session = Depends(get_db)):
    nuevo_producto = models.Producto(nombre=nombre, precio=precio, stock=stock)
    db.add(nuevo_producto)
    db.commit()
    db.refresh(nuevo_producto)
    return templates.TemplateResponse("productos/creado.html", {"request": request, "producto": nuevo_producto})

@app.get("/productos/editar/{producto_id}")
async def editar_producto_form(request: Request, producto_id: int, db: Session = Depends(get_db)):
    producto = db.query(models.Producto).filter(models.Producto.id == producto_id).first()
    if producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return templates.TemplateResponse("productos/editar.html", {"request": request, "producto": producto})

@app.post("/productos/editar/{producto_id}")
async def editar_producto(request: Request, producto_id: int, nombre: str = Form(...), precio: float = Form(...), stock: int = Form(...), db: Session = Depends(get_db)):
    producto = db.query(models.Producto).filter(models.Producto.id == producto_id).first()
    if producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    producto.nombre = nombre
    producto.precio = precio
    producto.stock = stock
    db.commit()
    db.refresh(producto)
    return templates.TemplateResponse("productos/editado.html", {"request": request, "producto": producto})
