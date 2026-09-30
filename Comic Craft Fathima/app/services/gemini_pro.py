import time

from google.genai import types

from app.models import ComicOutline, ComicStory, PromptRequest
from app.services.gemini_client import get_gemini_client
from app.config import settings


def _is_temporary_error(exc: Exception) -> bool:
    """Check whether Gemini returned a temporary quota/service error."""

    message = str(exc).lower()

    temporary_errors = (
        "429",
        "503",
        "resource_exhausted",
        "unavailable",
        "high demand",
        "overloaded",
        "temporarily",
        "deadline exceeded",
        "timeout",
        "timed out",
    )

    return any(error in message for error in temporary_errors)


def _generate_story_with_model(
    client,
    model_name: str,
    prompt: str,
):
    """Generate the comic story using Gemini."""

    return client.models.generate_content(
        model=model_name,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ComicStory,
            max_output_tokens=7000,
        ),
    )


def generate_story(
    request: PromptRequest,
    outline: ComicOutline,
) -> ComicStory:

    client = get_gemini_client()

    outline_text = outline.model_dump_json(
        indent=2
    )

    prompt = f"""
Turn this comic outline into polished
panel-by-panel comic narration.

User inputs:

Story idea:
{request.story_prompt}

Main character:
{request.character_name}

Setting:
{request.setting}

Tone:
{request.tone}

Art style:
{request.art_style}

Outline:
{outline_text}

Requirements:

1. Return exactly {settings.panels_count} panels.

2. Preserve panel numbers and titles
   from the outline.

3. Keep character behavior and story
   continuity consistent.

4. scene_description should be concise
   and visual.

5. caption should be a short
   ambient/comic caption.

6. narration should advance the story.

7. dialogue should contain natural
   dialogue and may include multiple
   speakers.

8. Match the requested tone.

9. Do not make the story excessively long.

10. Keep the story suitable for a
    comic-book format.

11. Maintain continuity between every panel.
"""

    # The .env value is used first.
    #
    # Since your API key has access to
    # gemini-3.5-flash-lite, it is our
    # primary fallback.
    models_to_try = [
        settings.gemini_pro_model,
        "gemini-3.5-flash-lite",
        "gemini-3.6-flash",
        "gemini-3.5-flash",
        "gemini-flash-lite-latest",
        "gemini-flash-latest",
    ]

    # Remove duplicates.
    models_to_try = list(
        dict.fromkeys(models_to_try)
    )

    last_error = None

    for model_name in models_to_try:

        print()
        print("=" * 60)
        print(
            f"Trying Gemini story model: "
            f"{model_name}"
        )
        print("=" * 60)

        # Try each model twice.
        for attempt in range(2):

            try:

                print(
                    f"Gemini Story request: "
                    f"{model_name} "
                    f"(attempt {attempt + 1}/2)"
                )

                response = _generate_story_with_model(
                    client,
                    model_name,
                    prompt,
                )

                # -----------------------------------------
                # Structured response
                # -----------------------------------------

                if getattr(response, "parsed", None):

                    story = response.parsed

                else:

                    if not response.text:

                        raise RuntimeError(
                            "Gemini returned an empty "
                            "story response."
                        )

                    story = ComicStory.model_validate_json(
                        response.text
                    )

                # -----------------------------------------
                # Validate panel count
                # -----------------------------------------

                if len(story.panels) != settings.panels_count:

                    raise RuntimeError(
                        f"Gemini returned "
                        f"{len(story.panels)} story panels; "
                        f"expected "
                        f"{settings.panels_count}."
                    )

                print()
                print(
                    "SUCCESS: Comic story generated "
                    f"using {model_name}"
                )
                print()

                return story

            except Exception as exc:

                last_error = exc

                print(
                    f"Gemini Story error from "
                    f"{model_name}: {exc}"
                )

                # Non-temporary error:
                # stop immediately.
                if not _is_temporary_error(exc):

                    raise

                # Temporary error:
                # retry once.
                if attempt == 0:

                    wait_seconds = 5

                    print(
                        "Temporary Gemini story "
                        "generation error."
                    )

                    print(
                        f"Waiting {wait_seconds} "
                        "seconds before retry..."
                    )

                    time.sleep(wait_seconds)

                else:

                    print(
                        f"Second attempt failed "
                        f"for {model_name}."
                    )

        print(
            f"Model {model_name} unavailable "
            "for story generation."
        )

        print(
            "Trying the next story model..."
        )

    raise RuntimeError(
        "Gemini story generation failed.\n\n"
        "ComicCraft tried these models:\n"
        + "\n".join(
            f"- {model}"
            for model in models_to_try
        )
        + "\n\n"
        f"Last Gemini error: {last_error}"
    )