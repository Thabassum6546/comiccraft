from pathlib import Path
from datetime import datetime
import textwrap

from fpdf import FPDF
from PIL import Image

from app.models import ComicLayoutItem


BASE_DIR = Path(__file__).resolve().parents[2]

EXPORT_DIR = BASE_DIR / "static" / "exports"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)


class ComicPDF(FPDF):

    def header(self):
        self.set_font("Helvetica", "B", 15)

        self.cell(
            0,
            10,
            "ComicCraft - AI Comic Story",
            new_x="LMARGIN",
            new_y="NEXT",
            align="C",
        )

        self.ln(2)


def _safe_text(value) -> str:
    """
    Convert AI-generated text into safe PDF text.

    Helvetica in a standard PDF has limited Unicode
    support, so unsupported characters are replaced.
    """

    if value is None:
        return ""

    value = str(value)

    # Normalize whitespace.
    value = value.replace("\r\n", "\n")
    value = value.replace("\r", "\n")

    # Replace unusual whitespace characters.
    value = value.replace("\u00a0", " ")
    value = value.replace("\u200b", "")
    value = value.replace("\ufeff", "")

    # Prevent extremely long unbroken words from
    # crashing FPDF's line wrapping.
    cleaned_lines = []

    for line in value.split("\n"):

        if not line.strip():
            cleaned_lines.append("")
            continue

        wrapped = textwrap.wrap(
            line,
            width=80,
            break_long_words=True,
            break_on_hyphens=False,
            replace_whitespace=False,
        )

        if wrapped:
            cleaned_lines.extend(wrapped)
        else:
            cleaned_lines.append("")

    value = "\n".join(cleaned_lines)

    # Helvetica uses Latin-1.
    value = (
        value
        .encode("latin-1", "replace")
        .decode("latin-1")
    )

    return value


def _usable_width(pdf: FPDF) -> float:
    """
    Return the actual usable page width.
    """

    return (
        pdf.w
        - pdf.l_margin
        - pdf.r_margin
    )


def _write_text(
    pdf: FPDF,
    text: str,
    font_size: float = 10,
    style: str = "",
    line_height: float = 6,
):
    """
    Safely write text using an explicit cell width.
    """

    pdf.set_font(
        "Helvetica",
        style,
        font_size,
    )

    safe = _safe_text(text)

    if not safe.strip():
        return

    width = _usable_width(pdf)

    pdf.multi_cell(
        width,
        line_height,
        safe,
        new_x="LMARGIN",
        new_y="NEXT",
    )


def save_pdf(
    layout: list[ComicLayoutItem],
    title: str = "ComicCraft Comic",
) -> str:

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    filename = f"comic_{timestamp}.pdf"

    output = EXPORT_DIR / filename

    pdf = ComicPDF(
        orientation="P",
        unit="mm",
        format="A4",
    )

    pdf.set_auto_page_break(
        auto=True,
        margin=15,
    )

    # -------------------------------------------------
    # Generate one PDF page per comic panel
    # -------------------------------------------------

    for panel in layout:

        pdf.add_page()

        # -------------------------------------------------
        # Panel title
        # -------------------------------------------------

        title_text = (
            f"Panel {panel.panel_number}: "
            f"{panel.title}"
        )

        _write_text(
            pdf,
            title_text,
            font_size=17,
            style="B",
            line_height=9,
        )

        pdf.ln(2)

        # -------------------------------------------------
        # Panel image
        # -------------------------------------------------

        image_path = str(panel.image_path)

        # Convert URL-style path to local filesystem path.
        image_path = image_path.lstrip("/")

        image_file = BASE_DIR / image_path

        if image_file.exists():

            try:

                with Image.open(image_file) as im:

                    width_px, height_px = im.size

                # Prevent division by zero.
                if width_px > 0 and height_px > 0:

                    max_w = 180
                    max_h = 105

                    scale = min(
                        max_w / width_px,
                        max_h / height_px,
                    )

                    draw_w = width_px * scale
                    draw_h = height_px * scale

                    # Center image on A4 page.
                    x = (
                        pdf.w - draw_w
                    ) / 2

                    pdf.image(
                        str(image_file),
                        x=x,
                        y=pdf.get_y(),
                        w=draw_w,
                        h=draw_h,
                    )

                    pdf.ln(
                        draw_h + 6
                    )

            except Exception as image_error:

                print(
                    f"Warning: could not add image "
                    f"for panel "
                    f"{panel.panel_number}: "
                    f"{image_error}"
                )

        else:

            print(
                f"Warning: image not found: "
                f"{image_file}"
            )

        # -------------------------------------------------
        # Scene description
        # -------------------------------------------------

        _write_text(
            pdf,
            panel.scene_description,
            font_size=10,
            style="I",
            line_height=6,
        )

        pdf.ln(2)

        # -------------------------------------------------
        # Caption
        # -------------------------------------------------

        _write_text(
            pdf,
            "Caption",
            font_size=11,
            style="B",
            line_height=6,
        )

        _write_text(
            pdf,
            panel.caption,
            font_size=10,
            style="",
            line_height=6,
        )

        pdf.ln(2)

        # -------------------------------------------------
        # Narration
        # -------------------------------------------------

        _write_text(
            pdf,
            "Narration",
            font_size=11,
            style="B",
            line_height=6,
        )

        _write_text(
            pdf,
            panel.narration,
            font_size=10,
            style="",
            line_height=6,
        )

        pdf.ln(2)

        # -------------------------------------------------
        # Dialogue
        # -------------------------------------------------

        _write_text(
            pdf,
            "Dialogue",
            font_size=11,
            style="B",
            line_height=6,
        )

        _write_text(
            pdf,
            panel.dialogue,
            font_size=10,
            style="",
            line_height=6,
        )

    # -------------------------------------------------
    # Save PDF
    # -------------------------------------------------

    pdf.output(str(output))

    print(
        f"PDF successfully created: {output}"
    )

    return f"/static/exports/{output.name}"