from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from config.db import get_db  # Asegúrate de que get_db esté configurado para obtener la sesión de la base de datos
from models import models  # Importa tus modelos (Usuario, etc.)
from schemas.schema import User, UserCount, Vehiculo
from typing import List
from starlette.status import HTTP_204_NO_CONTENT
from cryptography.fernet import Fernet
from models.models import Proyecto,Gasolinera # Importa tu modelo de Proyecto
from schemas.schema import Proyecto as ProyectoSchema,GasolineraSchema,RolSchema, BitacoraSchema, BitacoraCreateSchema, BitacoraUpdateSchema # Importa el esquema Pydantic correspondiente

# Inicializa el encriptador de contraseña
key = Fernet.generate_key()
f = Fernet(key)

# Configura el enrutador de FastAPI
user = APIRouter()


# Ruta para contar usuarios
@user.get("/users/count", tags=["users"], response_model=UserCount)
def get_users_count(db: Session = Depends(get_db)):
    result = db.query(func.count(models.Usuario.id_usr)).scalar()
    return {"total": result}

# Obtener un usuario por ID
@user.get("/users/{id}", tags=["users"], response_model=User, description="Get a single user by Id")
def get_user(id: int, db: Session = Depends(get_db)):
    db_user = db.query(models.Usuario).filter(models.Usuario.id_usr == id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Retorna un objeto User construido con los datos obtenidos
    return User(
        id=db_user.id_usr,
        created_at=db_user.created_at,
        name=db_user.nombre,
        apellido=db_user.apellido,
        password=db_user.password,
        username=db_user.username,
        active=db_user.activo,
        rol=db_user.rol
    )


@user.post("/", tags=["users"], response_model=User, description="Create a new user")
def create_user(user: User, db: Session = Depends(get_db)):

    # Verifica si el rol existe
    if user.rol and not db.query(models.Rol).filter(models.Rol.id_rol == user.rol.id_rol).first():
        raise HTTPException(status_code=400, detail="El rol especificado no existe | Por favor revise los roles disponibles")

    # Verificar si el nombre de usuario ya existe
    existing_user = db.query(models.Usuario).filter(models.Usuario.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Crear el nuevo usuario
    new_user = models.Usuario(
        created_at=user.created_at,
        nombre=user.name,
        apellido=user.apellido,
        password=f.encrypt(user.password.encode("utf-8")),
        activo=user.active if user.active is not None else True,
        username=user.username,
        id_rol=user.rol.id_rol if user.rol else None
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Usar `from_orm` para mapear el modelo de base de datos a un esquema Pydantic
    return User.from_orm(new_user)



# Actualizar un usuario por ID
@user.put("/users/{id}", tags=["users"], response_model=User, description="Update a User by Id")
def update_user(id: int, user: User, db: Session = Depends(get_db)):
    db_user = db.query(models.Usuario).filter(models.Usuario.id_usr == id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Actualiza los campos
    db_user.created_at=user.created_at
    db_user.nombre = user.name
    db_user.apellido = user.apellido
    if user.password:
        db_user.password = f.encrypt(user.password.encode("utf-8"))
    db_user.username = user.username
    db_user.activo = user.active if user.active is not None else db_user.activo
    db_user.id_rol = user.rol.id_rol if user.rol else db_user.id_rol

    db.commit()
    db.refresh(db_user)  # Refresca el objeto actualizado
    return User(
        id=db_user.id_usr,         # Mapea id_usr a id en el modelo Pydantic
        created_at=db_user.created_at,
        name=db_user.nombre,
        apellido=db_user.apellido,
        password=db_user.password,
        username=db_user.username,
        active=db_user.activo,
        rol=db_user.rol
    )


@user.delete("/users/{id}", tags=["users"], status_code=status.HTTP_204_NO_CONTENT, description="Delete a User by Id")
def delete_user(id: int, db: Session = Depends(get_db)):
    db_user = db.query(models.Usuario).filter(models.Usuario.id_usr == id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Elimina registros relacionados en la tabla log antes de eliminar el usuario
    db.query(models.Log).filter(models.Log.id_usr == id).delete()
    
    # Ahora elimina el usuario
    db.delete(db_user)
    db.commit()
    return {"message": "User successfully deleted"}# 204 No Content indica que no se necesita devolver datos

# Configura el enrutador de FastAPI para vehiculos
vehiculo = APIRouter()

# Ruta para contar vehículos
@vehiculo.get("/vehiculos/count", tags=["vehiculos"])
def get_vehiculos_count(db: Session = Depends(get_db)):
    result = db.query(func.count(models.Vehiculo.id_vehiculo)).scalar()
    return {"total": result}

# Obtener un vehículo por ID
@vehiculo.get("/vehiculos/{id}", tags=["vehiculos"], response_model=Vehiculo, description="Get a single vehicle by Id")
def get_vehiculo(id: int, db: Session = Depends(get_db)):
    db_vehiculo = db.query(models.Vehiculo).filter(models.Vehiculo.id_vehiculo == id).first()
    if db_vehiculo is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return Vehiculo(
        id_vehiculo=db_vehiculo.id_vehiculo,
        created_at=db_vehiculo.created_at,
        modelo=db_vehiculo.modelo,
        marca=db_vehiculo.marca,
        placa=db_vehiculo.placa,
        rendimiento=db_vehiculo.rendimiento,
        galonaje=db_vehiculo.galonaje,
        tipo_combustible=db_vehiculo.tipo_combustible
    )

# Crear un nuevo vehículo
@vehiculo.post("/vehiculos/", tags=["vehiculos"], response_model=Vehiculo, description="Create a new vehicle")
def create_vehiculo(vehiculo: Vehiculo, db: Session = Depends(get_db)):
    new_vehiculo = models.Vehiculo(
        created_at=vehiculo.created_at,
        modelo=vehiculo.modelo,
        marca=vehiculo.marca,
        placa=vehiculo.placa,
        rendimiento=vehiculo.rendimiento,
        galonaje=vehiculo.galonaje,
        tipo_combustible=vehiculo.tipo_combustible
    )
    db.add(new_vehiculo)
    db.commit()
    db.refresh(new_vehiculo)
    return Vehiculo(
        id_vehiculo=new_vehiculo.id_vehiculo,
        created_at=new_vehiculo.created_at,
        modelo=new_vehiculo.modelo,
        marca=new_vehiculo.marca,
        placa=new_vehiculo.placa,
        rendimiento=new_vehiculo.rendimiento,
        galonaje=new_vehiculo.galonaje,
        tipo_combustible=new_vehiculo.tipo_combustible
    )

# Actualizar un vehículo por ID
@vehiculo.put("/vehiculos/{id}", tags=["vehiculos"], response_model=Vehiculo, description="Update a vehicle by Id")
def update_vehiculo(id: int, vehiculo: Vehiculo, db: Session = Depends(get_db)):
    db_vehiculo = db.query(models.Vehiculo).filter(models.Vehiculo.id_vehiculo == id).first()
    if db_vehiculo is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    # Actualiza los campos
    db_vehiculo.created_at = vehiculo.created_at
    db_vehiculo.modelo = vehiculo.modelo
    db_vehiculo.marca = vehiculo.marca
    db_vehiculo.placa = vehiculo.placa
    db_vehiculo.rendimiento = vehiculo.rendimiento
    db_vehiculo.galonaje = vehiculo.galonaje
    db_vehiculo.tipo_combustible = vehiculo.tipo_combustible

    db.commit()
    db.refresh(db_vehiculo)
    return Vehiculo(
        id_vehiculo=db_vehiculo.id_vehiculo,
        created_at=db_vehiculo.created_at,
        modelo=db_vehiculo.modelo,
        marca=db_vehiculo.marca,
        placa=db_vehiculo.placa,
        rendimiento=db_vehiculo.rendimiento,
        galonaje=db_vehiculo.galonaje,
        tipo_combustible=db_vehiculo.tipo_combustible
    )

# Eliminar un vehículo por ID
@vehiculo.delete("/vehiculos/{id}", tags=["vehiculos"], status_code=status.HTTP_204_NO_CONTENT, description="Delete a vehicle by Id")
def delete_vehiculo(id: int, db: Session = Depends(get_db)):
    db_vehiculo = db.query(models.Vehiculo).filter(models.Vehiculo.id_vehiculo == id).first()
    if db_vehiculo is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    db.delete(db_vehiculo)
    db.commit()
    return {"message": "Vehicle successfully deleted"}


# Configura el enrutador de FastAPI para proyectos
proyecto = APIRouter()

# Ruta para obtener la lista de todos los proyectos
@proyecto.get("/proyectos", tags=["proyectos"], response_model=List[ProyectoSchema], description="Get all projects")
def get_proyectos(db: Session = Depends(get_db)):
    proyectos = db.query(Proyecto).all()
    return proyectos

# Ruta para obtener un proyecto por ID
@proyecto.get("/proyectos/{id}", tags=["proyectos"], response_model=ProyectoSchema, description="Get a single project by Id")
def get_proyecto(id: int, db: Session = Depends(get_db)):
    proyecto = db.query(Proyecto).filter(Proyecto.id_proyecto == id).first()
    if proyecto is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return proyecto

# Ruta para crear un nuevo proyecto
@proyecto.post("/proyectos", tags=["proyectos"], response_model=ProyectoSchema, description="Create a new project")
def create_proyecto(proyecto: ProyectoSchema, db: Session = Depends(get_db)):
    nuevo_proyecto = Proyecto(
        nombre=proyecto.nombre,
        created_at=proyecto.created_at,
        direccion=proyecto.direccion,
        activo=proyecto.activo if proyecto.activo is not None else True
    )
    db.add(nuevo_proyecto)
    db.commit()
    db.refresh(nuevo_proyecto)
    return nuevo_proyecto

# Ruta para actualizar un proyecto por ID
@proyecto.put("/proyectos/{id}", tags=["proyectos"], response_model=ProyectoSchema, description="Update a project by Id")
def update_proyecto(id: int, proyecto: ProyectoSchema, db: Session = Depends(get_db)):
    db_proyecto = db.query(Proyecto).filter(Proyecto.id_proyecto == id).first()
    if db_proyecto is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Actualiza los campos
    db_proyecto.nombre = proyecto.nombre
    db_proyecto.created_at = proyecto.created_at
    db_proyecto.direccion = proyecto.direccion
    db_proyecto.activo = proyecto.activo if proyecto.activo is not None else db_proyecto.activo

    db.commit()
    db.refresh(db_proyecto)
    return db_proyecto


# Ruta para eliminar un proyecto por ID
@proyecto.delete("/proyectos/{id}", tags=["proyectos"], status_code=status.HTTP_204_NO_CONTENT, description="Delete a project by Id")
def delete_proyecto(id: int, db: Session = Depends(get_db)):
    db_proyecto = db.query(Proyecto).filter(Proyecto.id_proyecto == id).first()
    if db_proyecto is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db.delete(db_proyecto)
    db.commit()
    return {"message": "Project successfully deleted"}

# Configura el enrutador de FastAPI
gasolinera = APIRouter()

# Ruta para obtener todas las gasolineras
@gasolinera.get("/gasolineras", tags=["gasolineras"], response_model=List[GasolineraSchema])
def get_all_gasolineras(db: Session = Depends(get_db)):
    gasolineras = db.query(Gasolinera).all()
    return gasolineras

# Ruta para obtener una gasolinera por ID
@gasolinera.get("/gasolineras/{id}", tags=["gasolineras"], response_model=GasolineraSchema, description="Get a single gasolinera by Id")
def get_gasolinera(id: int, db: Session = Depends(get_db)):
    gasolinera = db.query(Gasolinera).filter(Gasolinera.id_gasolinera == id).first()
    if gasolinera is None:
        raise HTTPException(status_code=404, detail="Gasolinera not found")
    return gasolinera

# Ruta para crear una nueva gasolinera
@gasolinera.post("/gasolineras", tags=["gasolineras"], response_model=GasolineraSchema, description="Create a new gasolinera")
def create_gasolinera(gasolinera: GasolineraSchema, db: Session = Depends(get_db)):
    new_gasolinera = Gasolinera(
        nombre=gasolinera.nombre,
        direccion=gasolinera.direccion,
        created_at=gasolinera.created_at or None  # Establece la fecha de creación si se proporciona
    )
    db.add(new_gasolinera)
    db.commit()
    db.refresh(new_gasolinera)  # Refresca el objeto para obtener el ID generado
    return new_gasolinera

# Ruta para actualizar una gasolinera por ID
@gasolinera.put("/gasolineras/{id}", tags=["gasolineras"], response_model=GasolineraSchema, description="Update a gasolinera by Id")
def update_gasolinera(id: int, gasolinera: GasolineraSchema, db: Session = Depends(get_db)):
    db_gasolinera = db.query(Gasolinera).filter(Gasolinera.id_gasolinera == id).first()
    if db_gasolinera is None:
        raise HTTPException(status_code=404, detail="Gasolinera not found")
    
    # Actualiza los campos
    db_gasolinera.nombre = gasolinera.nombre
    db_gasolinera.direccion = gasolinera.direccion
    db_gasolinera.created_at = gasolinera.created_at or db_gasolinera.created_at

    db.commit()
    db.refresh(db_gasolinera)
    return db_gasolinera

# Ruta para eliminar una gasolinera por ID
@gasolinera.delete("/gasolineras/{id}", tags=["gasolineras"], status_code=status.HTTP_204_NO_CONTENT, description="Delete a gasolinera by Id")
def delete_gasolinera(id: int, db: Session = Depends(get_db)):
    db_gasolinera = db.query(Gasolinera).filter(Gasolinera.id_gasolinera == id).first()
    if db_gasolinera is None:
        raise HTTPException(status_code=404, detail="Gasolinera not found")
    
    db.delete(db_gasolinera)
    db.commit()
    return {"message": "Gasolinera successfully deleted"}

# Configura el enrutador de FastAPI para roles
roles = APIRouter()

# Crear un nuevo rol
@roles.post("/roles", tags=["roles"], response_model=RolSchema, description="Create a new role")
def create_role(role: RolSchema, db: Session = Depends(get_db)):
    new_role = models.Rol(
        descripcion=role.descripcion
    )
    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    return new_role

# Obtener un rol por ID
@roles.get("/roles/{id_rol}", tags=["roles"], response_model=RolSchema, description="Get a role by Id")
def get_role(id_rol: int, db: Session = Depends(get_db)):
    db_role = db.query(models.Rol).filter(models.Rol.id_rol == id_rol).first()
    if db_role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    return db_role

# Obtener todos los roles
@roles.get("/roles", tags=["roles"], response_model=List[RolSchema], description="Get all roles")
def get_all_roles(db: Session = Depends(get_db)):
    roles = db.query(models.Rol).all()
    return roles

# Actualizar un rol por ID
@roles.put("/roles/{id_rol}", tags=["roles"], response_model=RolSchema, description="Update a role by Id")
def update_role(id_rol: int, role: RolSchema, db: Session = Depends(get_db)):
    db_role = db.query(models.Rol).filter(models.Rol.id_rol == id_rol).first()
    if db_role is None:
        raise HTTPException(status_code=404, detail="Role not found")

    # Actualiza el campo de descripción
    db_role.descripcion = role.descripcion
    db.commit()
    db.refresh(db_role)
    return db_role

# Eliminar un rol por ID
@roles.delete("/roles/{id_rol}", tags=["roles"], status_code=status.HTTP_204_NO_CONTENT, description="Delete a role by Id")
def delete_role(id_rol: int, db: Session = Depends(get_db)):
    db_role = db.query(models.Rol).filter(models.Rol.id_rol == id_rol).first()
    if db_role is None:
        raise HTTPException(status_code=404, detail="Role not found")

    db.delete(db_role)
    db.commit()
    return {"message": "Role successfully deleted"}

# Crear el enrutador para bitácoras
bitacora_router = APIRouter(
    prefix="/bitacoras",
    tags=["bitacoras"]
)

# Crear una nueva bitácora
@bitacora_router.post("/", response_model=BitacoraSchema, status_code=status.HTTP_201_CREATED)
def create_bitacora(bitacora: BitacoraCreateSchema, db: Session = Depends(get_db)):
    # Crear la instancia de Bitacora en base de datos
    new_bitacora = models.Bitacora(
        created_at=bitacora.created_at,
        comentario=bitacora.comentario,
        km_inicial=bitacora.km_inicial,
        km_final=bitacora.km_final,
        num_galones=bitacora.num_galones,
        costo=bitacora.costo,
        tipo_gasolina=bitacora.tipo_gasolina,
        id_usr=bitacora.id_usr,
        id_vehiculo=bitacora.id_vehiculo,
        id_gasolinera=bitacora.id_gasolinera,
        id_proyecto=bitacora.id_proyecto
    )
    db.add(new_bitacora)
    db.commit()
    db.refresh(new_bitacora)
    print(new_bitacora.usuario.__dict__)  # Confirmar qué campos tiene usuario

    # Construir los objetos anidados usando from_orm
    usuario_data = User.from_orm(new_bitacora.usuario) if new_bitacora.usuario else None
    vehiculo_data = Vehiculo.from_orm(new_bitacora.vehiculo) if new_bitacora.vehiculo else None
    gasolinera_data = GasolineraSchema.from_orm(new_bitacora.gasolinera) if new_bitacora.gasolinera else None
    proyecto_data = ProyectoSchema.from_orm(new_bitacora.proyecto) if new_bitacora.proyecto else None


    # Retornar el objeto de respuesta completo
    return BitacoraSchema(
        id_bitacora=new_bitacora.id_bitacora,
        created_at=new_bitacora.created_at,
        comentario=new_bitacora.comentario,
        km_inicial=new_bitacora.km_inicial,
        km_final=new_bitacora.km_final,
        num_galones=new_bitacora.num_galones,
        costo=new_bitacora.costo,
        tipo_gasolina=new_bitacora.tipo_gasolina,
        id_usr=new_bitacora.id_usr,
        id_vehiculo=new_bitacora.id_vehiculo,
        id_gasolinera=new_bitacora.id_gasolinera,
        id_proyecto=new_bitacora.id_proyecto,
        usuario=usuario_data,
        vehiculo=vehiculo_data,
        gasolinera=gasolinera_data,
        proyecto=proyecto_data
    )

# Actualizar una bitácora por ID
@bitacora_router.put("/{id}", response_model=BitacoraSchema)
def update_bitacora(id: int, bitacora: BitacoraUpdateSchema, db: Session = Depends(get_db)):
    # Busca la bitácora en la base de datos
    db_bitacora = db.query(models.Bitacora).filter(models.Bitacora.id_bitacora == id).first()
    if db_bitacora is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bitacora not found")

    # Actualiza solo los campos proporcionados
    if bitacora.created_at is not None:
        db_bitacora.created_at = bitacora.created_at
    if bitacora.comentario is not None:
        db_bitacora.comentario = bitacora.comentario
    if bitacora.km_inicial is not None:
        db_bitacora.km_inicial = bitacora.km_inicial
    if bitacora.km_final is not None:
        db_bitacora.km_final = bitacora.km_final
    if bitacora.num_galones is not None:
        db_bitacora.num_galones = bitacora.num_galones
    if bitacora.costo is not None:
        db_bitacora.costo = bitacora.costo
    if bitacora.tipo_gasolina is not None:
        db_bitacora.tipo_gasolina = bitacora.tipo_gasolina
    if bitacora.id_usr is not None:
        db_bitacora.id_usr = bitacora.id_usr
    if bitacora.id_vehiculo is not None:
        db_bitacora.id_vehiculo = bitacora.id_vehiculo
    if bitacora.id_gasolinera is not None:
        db_bitacora.id_gasolinera = bitacora.id_gasolinera
    if bitacora.id_proyecto is not None:
        db_bitacora.id_proyecto = bitacora.id_proyecto

    # Guarda los cambios en la base de datos
    db.commit()
    db.refresh(db_bitacora)

    # Retorna el objeto actualizado
    return db_bitacora



# Eliminar una bitácora por ID
@bitacora_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bitacora(id: int, db: Session = Depends(get_db)):
    db_bitacora = db.query(models.Bitacora).filter(models.Bitacora.id_bitacora == id).first()
    if db_bitacora is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bitacora not found")
    
    db.delete(db_bitacora)
    db.commit()
    return {"message": "Bitacora successfully deleted"}