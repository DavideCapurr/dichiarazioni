#!/usr/bin/env python3
"""Check whether the backend can export DOCX templates to PDF."""
from pathlib import Path
import shutil


def main() -> None:
    soffice = (
        shutil.which("soffice")
        or shutil.which("libreoffice")
        or _existing_path("/Applications/LibreOffice.app/Contents/MacOS/soffice")
    )
    pages = Path("/Applications/Pages.app").exists() and shutil.which("osascript")

    if soffice:
        print(f"OK: LibreOffice disponibile: {soffice}")
        return
    if pages:
        print("OK: Pages.app disponibile come fallback locale macOS")
        return

    raise SystemExit(
        "ERRORE: nessun converter DOCX->PDF trovato. "
        "Installa LibreOffice sul server/backend."
    )


def _existing_path(path: str) -> str | None:
    candidate = Path(path)
    return str(candidate) if candidate.exists() else None


if __name__ == "__main__":
    main()
