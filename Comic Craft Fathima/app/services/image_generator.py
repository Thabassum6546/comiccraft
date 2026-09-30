from pathlib import Path
import re
from PIL import Image, ImageDraw, ImageFont
from huggingface_hub import InferenceClient

from app.config import settings

BASE_DIR = Path(__file__).resolve().parents[2]
PANEL_DIR = BASE_DIR / "static" / "panels"
PANEL_DIR.mkdir(parents=True, exist_ok=True)

def _safe_name(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9_-]+", "_", value).strip("_")
    return value[:80] or "panel"

def _fallback_image(prompt: str, filename: str) -> Path:
    # Lets the full application be tested even when an image provider is unavailable.
    img = Image.new("RGB", (settings.image_width, settings.image_height), "#dff3ff")
    draw = ImageDraw.Draw(img)
    draw.rectangle((20, 20, settings.image_width - 20, settings.image_height - 20), outline="#126782", width=6)
    title = "ComicCraft • Image Fallback"
    body = prompt[:240]
    try:
        font = ImageFont.truetype("arial.ttf", 22)
        small = ImageFont.truetype("arial.ttf", 17)
    except Exception:
        font = ImageFont.load_default()
        small = ImageFont.load_default()
    draw.text((45, 45), title, fill="#123", font=font)
    draw.multiline_text((45, 105), body, fill="#123", font=small, spacing=8)
    path = PANEL_DIR / filename
    img.save(path)
    return path

def generate_image(image_prompt: str, panel_number: int) -> str:
    filename = f"panel_{panel_number:02d}_{_safe_name(image_prompt[:50])}.png"
    output_path = PANEL_DIR / filename

    if settings.image_provider.lower() != "huggingface":
        if settings.allow_image_fallback:
            return f"/static/panels/{_fallback_image(image_prompt, filename).name}"
        raise RuntimeError(f"Unsupported IMAGE_PROVIDER: {settings.image_provider}")

    if not settings.hf_token:
        if settings.allow_image_fallback:
            return f"/static/panels/{_fallback_image(image_prompt, filename).name}"
        raise RuntimeError("HF_TOKEN is not configured.")

    try:
        client = InferenceClient(
            provider="auto",
            api_key=settings.hf_token,
        )
        image = client.text_to_image(
            prompt=image_prompt,
            model=settings.image_model,
            width=settings.image_width,
            height=settings.image_height,
            num_inference_steps=settings.image_steps,
            guidance_scale=settings.image_guidance,
        )
        image.save(output_path)
        return f"/static/panels/{output_path.name}"
    except Exception as exc:
        if settings.allow_image_fallback:
            return f"/static/panels/{_fallback_image(image_prompt, filename).name}"
        raise RuntimeError(f"Hugging Face image generation failed: {exc}") from exc
