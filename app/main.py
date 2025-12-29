"""FastAPI application entry point"""
import os
from datetime import datetime

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app.config import get_settings
from app.auth.router import router as auth_router
from app.pdfs.router import router as pdfs_router
from app.mcq.router import router as mcq_router
from app.quiz.router import router as quiz_router

settings = get_settings()

app = FastAPI(title="PDF to MCQ")

# Session middleware with proper cookie settings
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.APP_SECRET_KEY,
    session_cookie="session",
    max_age=14400,  # 4 hours
    same_site="lax",
    https_only=False
)

# Static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates with cache busting
templates = Jinja2Templates(directory="app/templates")

# Add static file version to template context
@app.middleware("http")
async def add_cache_buster(request, call_next):
    response = await call_next(request)
    return response

# Add custom template globals
templates.env.globals['static_version'] = str(int(datetime.now().timestamp()))

# Routers
app.include_router(auth_router)
app.include_router(pdfs_router)
app.include_router(mcq_router)
app.include_router(quiz_router)


@app.get("/")
async def root():
    """Redirect to PDFs page"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/pdfs")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
