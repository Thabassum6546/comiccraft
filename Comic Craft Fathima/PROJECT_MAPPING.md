# Project documentation mapping

This implementation follows the supplied ComicCraft PDF:
- FastAPI backend and Jinja2 frontend
- `generate_outline()` in `gemini_flash.py`
- `generate_story()` in `gemini_pro.py`
- `generate_image()` in `image_generator.py`
- `build_comic_layout()` in `layout_builder.py`
- `save_pdf()` in `exporters.py`
- `/`, `/generate`, `/generate-comic/json`, `/test-image`, `/export-success`
- 5-panel workflow
- PDF export
- supplied scenic/comic background image

The source document's model names are historical (`gemini-1.5-flash`, `gemini-1.5-pro`).
This code uses the current Google GenAI SDK and configurable current model names instead.
