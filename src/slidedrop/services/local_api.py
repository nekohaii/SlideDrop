from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from slidedrop.engines.libreoffice import LibreOfficeStrategy
from slidedrop.engines.options import ConversionOptions
from slidedrop.manager import ConversionManager
from slidedrop.models import FileStatus

_JSON_CT = "application/json; charset=utf-8"

# Listen address is forced to loopback only so the conversion API is not reachable from the LAN.
_LOOPBACK_BIND = "127.0.0.1"


def _allow_client(host: str) -> bool:
    normalized = host.lower().strip()
    return normalized in {"127.0.0.1", "::1", "localhost"} or normalized.startswith(
        "::ffff:127.0.0.1",
    )


class LocalConvertHTTPServer(ThreadingHTTPServer):
    def verify_request(self, request, client_address):  # type: ignore[override]
        host = client_address[0]
        return _allow_client(host)


class Handler(BaseHTTPRequestHandler):
    server_version = "SlideDropLocalAPI/1.0"

    def log_message(self, fmt: str, *args) -> None:
        return

    def _send_json(self, status: int, payload: object) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", _JSON_CT)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path == "/health":
            self._send_json(200, {"ok": True})
            return
        self._send_json(404, {"error": "not_found"})

    def do_POST(self) -> None:
        if self.path != "/v1/convert":
            self._send_json(404, {"error": "not_found"})
            return

        length_header = self.headers.get("Content-Length")
        if not length_header:
            self._send_json(400, {"error": "missing_content_length"})
            return
        try:
            length = int(length_header)
        except ValueError:
            self._send_json(400, {"error": "bad_content_length"})
            return

        raw = self.rfile.read(length)
        try:
            body = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            self._send_json(400, {"error": "invalid_json"})
            return

        paths_raw = body.get("paths")
        if not isinstance(paths_raw, list) or not paths_raw:
            self._send_json(400, {"error": "paths_required"})
            return

        paths = [Path(str(p)).expanduser().resolve() for p in paths_raw]
        soffice = body.get("soffice")
        timeout = int(body.get("timeout", 300))
        skip_if_unchanged = bool(body.get("skip_if_unchanged", False))
        export_notes = bool(body.get("export_notes", False))
        extra = body.get("pdf_extra")
        if extra is not None and not isinstance(extra, dict):
            self._send_json(400, {"error": "pdf_extra_must_be_object"})
            return

        engine_path = Path(str(soffice)).expanduser().resolve() if soffice else None
        manager = ConversionManager(engine=LibreOfficeStrategy(engine_path, timeout_seconds=timeout))
        manager.add_paths(paths)

        options = ConversionOptions(
            timeout_seconds=max(30, timeout),
            skip_if_unchanged=skip_if_unchanged,
            export_notes_pages=export_notes,
            impress_pdf_extra_properties=dict(extra or {}),
        )

        results: list[dict] = []
        exit_failed = False
        for item in manager.convertable_items():
            result = manager.engine.convert(item, options)
            results.append(
                {
                    "source": str(item.source_path),
                    "success": result.success,
                    "pdf": str(result.output_pdf) if result.output_pdf else None,
                    "message": result.message,
                }
            )
            if result.success:
                item.status = FileStatus.DONE
                item.output_pdf = result.output_pdf
            else:
                exit_failed = True
                item.status = FileStatus.FAILED

        self._send_json(200 if not exit_failed else 207, {"results": results})


def serve_convert_api(port: int = 8765) -> None:
    """Bind strictly to IPv4 loopback; rejects non-local clients at accept time."""
    server = LocalConvertHTTPServer((_LOOPBACK_BIND, port), Handler)
    print(f"SlideDrop local API on http://{_LOOPBACK_BIND}:{port} (POST /v1/convert, GET /health)")
    print("Loopback only — not exposed on your LAN. OS firewall prompts may still appear once.")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.shutdown()
        server.server_close()
