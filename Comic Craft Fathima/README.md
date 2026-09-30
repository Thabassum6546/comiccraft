# ComicCraft — AI Comic Story Creator

ComicCraft is a FastAPI + Jinja2 web application that follows the supplied project specification:
- collect story prompt, character, setting, tone and art style;
- generate a structured 5-panel outline with Gemini;
- expand the outline into narration/dialogue;
- generate comic illustrations;
- build a panel layout;
- export the result as a multi-page PDF;
- expose browser routes and a JSON API.

## Important model update

The supplied documentation names `models/gemini-1.5-flash` and `models/gemini-1.5-pro`.
This implementation uses the current Google GenAI Python SDK and configurable model names.
The defaults are:
- `gemini-3.8-flash` for structured outline generation
- `gemini-3.1-pro-preview` for detailed story generation

Change the two variables in `.env` if the models available to your API key differ.

## Project structure

```text
ComicCraft/
├── app/
│   ├── main.py
│   ├── routes.py
│   ├── config.py
│   ├── models.py
│   └── services/
│       ├── gemini_client.py
│       ├── gemini_flash.py
│       ├── gemini_pro.py
│       ├── image_generator.py
│       ├── layout_builder.py
│       └── exporters.py
├── templates/
│   ├── index.html
│   ├── comic_preview.html
│   ├── export_success.html
│   └── error.html
├── static/
│   ├── css/style.css
│   ├── js/app.js
│   ├── images/comic_background.png
│   ├── panels/
│   └── exports/
├── tests/test_app.py
├── .env.example
├── .gitignore
├── requirements.txt
└── run.py
```

## Windows / VS Code setup

Open the project folder in VS Code.

### 1. Create the virtual environment

PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### 2. Install packages

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Create `.env`

```powershell
Copy-Item .env.example .env
```

Open `.env` and set:

```env
GEMINI_API_KEY=your_real_gemini_key
HF_TOKEN=your_real_huggingface_token
```

Do not put quotation marks around the key unless required by your shell.

### 4. Run the app

```powershell
python run.py
```

or:

```powershell
uvicorn app.main:app --reload
```

Open:
- http://127.0.0.1:8000
- http://127.0.0.1:8000/docs
- http://127.0.0.1:8000/health

## Test without image inference

The project includes an image fallback so the UI/PDF pipeline can be tested even if Hugging Face is not configured.

Set:

```env
ALLOW_IMAGE_FALLBACK=true
```

You still need a Gemini API key to generate the actual story.

## API test

Open `/docs`, choose `POST /generate-comic/json`, and send:

```json
{
  "story_prompt": "A brave fox exploring an enchanted forest",
  "character_name": "Finn",
  "setting": "Forest",
  "tone": "Adventurous",
  "art_style": "Comic book"
}
```

## Image test

Browser:

```text
http://127.0.0.1:8000/test-image?prompt=A%20heroic%20fox%20in%20a%20magical%20forest
```

## Run tests

```powershell
pytest
```

## Background image

The supplied comic explosion/cloud artwork is included at:

```text
static/images/comic_background.png
```

It is used as the landing-page and success-page background.

## Troubleshooting

### `GEMINI_MODEL=` is not recognized in PowerShell

PowerShell does not use Bash's `NAME=value` syntax.

Use the `.env` file instead, or:

```powershell
$env:GEMINI_FLASH_MODEL="gemini-3.8-flash"
```

### Gemini 503 / model unavailable

Check the model configured in `.env` and the models available to your API key. The project keeps the model names configurable so you do not need to edit Python code.

### No images

Check:
1. `HF_TOKEN`
2. `IMAGE_MODEL`
3. `IMAGE_PROVIDER=huggingface`
4. `ALLOW_IMAGE_FALLBACK=true` while testing

### PDF opens but some special characters look different

The PDF exporter uses standard Helvetica for maximum portability. For full Unicode typography, add and register a Unicode TTF font in `exporters.py`.

## Flow

```text
Browser
   ↓
FastAPI /generate
   ↓
Gemini Flash → 5-panel outline
   ↓
Gemini Pro → narration + dialogue
   ↓
Hugging Face → one illustration per panel
   ↓
layout_builder.py
   ↓
exporters.py → PDF
   ↓
Comic Preview → Download
```
