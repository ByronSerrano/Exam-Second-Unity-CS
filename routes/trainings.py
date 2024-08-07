from fastapi import APIRouter, Depends, Request, Form, HTTPException
from sqlalchemy.orm import Session
from models import models
from schemas import schemas
from db.database import get_db
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
import os
from datetime import datetime

# Configura Jinja2Templates
templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'templates')
templates = Jinja2Templates(directory=templates_dir)

router = APIRouter()

@router.get("/")
async def lista_entrenamientos(request: Request, db: Session = Depends(get_db)):
    entrenamientos = db.query(models.Training).all()
    return templates.TemplateResponse("entrenamientos/lista.html", {"request": request, "entrenamientos": entrenamientos})

@router.get("/crear")
async def crear_entrenamiento_form(request: Request, db: Session = Depends(get_db)):
    miembros = db.query(models.Members).all()
    return templates.TemplateResponse("entrenamientos/crear.html", {"request": request, "miembros": miembros})

@router.post("/crear")
async def crear_entrenamiento(request: Request, title: str = Form(...), description: str = Form(...), date: str = Form(...), miembros: list[int] = Form(...), db: Session = Depends(get_db)):
    entrenamiento = models.Training(title=title, description=description, date=datetime.strptime(date, '%Y-%m-%d %H:%M:%S'))
    entrenamiento.members = db.query(models.Members).filter(models.Members.id.in_(miembros)).all()
    db.add(entrenamiento)
    db.commit()
    db.refresh(entrenamiento)
    return templates.TemplateResponse("entrenamientos/creado.html", {"request": request, "entrenamiento": entrenamiento})

@router.get("/editar/{entrenamiento_id}")
async def editar_entrenamiento_form(request: Request, entrenamiento_id: int, db: Session = Depends(get_db)):
    entrenamiento = db.query(models.Training).filter(models.Training.id == entrenamiento_id).first()
    miembros = db.query(models.Members).all()
    if entrenamiento is None:
        raise HTTPException(status_code=404, detail="Entrenamiento no encontrado")
    return templates.TemplateResponse("entrenamientos/editar.html", {"request": request, "entrenamiento": entrenamiento, "miembros": miembros})

@router.post("/editar/{entrenamiento_id}")
async def editar_entrenamiento(request: Request, entrenamiento_id: int, title: str = Form(...), description: str = Form(...), date: str = Form(...), miembros: list[int] = Form(...), db: Session = Depends(get_db)):
    entrenamiento = db.query(models.Training).filter(models.Training.id == entrenamiento_id).first()
    if entrenamiento is None:
        raise HTTPException(status_code=404, detail="Entrenamiento no encontrado")
    entrenamiento.title = title
    entrenamiento.description = description
    entrenamiento.date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
    entrenamiento.members = db.query(models.Members).filter(models.Members.id.in_(miembros)).all()
    db.commit()
    db.refresh(entrenamiento)
    return templates.TemplateResponse("entrenamientos/editado.html", {"request": request, "entrenamiento": entrenamiento})

@router.post("/eliminar/{entrenamiento_id}")
async def eliminar_entrenamiento(request: Request, entrenamiento_id: int, db: Session = Depends(get_db)):
    entrenamiento = db.query(models.Training).filter(models.Training.id == entrenamiento_id).first()
    if entrenamiento is None:
        raise HTTPException(status_code=404, detail="Entrenamiento no encontrado")
    db.delete(entrenamiento)
    db.commit()
    return RedirectResponse(url="/entrenamientos", status_code=303)
