from fastapi import FastAPI
from app.routes.products import router as products_router

app = FastAPI(
    title="Sushi App API",
    version="0.1.0"
)

app.include_router(products_router)


@app.get("/")
def root():
    return {
        "message": "Sushi App API funcionando"
    }