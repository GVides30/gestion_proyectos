from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configura la URL de conexión a PostgreSQL
DATABASE_URL = "postgresql+psycopg2://root:7cu6nKEZc1dUh3l3r0Im1uYneAekFEWS@dpg-cssfon52ng1s73akplqg-a.oregon-postgres.render.com/gestion_proyectos_ghcl"

# Crea el motor de la base de datos
engine = create_engine(DATABASE_URL)

# Crea el objeto MetaData
meta = MetaData()

# Crea la clase base para los modelos ORM
Base = declarative_base()

# Configura la sesión de la base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crea todas las tablas definidas en los modelos
Base.metadata.create_all(bind=engine)

# Función para obtener la sesión de la base de datos en cada solicitud
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
