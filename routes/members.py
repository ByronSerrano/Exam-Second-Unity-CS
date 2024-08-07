from fastapi import APIRouter, Depends, Request, Form, HTTPException
from sqlalchemy.orm import Session
from models import models
from schemas import schemas
from db.database import get_db
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
import os

# Configura Jinja2Templates
templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'templates')
templates = Jinja2Templates(directory=templates_dir)

router = APIRouter()

@router.get("/")
async def lista_miembros(request: Request, db: Session = Depends(get_db)):
    miembros = db.query(models.Members).all()
    return templates.TemplateResponse("miembros/lista.html", {"request": request, "miembros": miembros})

@router.get("/crear")
async def crear_miembro_form(request: Request):
    return templates.TemplateResponse("miembros/crear.html", {"request": request})

@router.post("/crear")
async def crear_miembro(request: Request, nombre: str = Form(...), edad: int = Form(...), db: Session = Depends(get_db)):
    nuevo_miembro = models.Members(nombre=nombre, edad=edad)
    db.add(nuevo_miembro)
    db.commit()
    db.refresh(nuevo_miembro)
    return templates.TemplateResponse("miembros/creado.html", {"request": request, "miembro": nuevo_miembro})

@router.get("/editar/{miembro_id}")
async def editar_miembro_form(request: Request, miembro_id: int, db: Session = Depends(get_db)):
    miembro = db.query(models.Members).filter(models.Members.id == miembro_id).first()
    if miembro is None:
        raise HTTPException(status_code=404, detail="Miembro no encontrado")
    return templates.TemplateResponse("miembros/editar.html", {"request": request, "miembro": miembro})

@router.post("/editar/{miembro_id}")
async def editar_miembro(request: Request, miembro_id: int, nombre: str = Form(...), edad: int = Form(...), db: Session = Depends(get_db)):
    miembro = db.query(models.Members).filter(models.Members.id == miembro_id).first()
    if miembro is None:
        raise HTTPException(status_code=404, detail="Miembro no encontrado")
    miembro.nombre = nombre
    miembro.edad = edad
    db.commit()
    db.refresh(miembro)
    return templates.TemplateResponse("miembros/editado.html", {"request": request, "miembro": miembro})

@router.post("/eliminar/{miembro_id}")
async def eliminar_miembro(request: Request, miembro_id: int, db: Session = Depends(get_db)):
    miembro = db.query(models.Members).filter(models.Members.id == miembro_id).first()
    if miembro is None:
        raise HTTPException(status_code=404, detail="Miembro no encontrado")
    db.delete(miembro)
    db.commit()
    return RedirectResponse(url="/miembros", status_code=303)
