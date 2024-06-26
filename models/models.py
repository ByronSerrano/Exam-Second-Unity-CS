from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from db.database import Base

class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    precio = Column(Float)
    stock = Column(Integer)

    ventas = relationship("Venta", back_populates="producto")

class Vendedor(Base):
    __tablename__ = "vendedores"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    region = Column(String)

    ventas = relationship("Venta", back_populates="vendedor")

class Venta(Base):
    __tablename__ = "ventas"

    id = Column(Integer, primary_key=True, index=True)
    producto_id = Column(Integer, ForeignKey("productos.id"))
    vendedor_id = Column(Integer, ForeignKey("vendedores.id"))
    cantidad = Column(Integer)
    fecha_venta = Column(DateTime)

    producto = relationship("Producto", back_populates="ventas")
    vendedor = relationship("Vendedor", back_populates="ventas")