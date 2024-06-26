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


"""
    Rutas para lo Productos
"""
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


"""
    Rutas para las Ventas
"""
@app.get("/vendedores/", response_model=List[schemas.Vendedor])
async def lista_vendedores(request: Request, db: Session = Depends(get_db)):
    vendedores = db.query(models.Vendedor).all()
    return templates.TemplateResponse("vendedores/lista.html", {"request": request, "vendedores": vendedores})

@app.get("/vendedores/crear")
async def crear_vendedor_form(request: Request):
    return templates.TemplateResponse("vendedores/crear.html", {"request": request})

@app.post("/vendedores/crear", response_model=schemas.Vendedor)
async def crear_vendedor(request: Request, nombre: str = Form(...), region: str = Form(...), db: Session = Depends(get_db)):
    nuevo_vendedor = models.Vendedor(nombre=nombre, region=region)
    db.add(nuevo_vendedor)
    db.commit()
    db.refresh(nuevo_vendedor)
    return templates.TemplateResponse("vendedores/creado.html", {"request": request, "vendedor": nuevo_vendedor})

@app.get("/vendedores/editar/{vendedor_id}")
async def editar_vendedor_form(request: Request, vendedor_id: int, db: Session = Depends(get_db)):
    vendedor = db.query(models.Vendedor).filter(models.Vendedor.id == vendedor_id).first()
    if vendedor is None:
        raise HTTPException(status_code=404, detail="Vendedor no encontrado")
    return templates.TemplateResponse("vendedores/editar.html", {"request": request, "vendedor": vendedor})

@app.post("/vendedores/editar/{vendedor_id}", response_model=schemas.Vendedor)
async def editar_vendedor(request: Request, vendedor_id: int, nombre: str = Form(...), region: str = Form(...), db: Session = Depends(get_db)):
    vendedor = db.query(models.Vendedor).filter(models.Vendedor.id == vendedor_id).first()
    if vendedor is None:
        raise HTTPException(status_code=404, detail="Vendedor no encontrado")
    vendedor.nombre = nombre
    vendedor.region = region
    db.commit()
    db.refresh(vendedor)
    return templates.TemplateResponse("vendedores/editado.html", {"request": request, "vendedor": vendedor})

@app.delete("/vendedores/{vendedor_id}", response_model=schemas.Vendedor)
def eliminar_vendedor(vendedor_id: int, db: Session = Depends(get_db)):
    vendedor = db.query(models.Vendedor).filter(models.Vendedor.id == vendedor_id).first()
    if vendedor is None:
        raise HTTPException(status_code=404, detail="Vendedor no encontrado")
    db.delete(vendedor)
    db.commit()
    return {"message": "Vendedor eliminado"}
