import time

from google.genai import types

from app.config import settings
from app.models import ComicOutline, PromptRequest
from app.services.gemini_client import get_gemini_client


def _is_temporary_error(exc: Exception) -> bool:
    """Check whether the Gemini error is temporary."""

    message = str(exc).lower()

    temporary_errors = (
        "503",
        "unavailable",
        "high demand",
        "overloaded",
        "temporarily",
        "deadline exceeded",
        "timeout",
        "timed out",
    )

    return any(error in message for error in temporary_errors)


def _generate_with_model(
    client,
    model_name: str,
    prompt: str,
):
    """Generate a structured comic outline."""

    return client.models.generate_content(
        model=model_name,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ComicOutline,
            max_output_tokens=5000,
        ),
    )


def generate_outline(
    request: PromptRequest,
) -> ComicOutline:

    client = get_gemini_client()

    prompt = f"""
Create a cohesive {settings.panels_count}-panel comic outline.

User story idea:
{request.story_prompt}

Main character:
{request.character_name}

Setting:
{request.setting}

Tone:
{request.tone}

Art style:
{request.art_style}

Requirements:

1. Return exactly {settings.panels_count} panels.

2. Keep the same main character and visual identity
   across all panels.

3. The story must have:
   - a clear beginning
   - story development
   - a turning point
   - a satisfying ending

4. Each panel must contain:
   - panel number
   - scene description
   - narration
   - dialogue
   - image prompt

5. Each image prompt must describe ONE comic illustration.

6. Do NOT create a collage.

7. Do NOT include written text inside the generated image.

8. Do NOT include captions inside the generated image.

9. Do NOT include speech bubbles inside the generated image.

10. Do NOT include logos or watermarks.

11. Describe:
   - character
   - action
   - environment
   - camera framing
   - lighting
   - requested art style

12. Keep visual continuity between panels.
"""

    # The first model comes from .env.
    # The remaining models are fallbacks.
    models_to_try = [
        settings.gemini_flash_model,
        "gemini-3.5-flash-lite",
        "gemini-3.6-flash",
        "gemini-3.5-flash",
        "gemini-flash-lite-latest",
        "gemini-flash-latest",
    ]

    # Remove duplicate model names.
    models_to_try = list(dict.fromkeys(models_to_try))

    last_error = None

    for model_name in models_to_try:

        print()
        print("=" * 60)
        print(f"Trying Gemini model: {model_name}")
        print("=" * 60)

        # Try each model twice.
        for attempt in range(2):

            try:

                print(
                    f"Gemini Flash request: "
                    f"{model_name} "
                    f"(attempt {attempt + 1}/2)"
                )

                response = _generate_with_model(
                    client,
                    model_name,
                    prompt,
                )

                # ---------------------------------------------
                # Get structured response
                # ---------------------------------------------

                if getattr(response, "parsed", None):

                    outline = response.parsed

                else:

                    if not response.text:
                        raise RuntimeError(
                            "Gemini returned an empty response."
                        )

                    outline = ComicOutline.model_validate_json(
                        response.text
                    )

                # ---------------------------------------------
                # Check panel count
                # ---------------------------------------------

                if len(outline.panels) != settings.panels_count:

                    raise RuntimeError(
                        f"Gemini returned "
                        f"{len(outline.panels)} panels; "
                        f"expected "
                        f"{settings.panels_count}."
                    )

                print()
                print(
                    f"SUCCESS: Comic outline generated "
                    f"using {model_name}"
                )
                print()

                return outline

            except Exception as exc:

                last_error = exc

                print(
                    f"Gemini error from "
                    f"{model_name}: {exc}"
                )

                # If this is not a temporary error,
                # stop immediately.
                if not _is_temporary_error(exc):

                    raise

                # Retry once after waiting.
                if attempt == 0:

                    wait_seconds = 5

                    print(
                        "Temporary Gemini service error."
                    )

                    print(
                        f"Waiting {wait_seconds} seconds "
                        f"before retry..."
                    )

                    time.sleep(wait_seconds)

                else:

                    print(
                        f"Second attempt failed for "
                        f"{model_name}."
                    )

        print(
            f"Model {model_name} unavailable."
        )

        print(
            "Trying the next Gemini model..."
        )

    # ---------------------------------------------
    # All models failed
    # ---------------------------------------------

    raise RuntimeError(
        "Gemini is temporarily unavailable.\n\n"
        "ComicCraft tried these models:\n"
        + "\n".join(
            f"- {model}"
            for model in models_to_try
        )
        + "\n\n"
        f"Last Gemini error: {last_error}"
    )