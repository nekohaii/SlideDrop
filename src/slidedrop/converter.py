from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

from .config import DEFAULT_LIBREOFFICE_PATH
from .models import QueueItem


@dataclass
class ConversionResult:
    success: bool
    output_pdf: Path | None
    message: str
    stdout: str = ""
    stderr: str = ""


class LibreOfficeConverter:
    def __init__(self, soffice_path: Path = DEFAULT_LIBREOFFICE_PATH) -> None:
        self.soffice_path = soffice_path

    def validate(self) -> tuple[bool, str]:
        if not self.soffice_path.exists():
            return False, f"LibreOffice was not found at: {self.soffice_path}"
        if not self.soffice_path.is_file():
            return False, f"LibreOffice path is not a file: {self.soffice_path}"
        return True, "LibreOffice found."

    def convert(self, item: QueueItem, high_quality: bool = False) -> ConversionResult:
        valid, message = self.validate()
        if not valid:
            return ConversionResult(False, None, message)

        if not item.source_path.exists():
            return ConversionResult(False, None, f"Input file does not exist: {item.source_path}")

        item.output_dir.mkdir(parents=True, exist_ok=True)
        output_pdf = item.output_dir / f"{item.source_path.stem}.pdf"

        convert_to = "pdf"
        if high_quality:
            # Kept conservative until Impress PDF filter parameters are verified.
            convert_to = "pdf"

        command = [
            str(self.soffice_path),
            "--headless",
            "--convert-to",
            convert_to,
            "--outdir",
            str(item.output_dir),
            str(item.source_path),
        ]

        try:
            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=300,
                check=False,
                shell=False,
            )
        except subprocess.TimeoutExpired as exc:
            return ConversionResult(
                False,
                None,
                f"Timed out while converting {item.source_path.name}.",
                stdout=exc.stdout or "",
                stderr=exc.stderr or "",
            )
        except OSError as exc:
            return ConversionResult(False, None, f"Could not start LibreOffice: {exc}")

        stdout = completed.stdout.strip()
        stderr = completed.stderr.strip()
        if completed.returncode != 0:
            details = stderr or stdout or f"LibreOffice exited with code {completed.returncode}."
            return ConversionResult(False, None, details, stdout=stdout, stderr=stderr)

        if not output_pdf.exists():
            details = stderr or stdout or "LibreOffice finished but no PDF was created."
            return ConversionResult(False, None, details, stdout=stdout, stderr=stderr)

        return ConversionResult(True, output_pdf, f"Created {output_pdf}", stdout=stdout, stderr=stderr)
