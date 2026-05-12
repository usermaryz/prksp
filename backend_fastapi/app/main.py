from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import DATA_DIR, settings
from app.database import SessionLocal, engine
from app.models import Base
from app.routers import auth, dashboard, inventory, logistics, orders, picking, products
from app.seed import seed_if_empty


@asynccontextmanager
async def lifespan(_: FastAPI):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_if_empty(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="PRKSP WMS API",
    version="0.1",
    description="Учебный REST-слой мини-WMS: заказы, склад, сборка, логистика.",
    lifespan=lifespan,
)

_default_cors = [
    "http://127.0.0.1:3000",
    "http://localhost:3000",
    "http://127.0.0.1:8080",
    "http://localhost:8080",
]
_extra = [o.strip() for o in settings.cors_extra_origins.split(",") if o.strip()]
_cors_origins = _default_cors + _extra

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(products.router, prefix="/api")
app.include_router(orders.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(inventory.router, prefix="/api")
app.include_router(picking.router, prefix="/api")
app.include_router(logistics.router, prefix="/api")


@app.get("/health")
def health():
    return {"status": "ok"}
