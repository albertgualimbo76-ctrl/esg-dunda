import ssl
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# URL do banco
DATABASE_URL = "postgresql+asyncpg://neondb_owner:npg_pfmYoOV9sH4c@ep-lucky-paper-aivl915j.c-4.us-east-1.aws.neon.tech/"

# SSL para Neon
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = True
ssl_context.verify_mode = ssl.CERT_REQUIRED

# Engine assíncrona
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    connect_args={"ssl": ssl_context, "database": "neondb"},
    pool_size=5,
    max_overflow=0
)

# Sessão assíncrona
SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base para modelos
Base = declarative_base()

# Dependency FastAPI
async def get_db():
    async with SessionLocal() as session:
        yield session