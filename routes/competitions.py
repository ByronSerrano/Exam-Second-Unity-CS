from fastapi import APIRouter, Depends, Request, Form, HTTPException
from sqlalchemy.orm import Session
from models import models
from schemas import schemas
from db.database import get_db
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from jose import jwt, JWTError
import os

# Configura Jinja2Templates
templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'templates')
templates = Jinja2Templates(directory=templates_dir)

router = APIRouter()

@router.get("/")
async def lista_competiciones(request: Request, db: Session = Depends(get_db)):
    competiciones = db.query(models.Competition).all()
    return templates.TemplateResponse("competiciones/lista.html", {"request": request, "competiciones": competiciones})

@router.get("/crear")
async def crear_competicion_form(request: Request, db: Session = Depends(get_db)):
    miembros = db.query(models.Members).all()
    return templates.TemplateResponse("competiciones/crear.html", {"request": request, "miembros": miembros})

@router.post("/crear")
async def crear_competicion(request: Request, name: str = Form(...), location: str = Form(...), date: str = Form(...), miembros: list[int] = Form(...), db: Session = Depends(get_db)):
    nueva_competencia = models.Competition(name=name, location=location, date=date)
    db.add(nueva_competencia)
    db.commit()
    db.refresh(nueva_competencia)
    for miembro_id in miembros:
        competencia_miembro = models.CompetitionMember(competition_id=nueva_competencia.id, member_id=miembro_id)
        db.add(competencia_miembro)
    db.commit()
    return templates.TemplateResponse("competiciones/creado.html", {"request": request, "competencia": nueva_competencia})

@router.get("/editar/{competencia_id}")
async def editar_competicion_form(request: Request, competencia_id: int, db: Session = Depends(get_db)):
    competencia = db.query(models.Competition).filter(models.Competition.id == competencia_id).first()
    if competencia is None:
        raise HTTPException(status_code=404, detail="Competencia no encontrada")
    miembros = db.query(models.Members).all()
    return templates.TemplateResponse("competiciones/editar.html", {"request": request, "competencia": competencia, "miembros": miembros})

@router.post("/editar/{competencia_id}")
async def editar_competicion(request: Request, competencia_id: int, name: str = Form(...), location: str = Form(...), date: str = Form(...), miembros: list[int] = Form(...), db: Session = Depends(get_db)):
    competencia = db.query(models.Competition).filter(models.Competition.id == competencia_id).first()
    if competencia is None:
        raise HTTPException(status_code=404, detail="Competencia no encontrada")
    competencia.name = name
    competencia.location = location
    competencia.date = date
    db.commit()

    db.query(models.CompetitionMember).filter(models.CompetitionMember.competition_id == competencia_id).delete()
    for miembro_id in miembros:
        competencia_miembro = models.CompetitionMember(competition_id=competencia.id, member_id=miembro_id)
        db.add(competencia_miembro)
    db.commit()

    return templates.TemplateResponse("competiciones/editado.html", {"request": request, "competencia": competencia})

@router.get("/eliminar/{competencia_id}")
async def eliminar_competicion(request: Request, competencia_id: int, db: Session = Depends(get_db)):
    competencia = db.query(models.Competition).filter(models.Competition.id == competencia_id).first()
    if competencia is None:
        raise HTTPException(status_code=404, detail="Competencia no encontrada")
    db.delete(competencia)
    db.commit()
    return RedirectResponse(url="/competiciones/", status_code=303)
