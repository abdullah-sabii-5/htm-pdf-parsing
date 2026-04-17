# HTML/HTM to PDF (No LLM) - R&D + Prototype

This repo contains a deterministic HTML-to-PDF conversion CLI that does not use any LLM.

## Quick R&D Findings

1. `.htm` is **not** "HTML3".
2. `.htm` and `.html` are file extensions; rendering is based on the HTML parser/engine and content type (typically `text/html`), not the extension.
3. HTML 3.2 is a historical spec from 1997 and is superseded.
4. For modern websites (CSS + JS), a modern browser engine (Chromium via Playwright/Puppeteer or headless Chrome) is the most reliable converter.
5. For print-focused static documents, WeasyPrint is strong for paged-media CSS and has no JavaScript runtime.
6. `wkhtmltopdf` still exists but is based on old WebKit/Qt history and is generally less future-proof for modern web rendering.

## Sources

- WHATWG HTML Living Standard (updated April 7, 2026): https://html.spec.whatwg.org/multipage/introduction.html
- W3C HTML 3.2 (Recommendation date Jan 14, 1997; superseded): https://www.w3.org/TR/REC-html32
- Playwright `page.pdf()` API: https://playwright.dev/docs/api/class-page#page-pdf
- WeasyPrint docs: https://doc.courtbouillon.org/weasyprint/stable/
- wkhtmltopdf status/recommendations: https://wkhtmltopdf.org/status.html

## Prototype in this repo

- CLI: `html2pdf.py`
- Web UI: `app.py` + `templates/index.html`
- Sample input: `samples/invoice.htm`

The converter supports:

- `chromium` (headless CLI printing)
- `wkhtmltopdf`
- `weasyprint` (CLI)
- `auto` mode (tries engines in order)

## Usage

```bash
python3 html2pdf.py --input samples/invoice.htm --output out/invoice.pdf --engine auto
```

## Web UI (Upload + Download)

Run:

```bash
.venv/bin/python app.py
```

Then open:

```text
http://127.0.0.1:5000
```

Flow:

1. Upload `.htm` or `.html`.
2. Choose renderer (`auto` recommended).
3. Click "Convert and Download PDF".

For non-technical QA setup, see:

- `QA_WINDOWS_SETUP.md` — Windows
- `QA_LINUX_MAC_SETUP.md` — Linux & macOS

### URL input

```bash
python3 html2pdf.py --input https://example.com --output out/example.pdf --engine chromium
```

### Force a specific engine

```bash
python3 html2pdf.py --input samples/invoice.htm --output out/invoice.pdf --engine weasyprint
```

## Engine setup

Install at least one engine:

1. Chromium/Chrome (recommended for JS-heavy pages)
2. `wkhtmltopdf`
3. `weasyprint` CLI

Then rerun the command above.

### Reproducible local setup (used here)

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
python3 html2pdf.py --input samples/invoice.htm --output out/invoice.pdf --engine auto
```

The script auto-detects `.venv/bin/weasyprint` if `weasyprint` is not in `PATH`.

### One-command Web UI startup

| Platform | Command |
|----------|---------|
| Windows | Double-click `start-ui-windows.bat` |
| Linux / macOS | `chmod +x start-ui.sh && ./start-ui.sh` |

## Notes

- No LLM is used anywhere in the pipeline.
- Conversion quality depends on renderer support for your HTML/CSS/JS.
- For dynamic pages, prefer `chromium`.
