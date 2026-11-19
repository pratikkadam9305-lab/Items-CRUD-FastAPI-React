from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .database import Base, engine
from .routers import items

import logging
import json
import time
from datetime import datetime, timezone


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Items CRUD API", version="1.0.0")

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger("api.request")
logger.setLevel(logging.INFO)

@app.middleware("http")
async def request_logging_middleware(request, call_next):

    # Log API requests only
    if not request.url.path.startswith("/api"):
        return await call_next(request)

    start_time = time.perf_counter()

    try:
        response = await call_next(request)

        processing_time = (
            time.perf_counter() - start_time
        ) * 1000

        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "processing_time_ms": round(processing_time, 2),
        }

        logger.info(json.dumps(log_data))

        return response

    except Exception:
        processing_time = (
            time.perf_counter() - start_time
        ) * 1000

        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "method": request.method,
            "path": request.url.path,
            "status_code": 500,
            "processing_time_ms": round(processing_time, 2),
            "error": "Internal server error",
        }

        logger.exception(json.dumps(log_data))

        raise

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(items.router, prefix="/api")

FRONTEND_DIST = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"

if FRONTEND_DIST.exists():
    assets_dir = FRONTEND_DIST / "assets"
    if assets_dir.is_dir():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/")
    async def serve_index():
        return FileResponse(FRONTEND_DIST / "index.html")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = FRONTEND_DIST / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(FRONTEND_DIST / "index.html")
