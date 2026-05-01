from __future__ import annotations

import atexit
import os
import signal
import subprocess
from pathlib import Path

from ..models import QueueItem
from .base import ConversionResult
from .discovery import discover_libreoffice


_ACTIVE_PROCESSES: set[subprocess.Popen] = set()


def _cleanup_processes() -> None:
    for process in list(_ACTIVE_PROCESSES):
        if process.poll() is None:
            try:
                process.kill()
            except OSError:
                pass


atexit.register(_cleanup_processes)


class LibreOfficeStrategy:
    def __init__(self, soffice_path: Path | None = None, timeout_seconds: int = 300) -> None:
        self.soffice_path = discover_libreoffice(soffice_path)
        self.timeout_seconds = timeout_seconds

    def refresh_path(self, soffice_path: Path | None = None) -> None:
        self.soffice_path = discover_libreoffice(soffice_path)

    def validate(self) -> tuple[bool, str]:
        if not self.soffice_path:
            return False, "LibreOffice was not found. Open Settings and choose soffice.exe, or install LibreOffice."
        if not self.soffice_path.exists():
            return False, f"LibreOffice was not found at: {self.soffice_path}"
        if not self.soffice_path.is_file():
            return False, f"LibreOffice path is not a file: {self.soffice_path}"
        return True, f"LibreOffice found: {self.soffice_path}"

    def convert(self, item: QueueItem) -> ConversionResult:
        valid, message = self.validate()
        if not valid:
            return ConversionResult(False, None, message)

        if not item.source_path.exists():
            return ConversionResult(False, None, f"Input file does not exist: {item.source_path}")

        item.output_dir.mkdir(parents=True, exist_ok=True)
        output_pdf = item.output_dir / f"{item.source_path.stem}.pdf"
        command = [
            str(self.soffice_path),
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            str(item.output_dir),
            str(item.source_path),
        ]

        process_kwargs = {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP} if os.name == "nt" else {"start_new_session": True}
        process: subprocess.Popen | None = None
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=False,
                **process_kwargs,
            )
            _ACTIVE_PROCESSES.add(process)
            stdout, stderr = process.communicate(timeout=self.timeout_seconds)
        except subprocess.TimeoutExpired:
            if process:
                self._terminate_process(process)
            self._delete_invalid_pdf(output_pdf)
            return ConversionResult(False, None, f"Timed out while converting {item.source_path.name}.")
        except OSError as exc:
            return ConversionResult(False, None, f"Could not start LibreOffice: {exc}")
        finally:
            if process:
                _ACTIVE_PROCESSES.discard(process)

        stdout = (stdout or "").strip()
        stderr = (stderr or "").strip()
        if process and process.returncode != 0:
            self._delete_invalid_pdf(output_pdf, always=True)
            details = stderr or stdout or f"LibreOffice exited with code {process.returncode}."
            return ConversionResult(False, None, details, stdout=stdout, stderr=stderr)

        if not output_pdf.exists() or output_pdf.stat().st_size <= 0:
            self._delete_invalid_pdf(output_pdf)
            details = stderr or stdout or "LibreOffice finished but no valid PDF was created."
            return ConversionResult(False, None, details, stdout=stdout, stderr=stderr)

        return ConversionResult(True, output_pdf, f"Created {output_pdf}", stdout=stdout, stderr=stderr)

    @staticmethod
    def _terminate_process(process: subprocess.Popen) -> None:
        try:
            if os.name == "nt":
                process.kill()
            else:
                os.killpg(process.pid, signal.SIGTERM)
        except OSError:
            pass

    @staticmethod
    def _delete_invalid_pdf(path: Path, always: bool = False) -> None:
        try:
            if path.exists() and (always or path.stat().st_size <= 0):
                path.unlink()
        except OSError:
            pass
