from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routes.categories import router as categories_router
from app.routes.auth import router as auth_router
from app.routes.orders import router as orders_router
from app.routes.products import router as products_router

app = FastAPI(
    title="Sushi App API",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products_router)
app.include_router(categories_router)
app.include_router(auth_router)
app.include_router(orders_router)


@app.get("/health", tags=["Operations"])
def health_check():
    return {"status": "ok"}


@app.get("/")
def root():
    return {
        "message": "Sushi App API funcionando"
    }
