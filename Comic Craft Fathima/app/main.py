from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.routes import router

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(
    title=settings.app_name,
    description="AI Comic Story Creator using Gemini and Stable Diffusion-compatible image generation.",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
app.include_router(router)

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return {}
