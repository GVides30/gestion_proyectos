from fastapi import FastAPI
from routes.routes import user, vehiculo, proyecto, gasolinera, roles, bitacora_router, app as login_router
from config.openapi import tags_metadata

app = FastAPI(
   title="Gestión de Proyectos",
   description="Trabajo Final de FBD",
   version="0.0.1",
   openapi_tags=tags_metadata,
)

# Incluyendo las rutas de usuario
app.include_router(user)
app.include_router(vehiculo)
app.include_router(proyecto)
app.include_router(gasolinera)
app.include_router(roles)
app.include_router(bitacora_router)
app.include_router(login_router, prefix="/login", tags=["login"]) 

