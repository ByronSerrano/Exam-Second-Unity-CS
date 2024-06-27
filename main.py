from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.templating import Jinja2Templates
from jinja2 import FileSystemLoader
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import os
from typing import List
from datetime import datetime

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


"""
    Rutas para las Ventas
"""
# Rutas para Ventas
@app.get("/ventas/", response_model=List[schemas.Venta])
async def lista_ventas(request: Request, db: Session = Depends(get_db)):
    ventas = db.query(models.Venta).all()
    return templates.TemplateResponse("ventas/lista.html", {"request": request, "ventas": ventas})

@app.get("/ventas/crear")
async def crear_venta_form(request: Request, db: Session = Depends(get_db)):
    productos = db.query(models.Producto).all()
    vendedores = db.query(models.Vendedor).all()
    return templates.TemplateResponse("ventas/crear.html", {"request": request, "productos": productos, "vendedores": vendedores})

@app.post("/ventas/crear", response_model=schemas.Venta)
async def crear_venta(
    request: Request, 
    producto_id: int = Form(...), 
    vendedor_id: int = Form(...), 
    cantidad: int = Form(...), 
    fecha_venta: str = Form(...),
    db: Session = Depends(get_db)
):
    fecha_venta = datetime.strptime(fecha_venta, '%Y-%m-%dT%H:%M')
    nueva_venta = models.Venta(producto_id=producto_id, vendedor_id=vendedor_id, cantidad=cantidad, fecha_venta=fecha_venta)
    db.add(nueva_venta)
    db.commit()
    db.refresh(nueva_venta)
    return templates.TemplateResponse("ventas/creado.html", {"request": request, "venta": nueva_venta})

@app.get("/ventas/editar/{venta_id}")
async def editar_venta_form(request: Request, venta_id: int, db: Session = Depends(get_db)):
    venta = db.query(models.Venta).filter(models.Venta.id == venta_id).first()
    if venta is None:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    productos = db.query(models.Producto).all()
    vendedores = db.query(models.Vendedor).all()
    return templates.TemplateResponse("ventas/editar.html", {"request": request, "venta": venta, "productos": productos, "vendedores": vendedores})

@app.post("/ventas/editar/{venta_id}", response_model=schemas.Venta)
async def editar_venta(
    request: Request, 
    venta_id: int, 
    producto_id: int = Form(...), 
    vendedor_id: int = Form(...), 
    cantidad: int = Form(...), 
    fecha_venta: str = Form(...),
    db: Session = Depends(get_db)
):
    venta = db.query(models.Venta).filter(models.Venta.id == venta_id).first()
    if venta is None:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    fecha_venta = datetime.strptime(fecha_venta, '%Y-%m-%dT%H:%M')
    venta.producto_id = producto_id
    venta.vendedor_id = vendedor_id
    venta.cantidad = cantidad
    venta.fecha_venta = fecha_venta
    db.commit()
    db.refresh(venta)
    return templates.TemplateResponse("ventas/editado.html", {"request": request, "venta": venta})

@app.delete("/ventas/{venta_id}", response_model=schemas.Venta)
def eliminar_venta(venta_id: int, db: Session = Depends(get_db)):
    venta = db.query(models.Venta).filter(models.Venta.id == venta_id).first()
    if venta is None:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    db.delete(venta)
    db.commit()
    return {"message": "Venta eliminada"}