#!/usr/bin/env python3
"""Simple web UI for HTML/HTM -> PDF conversion."""

from __future__ import annotations

import io
import tempfile
from pathlib import Path

from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename

from html2pdf import (
    ConvertError,
    ENGINE_AUTO,
    ENGINE_CHROMIUM,
    ENGINE_WEASYPRINT,
    ENGINE_WKHTMLTOPDF,
    convert,
    resolve_input_target,
)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB

ALLOWED_EXTENSIONS = {".htm", ".html"}
ALLOWED_ENGINES = {
    ENGINE_AUTO,
    ENGINE_CHROMIUM,
    ENGINE_WKHTMLTOPDF,
    ENGINE_WEASYPRINT,
}


def _is_allowed_filename(filename: str) -> bool:
    ext = Path(filename).suffix.lower()
    return ext in ALLOWED_EXTENSIONS


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/convert")
def convert_upload():
    uploaded = request.files.get("file")
    engine = request.form.get("engine", ENGINE_AUTO).strip().lower()

    if not uploaded or uploaded.filename == "":
        return render_template("index.html", error="Please select an .htm or .html file."), 400

    if not _is_allowed_filename(uploaded.filename):
        return render_template("index.html", error="Only .htm and .html files are allowed."), 400

    if engine not in ALLOWED_ENGINES:
        return render_template("index.html", error="Unsupported engine selection."), 400

    safe_name = secure_filename(uploaded.filename) or "document.html"
    stem = Path(safe_name).stem or "converted"

    try:
        with tempfile.TemporaryDirectory(prefix="html2pdf-ui-") as td:
            temp_dir = Path(td)
            input_path = temp_dir / safe_name
            output_path = temp_dir / f"{stem}.pdf"

            uploaded.save(input_path)
            input_target = resolve_input_target(str(input_path))
            convert(
                input_target=input_target,
                output_pdf=output_path,
                engine=engine,
                timeout_sec=90,
            )
            pdf_bytes = output_path.read_bytes()
    except ConvertError as err:
        return render_template("index.html", error=str(err)), 500

    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"{stem}.pdf",
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
