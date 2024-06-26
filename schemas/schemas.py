from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ProductoBase(BaseModel):
    nombre: str
    precio: float
    stock: int

class ProductoCreate(ProductoBase):
    pass

class Producto(ProductoBase):
    id: int

    class Config:
        orm_mode = True

class VendedorBase(BaseModel):
    nombre: str
    region: str

class VendedorCreate(VendedorBase):
    pass

class Vendedor(VendedorBase):
    id: int

    class Config:
        orm_mode = True

class VentaBase(BaseModel):
    producto_id: int
    vendedor_id: int
    cantidad: int
    fecha_venta: datetime

class VentaCreate(VentaBase):
    pass

class Venta(VentaBase):
    id: int

    class Config:
        orm_mode = True