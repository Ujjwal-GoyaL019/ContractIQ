from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.suppliers import router as suppliers_router
from app.api.v1.products import router as products_router
from app.api.v1.inventory import router as inventory_router
from app.api.v1.forecast import router as forecast_router
from app.api.v1.risk import router as risk_router
from app.api.v1.documents import router as documents_router
from app.api.v1.chat import router as chat_router
from app.api.v1.optimization import router as optimization_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(suppliers_router)
api_router.include_router(products_router)
api_router.include_router(inventory_router)
api_router.include_router(forecast_router)
api_router.include_router(risk_router)
api_router.include_router(documents_router)
api_router.include_router(chat_router)
api_router.include_router(optimization_router)

