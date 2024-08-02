from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from db.database import Base

class Articulo(Base):
    __tablename__ = "articulos"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True, nullable=False)
    descripcion = Column(String)
    promedio_calificaciones = Column(Float, nullable=True)  # Permitir NULL en promedio_calificaciones
    calificaciones = relationship("Calificacion", back_populates="articulo")

class Calificacion(Base):
    __tablename__ = "calificaciones"
    id = Column(Integer, primary_key=True, index=True)
    estrellas = Column(Integer)
    reseña = Column(String)
    fecha = Column(DateTime)
    articulo_id = Column(Integer, ForeignKey("articulos.id"))
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    articulo = relationship("Articulo", back_populates="calificaciones")
    usuario = relationship("Usuario", back_populates="calificaciones")
    
    __table_args__ = (UniqueConstraint('articulo_id', 'usuario_id', name='uix_1'),)  # Añadir restricción de unicidad

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, index=True)
    calificaciones = relationship("Calificacion", back_populates="usuario")
