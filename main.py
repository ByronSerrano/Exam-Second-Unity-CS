from fastapi import FastAPI, Depends, HTTPException, Request, Form, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
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

app = FastAPI()

# Configura archivos estáticos (CSS, JS, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Manejador de WebSockets para actualizar calificaciones en tiempo real
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# Ruta para la página principal
@app.get("/")
async def home(request: Request, db: Session = Depends(get_db)):
    articulos = db.query(models.Articulo).all()
    return templates.TemplateResponse("home.html", {"request": request, "articulos": articulos})

# Rutas para los Artículos
@app.get("/articulos/")
async def lista_articulos(request: Request, db: Session = Depends(get_db)):
    articulos = db.query(models.Articulo).all()
    return templates.TemplateResponse("articulos/lista.html", {"request": request, "articulos": articulos})

@app.get("/articulos/{articulo_id}")
async def ver_articulo(request: Request, articulo_id: int, db: Session = Depends(get_db)):
    articulo = db.query(models.Articulo).filter(models.Articulo.id == articulo_id).first()
    if articulo is None:
        raise HTTPException(status_code=404, detail="Artículo no encontrado")
    return templates.TemplateResponse("articulos/detalle.html", {"request": request, "articulo": articulo})

# Rutas para las Calificaciones y Reseñas
@app.post("/calificaciones/")
async def calificar_articulo(request: Request, articulo_id: int = Form(...), usuario_id: int = Form(...), estrellas: int = Form(...), reseña: str = Form(...), db: Session = Depends(get_db)):
    try:
        nueva_calificacion = models.Calificacion(articulo_id=articulo_id, usuario_id=usuario_id, estrellas=estrellas, reseña=reseña, fecha=datetime.now())
        db.add(nueva_calificacion)
        db.commit()
        db.refresh(nueva_calificacion)

        # Actualizar promedio de calificaciones del artículo
        calificaciones = db.query(models.Calificacion).filter(models.Calificacion.articulo_id == articulo_id).all()
        if calificaciones:
            promedio = sum([calificacion.estrellas for calificacion in calificaciones]) / len(calificaciones)
        else:
            promedio = 0.0  # Puede ser 0.0 o None dependiendo de cómo quieras manejarlo
        articulo = db.query(models.Articulo).filter(models.Articulo.id == articulo_id).first()
        articulo.promedio_calificaciones = promedio
        db.commit()

        # Notificar a todos los clientes conectados
        if promedio is not None:
            await manager.broadcast(f"El artículo {articulo_id} tiene un nuevo promedio de calificaciones: {promedio:.2f}")
        else:
            await manager.broadcast(f"El artículo {articulo_id} aún no tiene calificaciones")

        return templates.TemplateResponse("calificaciones/creada.html", {"request": request, "calificacion": nueva_calificacion})
    except IntegrityError:
        db.rollback()
        return templates.TemplateResponse("calificaciones/error.html", {"request": request, "detail": "El usuario ya ha calificado este artículo"})


@app.websocket("/ws/calificaciones/")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Inicia la aplicación
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
