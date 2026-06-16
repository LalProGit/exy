from fastapi import APIRouter
from src.domain.system.router import router as system_router

router = APIRouter()

router.include_router(system_router)