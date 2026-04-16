import logging
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.routers import clients, declarations
from app.services.fattureincloud import (
    FattureInCloudAuthError,
    FattureInCloudError,
    FattureInCloudNotFoundError,
)
from app.services.pdf_generator import PDFTemplateError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

app = FastAPI(title="Dichiarazioni di Conformità")

# Static files and templates
BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

# Routers
app.include_router(clients.router)
app.include_router(declarations.router)


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


# --- Exception handlers ---

@app.exception_handler(FattureInCloudAuthError)
def handle_auth_error(request: Request, exc: FattureInCloudAuthError):
    return JSONResponse(
        status_code=401,
        content={"error": str(exc)},
    )


@app.exception_handler(FattureInCloudNotFoundError)
def handle_not_found_error(request: Request, exc: FattureInCloudNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"error": str(exc)},
    )


@app.exception_handler(FattureInCloudError)
def handle_fic_error(request: Request, exc: FattureInCloudError):
    return JSONResponse(
        status_code=502,
        content={"error": str(exc)},
    )


@app.exception_handler(PDFTemplateError)
def handle_pdf_error(request: Request, exc: PDFTemplateError):
    return JSONResponse(
        status_code=500,
        content={"error": str(exc)},
    )
