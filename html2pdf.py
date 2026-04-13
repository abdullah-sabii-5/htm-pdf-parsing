#!/usr/bin/env python3
"""Deterministic HTML/HTM -> PDF converter with pluggable engines.

No LLM is used. This tool shells out to one of:
- chromium / google-chrome (headless print-to-pdf)
- wkhtmltopdf
- weasyprint
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse


ENGINE_AUTO = "auto"
ENGINE_CHROMIUM = "chromium"
ENGINE_WKHTMLTOPDF = "wkhtmltopdf"
ENGINE_WEASYPRINT = "weasyprint"

SUPPORTED_ENGINES = [
    ENGINE_AUTO,
    ENGINE_CHROMIUM,
    ENGINE_WKHTMLTOPDF,
    ENGINE_WEASYPRINT,
]

CHROMIUM_CANDIDATES = [
    "chromium",
    "chromium-browser",
    "google-chrome",
    "google-chrome-stable",
    "chrome",
    "chrome.exe",
    "msedge",
    "microsoft-edge",
    "msedge.exe",
]

WEASYPRINT_CANDIDATES = [
    "weasyprint",
    str((Path.cwd() / ".venv" / "bin" / "weasyprint").resolve()),
]


class ConvertError(RuntimeError):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert HTML/HTM file (or URL) to PDF without any LLM."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Input HTML/HTM file path or http(s) URL.",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output PDF path.",
    )
    parser.add_argument(
        "--engine",
        default=ENGINE_AUTO,
        choices=SUPPORTED_ENGINES,
        help="Rendering engine. Default: auto.",
    )
    parser.add_argument(
        "--timeout-sec",
        type=int,
        default=60,
        help="Conversion command timeout in seconds. Default: 60.",
    )
    return parser.parse_args()


def is_http_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def resolve_input_target(raw_input: str) -> str:
    if is_http_url(raw_input):
        return raw_input

    path = Path(raw_input).expanduser().resolve()
    if not path.exists():
        raise ConvertError(f"Input file not found: {path}")
    if not path.is_file():
        raise ConvertError(f"Input must be a file or URL: {path}")
    return path.as_uri()


def ensure_output_path(output: str) -> Path:
    out_path = Path(output).expanduser().resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.suffix.lower() != ".pdf":
        raise ConvertError(f"Output must end with .pdf: {out_path}")
    return out_path


def command_exists(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def find_chromium_binary() -> str | None:
    env_override = (
        os.environ.get("HTML2PDF_BROWSER")
        or os.environ.get("CHROME_BIN")
        or os.environ.get("EDGE_BIN")
    )
    if env_override and Path(env_override).exists():
        return env_override

    for candidate in CHROMIUM_CANDIDATES:
        if command_exists(candidate):
            return candidate

    # Common Windows install locations for Chrome/Edge when not in PATH.
    windows_paths = [
        Path(os.environ.get("LOCALAPPDATA", ""))
        / "Google/Chrome/Application/chrome.exe",
        Path(os.environ.get("PROGRAMFILES", ""))
        / "Google/Chrome/Application/chrome.exe",
        Path(os.environ.get("PROGRAMFILES(X86)", ""))
        / "Google/Chrome/Application/chrome.exe",
        Path(os.environ.get("LOCALAPPDATA", ""))
        / "Microsoft/Edge/Application/msedge.exe",
        Path(os.environ.get("PROGRAMFILES", ""))
        / "Microsoft/Edge/Application/msedge.exe",
        Path(os.environ.get("PROGRAMFILES(X86)", ""))
        / "Microsoft/Edge/Application/msedge.exe",
        Path.home() / "AppData/Local/Google/Chrome/Application/chrome.exe",
        Path.home() / "AppData/Local/Microsoft/Edge/Application/msedge.exe",
    ]
    for path in windows_paths:
        if path.exists():
            return str(path)
    return None


def run_command(cmd: list[str], timeout_sec: int) -> None:
    try:
        subprocess.run(
            cmd,
            check=True,
            timeout=timeout_sec,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        raise ConvertError(
            f"Command failed ({' '.join(cmd)}):\n"
            f"exit={exc.returncode}\n"
            f"stderr={exc.stderr.strip()}"
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise ConvertError(
            f"Command timed out after {timeout_sec}s: {' '.join(cmd)}"
        ) from exc


def try_chromium(input_target: str, output_pdf: Path, timeout_sec: int) -> None:
    browser = find_chromium_binary()
    if not browser:
        raise ConvertError(
            "No Chromium-based browser found (Chrome/Edge). "
            "Install Chrome or Edge, add it to PATH, or set HTML2PDF_BROWSER "
            "to the full browser .exe path."
        )

    cmd = [
        browser,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        f"--print-to-pdf={str(output_pdf)}",
        "--print-to-pdf-no-header",
        input_target,
    ]
    run_command(cmd, timeout_sec=timeout_sec)


def try_wkhtmltopdf(input_target: str, output_pdf: Path, timeout_sec: int) -> None:
    if not command_exists("wkhtmltopdf"):
        raise ConvertError("wkhtmltopdf not found in PATH.")

    cmd = [
        "wkhtmltopdf",
        "--enable-local-file-access",
        input_target,
        str(output_pdf),
    ]
    run_command(cmd, timeout_sec=timeout_sec)


def try_weasyprint(input_target: str, output_pdf: Path, timeout_sec: int) -> None:
    binary = None
    for candidate in WEASYPRINT_CANDIDATES:
        if command_exists(candidate) or Path(candidate).exists():
            binary = candidate
            break

    if not binary:
        raise ConvertError("weasyprint CLI not found (PATH or .venv/bin).")

    cmd = [
        binary,
        input_target,
        str(output_pdf),
    ]
    run_command(cmd, timeout_sec=timeout_sec)


def convert(
    input_target: str,
    output_pdf: Path,
    engine: str,
    timeout_sec: int,
) -> str:
    engines = (
        [ENGINE_CHROMIUM, ENGINE_WKHTMLTOPDF, ENGINE_WEASYPRINT]
        if engine == ENGINE_AUTO
        else [engine]
    )
    errors: list[str] = []

    for current in engines:
        try:
            if current == ENGINE_CHROMIUM:
                try_chromium(input_target, output_pdf, timeout_sec)
            elif current == ENGINE_WKHTMLTOPDF:
                try_wkhtmltopdf(input_target, output_pdf, timeout_sec)
            elif current == ENGINE_WEASYPRINT:
                try_weasyprint(input_target, output_pdf, timeout_sec)
            else:
                raise ConvertError(f"Unsupported engine: {current}")
            return current
        except ConvertError as err:
            errors.append(f"{current}: {err}")

    joined = "\n\n".join(errors)
    raise ConvertError(
        "All conversion engines failed.\n"
        "Install at least one renderer (Chromium, wkhtmltopdf, or weasyprint).\n\n"
        f"Details:\n{joined}"
    )


def main() -> int:
    args = parse_args()
    try:
        input_target = resolve_input_target(args.input)
        output_pdf = ensure_output_path(args.output)
        used_engine = convert(
            input_target=input_target,
            output_pdf=output_pdf,
            engine=args.engine,
            timeout_sec=args.timeout_sec,
        )
        print(f"Success: generated {output_pdf} using engine={used_engine}")
        return 0
    except ConvertError as err:
        print(f"Error: {err}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
