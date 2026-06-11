"""
main.py
-------
Punto de entrada de la API. Crea la aplicación FastAPI, habilita CORS (para
que el frontend de la Etapa 3 pueda consumirla) y registra todos los routers.

Para correrla:
    uvicorn app.main:app --reload
Y abre la documentación interactiva en:
    http://localhost:8000/docs
"""

from contextlib import asynccontextmanager
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import cuentas, documentos, firmantes, ortografia, proyectos, reportes, vouchers
from app.database import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Al arrancar, crea cualquier tabla que falte (idempotente).
    # El catálogo se carga aparte con: python scripts/seed.py
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Sistema de Vouchers Contables",
    description="API para generar y controlar vouchers (partidas contables).",
    version="0.2.0",
    lifespan=lifespan,
)

# Orígenes permitidos para CORS.
#  - En desarrollo, el frontend de Vite corre en localhost:5173.
#  - En producción, define CORS_ORIGINS con la URL de tu frontend (varias
#    separadas por coma). Ej: CORS_ORIGINS=https://vouchers.vercel.app
_origenes = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _origenes.split(",") if o.strip()],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Estado"])
def inicio():
    return {"mensaje": "API de Vouchers en línea", "docs": "/docs"}


app.include_router(cuentas.router)
app.include_router(proyectos.router)
app.include_router(firmantes.router)
app.include_router(vouchers.router)
app.include_router(documentos.router)
app.include_router(reportes.router)
app.include_router(ortografia.router)
