from fastapi import FastAPI
from contextlib import asynccontextmanager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Perform any startup tasks here
    print("Starting up the application...")
    yield
    # Perform any shutdown tasks here
    print("Shutting down the application...")

app = FastAPI(
    title="EXY bot",
    lifespan=lifespan,
    version="1.0.0"
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy"}
