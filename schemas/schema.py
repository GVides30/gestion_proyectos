# schemas/schema.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Esquema para Rol
class RolSchema(BaseModel):
    id_rol: Optional[int]
    descripcion: str

    class Config:
        orm_mode = True
        from_attributes = True

class User(BaseModel):
    id: Optional[int] = Field(alias="id_usr")
    created_at: Optional[datetime]
    name: str = Field(alias="nombre")
    apellido: str
    password: str
    username: str
    active: Optional[bool] = True
    id_rol: Optional[int]  # Aquí se usa solo `id_rol`

    class Config:
        from_attributes = True
        populate_by_name = True

class Vehiculo(BaseModel):
    id_vehiculo: Optional[int]  # Opcional para que se incluya en la respuesta
    created_at: Optional[datetime]
    modelo: str
    marca: str
    placa: str
    rendimiento: Optional[float]
    galonaje: Optional[float]
    tipo_combustible: Optional[str]

    class Config:
        orm_mode = True  # Habilita el soporte para objetos ORM
        from_attributes = True 

class Proyecto(BaseModel):
    id_proyecto: Optional[int]  # Opcional para que se incluya en las respuestas si existe
    created_at: Optional[datetime]
    nombre: str
    direccion: Optional[str]
    activo: Optional[bool] = True  # Valor predeterminado si no se especifica

    class Config:
        orm_mode = True
        from_attributes = True  # Habilita el soporte para objetos ORM     


class GasolineraSchema(BaseModel):
    id_gasolinera: Optional[int]  # Opcional para que se incluya en la respuesta cuando exista
    created_at: Optional[datetime]
    nombre: str
    direccion: Optional[str]

    class Config:
        orm_mode = True
        from_attributes = True  # Habilita el soporte para objetos ORM
   
# Esquema para Bitacora
class BitacoraSchema(BaseModel):
    id_bitacora: Optional[int]  # Opcional para que se incluya en la respuesta si existe
    created_at: Optional[datetime]
    comentario: Optional[str]
    km_inicial: Optional[float]
    km_final: Optional[float]
    num_galones: Optional[float]
    costo: Optional[float]
    tipo_gasolina: Optional[str]
    id_usr: Optional[int]  # Foreign key al usuario
    id_vehiculo: Optional[int]  # Foreign key al vehículo
    id_gasolinera: Optional[int]  # Foreign key a la gasolinera
    id_proyecto: Optional[int]  # Foreign key al proyecto
    usuario: Optional[User]  # Relación con el esquema User
    vehiculo: Optional[Vehiculo]  # Relación con el esquema Vehiculo
    gasolinera: Optional[GasolineraSchema]  # Relación con el esquema Gasolinera
    proyecto: Optional[Proyecto]  # Relación con el esquema Proyecto

    class Config:
        orm_mode = True
        from_attributes = True  # Habilita el soporte para objetos ORM

class BitacoraCreateSchema(BaseModel):
    id_bitacora: Optional[int] 
    created_at: Optional[datetime] = datetime.now()
    comentario: str
    km_inicial: float
    km_final: float
    num_galones: float
    costo: float
    tipo_gasolina: str
    id_usr: int
    id_vehiculo: int
    id_gasolinera: int
    id_proyecto: int

    class Config:
        orm_mode = True

class BitacoraUpdateSchema(BaseModel):
    id_bitacora: Optional[int]  # Opcional para la búsqueda
    created_at: Optional[datetime]
    comentario: Optional[str]
    km_inicial: Optional[float]
    km_final: Optional[float]
    num_galones: Optional[float]
    costo: Optional[float]
    tipo_gasolina: Optional[str]
    id_usr: Optional[int]
    id_vehiculo: Optional[int]
    id_gasolinera: Optional[int]
    id_proyecto: Optional[int]

    class Config:
        orm_mode = True



class UserCount(BaseModel):
    total: int
