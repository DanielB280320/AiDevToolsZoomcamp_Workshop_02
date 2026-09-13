import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import router
from app.services import NotFoundError, ProviderError

# Comma-separated list of browser origins allowed to call the API (the Vite dev server by default).
CORS_ORIGINS = os.environ.get("KICKBOARD_CORS_ORIGINS", "http://localhost:5173").split(",")

app = FastAPI(title="Kickboard API", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=CORS_ORIGINS, allow_methods=["GET"], allow_headers=["*"])
app.include_router(router)


@app.exception_handler(NotFoundError)
async def handle_not_found(request: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(ProviderError)
async def handle_provider_error(request: Request, exc: ProviderError) -> JSONResponse:
    return JSONResponse(status_code=503, content={"detail": str(exc)})
