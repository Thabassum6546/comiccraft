from pathlib import Path

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.models import PromptRequest
from app.services.gemini_flash import generate_outline
from app.services.gemini_pro import generate_story
from app.services.image_generator import generate_image
from app.services.layout_builder import build_comic_layout
from app.services.exporters import save_pdf


BASE_DIR = Path(__file__).resolve().parent.parent

templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates")
)

router = APIRouter()


def _generate(request_data: PromptRequest):
    outline = generate_outline(request_data)

    story = generate_story(
        request_data,
        outline
    )

    image_paths = [
        generate_image(
            panel.image_prompt,
            panel.panel_number
        )
        for panel in outline.panels
    ]

    layout = build_comic_layout(
        outline,
        story,
        image_paths
    )

    pdf_path = save_pdf(
        layout,
        title=request_data.story_prompt[:60]
    )

    return outline, story, layout, pdf_path


# ---------------------------------------------------------
# HOME PAGE
# ---------------------------------------------------------

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "settings": settings
        },
    )


# ---------------------------------------------------------
# GENERATE COMIC
# ---------------------------------------------------------

@router.post("/generate", response_class=HTMLResponse)
async def generate(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    art_style: str = Form(...),
):

    data = PromptRequest(
        story_prompt=story_prompt,
        character_name=character_name,
        setting=setting,
        tone=tone,
        art_style=art_style,
    )

    try:

        _, _, layout, pdf_path = _generate(data)

        return templates.TemplateResponse(
            request=request,
            name="comic_preview.html",
            context={
                "layout": layout,
                "pdf_path": pdf_path,
                "story_prompt": data.story_prompt,
            },
        )

    except Exception as exc:

        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={
                "error": str(exc)
            },
            status_code=500,
        )


# ---------------------------------------------------------
# JSON API
# ---------------------------------------------------------

@router.post("/generate-comic/json")
async def generate_json(data: PromptRequest):

    try:

        _, _, layout, pdf_path = _generate(data)

        return {
            "success": True,
            "message": "Comic generated successfully.",
            "layout": [
                item.model_dump()
                for item in layout
            ],
            "pdf_path": pdf_path,
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        ) from exc


# ---------------------------------------------------------
# IMAGE TEST
# ---------------------------------------------------------

@router.get("/test-image")
async def test_image(
    prompt: str = (
        "A cheerful fox hero in a magical forest, "
        "dynamic comic-book illustration"
    )
):

    try:

        image_path = generate_image(
            prompt,
            999
        )

        return {
            "success": True,
            "image_path": image_path
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        ) from exc


# ---------------------------------------------------------
# DOWNLOAD PDF
# ---------------------------------------------------------

@router.get("/download/{filename}")
async def download(filename: str):

    safe_name = Path(filename).name

    file_path = (
        BASE_DIR
        / "static"
        / "exports"
        / safe_name
    )

    if (
        not file_path.exists()
        or file_path.suffix.lower() != ".pdf"
    ):
        raise HTTPException(
            status_code=404,
            detail="PDF not found."
        )

    return FileResponse(
        file_path,
        media_type="application/pdf",
        filename=safe_name,
    )


# ---------------------------------------------------------
# EXPORT SUCCESS PAGE
# ---------------------------------------------------------

@router.get(
    "/export-success",
    response_class=HTMLResponse
)
async def export_success(
    request: Request,
    filename: str = ""
):

    return templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={
            "filename": (
                Path(filename).name
                if filename
                else ""
            )
        },
    )


# ---------------------------------------------------------
# HEALTH CHECK
# ---------------------------------------------------------

@router.get("/health")
async def health():

    return {
        "status": "ok",
        "gemini_configured": bool(
            settings.gemini_api_key
        ),
        "huggingface_configured": bool(
            settings.hf_token
        ),
        "image_provider": settings.image_provider,
    }