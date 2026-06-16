from __future__ import annotations

from src.app import create_app
from src.core.config import get_settings
import uvicorn
app = create_app()

if __name__ == "__main__":
    # 1. Fetch the cached settings
    run_settings = get_settings()
    
    uvicorn.run(
        "src.main:app", 
        host=run_settings.host, 
        port=run_settings.port, 
        # Only enable auto-reload if we are strictly in development mode
        reload=(run_settings.environment == "development") 
    )