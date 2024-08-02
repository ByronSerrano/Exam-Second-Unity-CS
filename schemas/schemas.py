from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class CalificacionBase(BaseModel):
    estrellas: int
    reseña: str
    fecha: datetime
    articulo_id: int
    usuario_id: int

class CalificacionCreate(CalificacionBase):
    pass

class Calificacion(CalificacionBase):
    id: int

    class Config:
        orm_mode = True

class ArticuloBase(BaseModel):
    nombre: str
    descripcion: str
    promedio_calificaciones: float

class ArticuloCreate(ArticuloBase):
    pass

class Articulo(ArticuloBase):
    id: int
    calificaciones: List[Calificacion] = []

    class Config:
        orm_mode = True

class UsuarioBase(BaseModel):
    nombre: str

class UsuarioCreate(UsuarioBase):
    pass

class Usuario(UsuarioBase):
    id: int
    calificaciones: List[Calificacion] = []

    class Config:
        orm_mode = True
