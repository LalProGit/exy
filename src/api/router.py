from fastapi import APIRouter
from src.domain.ingress.router import router as ingress_router
from src.domain.system.router import router as system_router
from src.domain.tools.router import router as tools_router

router = APIRouter()

router.include_router(system_router)
router.include_router(ingress_router)
router.include_router(tools_router)