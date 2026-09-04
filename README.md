## Exy

FastAPI service with a required health endpoint.

### Run locally

```bash
uv sync
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

### Health check

```bash
curl http://localhost:8000/health
```
