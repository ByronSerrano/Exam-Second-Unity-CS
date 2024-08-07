from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str

class User(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True

class Producto(BaseModel):
    id: int
    nombre: str
    precio: float
    stock: int

    class Config:
        from_attributes = True

class Vendedor(BaseModel):
    id: int
    nombre: str
    region: str

    class Config:
        from_attributes = True

class Venta(BaseModel):
    id: int
    producto_id: int
    vendedor_id: int
    cantidad: int
    fecha_venta: str

    class Config:
        from_attributes = True
