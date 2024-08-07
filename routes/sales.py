from fastapi import APIRouter, Depends, Request, Form, HTTPException
from sqlalchemy.orm import Session
from models import models
from db.database import get_db
from fastapi.templating import Jinja2Templates
import os

# Configura Jinja2Templates para buscar en el directorio principal de 'templates'
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'templates'))

router = APIRouter()

@router.get("/")
async def lista_ventas(request: Request, db: Session = Depends(get_db)):
    ventas = db.query(models.Venta).all()
    return templates.TemplateResponse("ventas/lista.html", {"request": request, "ventas": ventas})

@router.get("/crear")
async def crear_venta_form(request: Request, db: Session = Depends(get_db)):
    productos = db.query(models.Producto).all()
    vendedores = db.query(models.Vendedor).all()
    return templates.TemplateResponse("ventas/crear.html", {"request": request, "productos": productos, "vendedores": vendedores})

@router.post("/crear")
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

@router.get("/editar/{venta_id}")
async def editar_venta_form(request: Request, venta_id: int, db: Session = Depends(get_db)):
    venta = db.query(models.Venta).filter(models.Venta.id == venta_id).first()
    if venta is None:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    productos = db.query(models.Producto).all()
    vendedores = db.query(models.Vendedor).all()
    return templates.TemplateResponse("ventas/editar.html", {"request": request, "venta": venta, "productos": productos, "vendedores": vendedores})

@router.post("/editar/{venta_id}")
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

@router.delete("/{venta_id}")
async def eliminar_venta(venta_id: int, db: Session = Depends(get_db)):
    venta = db.query(models.Venta).filter(models.Venta.id == venta_id).first()
    if venta is None:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    db.delete(venta)
    db.commit()
    return {"message": "Venta eliminada"}
