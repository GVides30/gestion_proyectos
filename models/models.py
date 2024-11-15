# models.py
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, TIMESTAMP
from sqlalchemy.orm import relationship
from config.db import Base  # Importamos Base desde config.db

# Tabla de Rol
class Rol(Base):
    __tablename__ = "rol"
    id_rol = Column(Integer, primary_key=True, index=True)
    descripcion = Column(String(255))

# Tabla de Usuarios
class Usuario(Base):
    __tablename__ = "usuarios"
    id_usr = Column(Integer, primary_key=True, index=True)
    created_at = Column(TIMESTAMP)
    nombre = Column(String(255), nullable=False)
    apellido = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    id_rol = Column(Integer, ForeignKey("rol.id_rol"))
    activo = Column(Boolean, default=True)
    username = Column(String(255), unique=True, nullable=False)

    # Relación con la tabla Rol
    rol = relationship("Rol")

# Tabla de Gasolineras
class Gasolinera(Base):
    __tablename__ = "gasolineras"
    id_gasolinera = Column(Integer, primary_key=True, index=True)
    created_at = Column(TIMESTAMP)
    nombre = Column(String(255), nullable=False)
    direccion = Column(String(255))

# Tabla de Proyecto
class Proyecto(Base):
    __tablename__ = "proyecto"
    id_proyecto = Column(Integer, primary_key=True, index=True)
    created_at = Column(TIMESTAMP)
    nombre = Column(String(255), nullable=False)
    direccion = Column(String(255))
    activo = Column(Boolean, default=True)

# Tabla de Vehiculos
class Vehiculo(Base):
    __tablename__ = "vehiculos"
    id_vehiculo = Column(Integer, primary_key=True, index=True)
    created_at = Column(TIMESTAMP)
    modelo = Column(String(255))
    marca = Column(String(255))
    placa = Column(String(255), unique=True, nullable=False)
    rendimiento = Column(Float)
    galonaje = Column(Float)
    tipo_combustible = Column(String(255))

# Tabla de Bitacora
class Bitacora(Base):
    __tablename__ = "bitacora"
    id_bitacora = Column(Integer, primary_key=True, index=True)
    created_at = Column(TIMESTAMP)
    comentario = Column(String(255))
    km_inicial = Column(Float)
    km_final = Column(Float)
    num_galones = Column(Float)
    costo = Column(Float)
    tipo_gasolina = Column(String(255))
    id_usr = Column(Integer, ForeignKey("usuarios.id_usr"))
    id_vehiculo = Column(Integer, ForeignKey("vehiculos.id_vehiculo"))
    id_gasolinera = Column(Integer, ForeignKey("gasolineras.id_gasolinera"))
    id_proyecto = Column(Integer, ForeignKey("proyecto.id_proyecto"))

    # Relaciones con otras tablas
    usuario = relationship("Usuario")
    vehiculo = relationship("Vehiculo")
    gasolinera = relationship("Gasolinera")
    proyecto = relationship("Proyecto")

# Tabla de Log
class Log(Base):
    __tablename__ = "log"
    id_log = Column(Integer, primary_key=True, index=True)
    created_at = Column(TIMESTAMP)
    descripcion = Column(String(255), default='login')
    id_usr = Column(Integer, ForeignKey("usuarios.id_usr"))

    # Relación con la tabla Usuario
    usuario = relationship("Usuario")