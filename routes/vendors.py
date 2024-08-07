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
async def lista_vendedores(request: Request, db: Session = Depends(get_db)):
    vendedores = db.query(models.Vendedor).all()
    return templates.TemplateResponse("vendedores/lista.html", {"request": request, "vendedores": vendedores})

@router.get("/crear")
async def crear_vendedor_form(request: Request):
    return templates.TemplateResponse("vendedores/crear.html", {"request": request})

@router.post("/crear")
async def crear_vendedor(request: Request, nombre: str = Form(...), region: str = Form(...), db: Session = Depends(get_db)):
    nuevo_vendedor = models.Vendedor(nombre=nombre, region=region)
    db.add(nuevo_vendedor)
    db.commit()
    db.refresh(nuevo_vendedor)
    return templates.TemplateResponse("vendedores/creado.html", {"request": request, "vendedor": nuevo_vendedor})

@router.get("/editar/{vendedor_id}")
async def editar_vendedor_form(request: Request, vendedor_id: int, db: Session = Depends(get_db)):
    vendedor = db.query(models.Vendedor).filter(models.Vendedor.id == vendedor_id).first()
    if vendedor is None:
        raise HTTPException(status_code=404, detail="Vendedor no encontrado")
    return templates.TemplateResponse("vendedores/editar.html", {"request": request, "vendedor": vendedor})

@router.post("/editar/{vendedor_id}")
async def editar_vendedor(request: Request, vendedor_id: int, nombre: str = Form(...), region: str = Form(...), db: Session = Depends(get_db)):
    vendedor = db.query(models.Vendedor).filter(models.Vendedor.id == vendedor_id).first()
    if vendedor is None:
        raise HTTPException(status_code=404, detail="Vendedor no encontrado")
    vendedor.nombre = nombre
    vendedor.region = region
    db.commit()
    db.refresh(vendedor)
    return templates.TemplateResponse("vendedores/editado.html", {"request": request, "vendedor": vendedor})
