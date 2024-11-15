# schemas/schema.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class User(BaseModel):
    id: Optional[int]  # Para que FastAPI incluya el ID en las respuestas, lo hacemos opcional
    name: str
    apellido: str  # Nuevo campo para incluir el apellido
    password: str
    username: str
    active: Optional[bool] = True  # Refleja el campo `activo` en tu modelo de base de datos

    class Config:
        orm_mode = True  # Habilita el soporte para objetos ORM

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

class Proyecto(BaseModel):
    id_proyecto: Optional[int]  # Opcional para que se incluya en las respuestas si existe
    created_at: Optional[datetime]
    nombre: str
    direccion: Optional[str]
    activo: Optional[bool] = True  # Valor predeterminado si no se especifica

    class Config:
        from_attributes = True  # Habilita el soporte para objetos ORM     

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class GasolineraSchema(BaseModel):
    id_gasolinera: Optional[int]  # Opcional para que se incluya en la respuesta cuando exista
    created_at: Optional[datetime]
    nombre: str
    direccion: Optional[str]

    class Config:
        from_attributes = True  # Habilita el soporte para objetos ORM
   

class UserCount(BaseModel):
    total: int
