from fastapi import APIRouter, Depends, Request, Form, HTTPException
from sqlalchemy.orm import Session
from models import models
from schemas import schemas
from db.database import get_db
from fastapi.templating import Jinja2Templates
import os

# Configura Jinja2Templates para buscar en el directorio principal de 'templates'
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'templates'))

router = APIRouter()

@router.get("/")
async def lista_productos(request: Request, db: Session = Depends(get_db)):
    productos = db.query(models.Producto).all()
    return templates.TemplateResponse("productos/lista.html", {"request": request, "productos": productos})

@router.get("/crear")
async def crear_producto_form(request: Request):
    return templates.TemplateResponse("productos/crear.html", {"request": request})

@router.post("/crear")
async def crear_producto(request: Request, nombre: str = Form(...), precio: float = Form(...), stock: int = Form(...), db: Session = Depends(get_db)):
    nuevo_producto = models.Producto(nombre=nombre, precio=precio, stock=stock)
    db.add(nuevo_producto)
    db.commit()
    db.refresh(nuevo_producto)
    return templates.TemplateResponse("productos/creado.html", {"request": request, "producto": nuevo_producto})

@router.get("/editar/{producto_id}")
async def editar_producto_form(request: Request, producto_id: int, db: Session = Depends(get_db)):
    producto = db.query(models.Producto).filter(models.Producto.id == producto_id).first()
    if producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return templates.TemplateResponse("productos/editar.html", {"request": request, "producto": producto})

@router.post("/editar/{producto_id}")
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
