from fastapi import FastAPI, Request
import json
import logging
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routes.categories import router as categories_router
from app.routes.auth import router as auth_router
from app.routes.orders import router as orders_router
from app.routes.products import router as products_router
from app.routes.store_settings import router as store_settings_router

app = FastAPI(
    title="Sushi App API",
    version="0.1.0"
)

audit_logger = logging.getLogger("uvicorn.error")


@app.middleware("http")
async def record_staff_activity(request: Request, call_next):
    response = await call_next(request)
    user_id = getattr(request.state, "admin_user_id", None)
    if user_id is not None or request.url.path in {"/auth/login", "/auth/logout"}:
        route = request.scope.get("route")
        audit_logger.info(json.dumps({
            "event": "staff_request", "user_id": user_id,
            "method": request.method, "route": getattr(route, "path", "authentication"),
            "status": response.status_code,
        }))
    return response

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
app.include_router(store_settings_router)


@app.get("/health", tags=["Operations"])
def health_check():
    return {"status": "ok"}


@app.get("/")
def root():
    return {
        "message": "Sushi App API funcionando"
    }
