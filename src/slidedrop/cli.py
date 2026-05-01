from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from slidedrop.engines.libreoffice import LibreOfficeStrategy
from slidedrop.engines.options import ConversionOptions
from slidedrop.manager import ConversionManager
from slidedrop.models import FileStatus
from slidedrop.services.logging import configure_logging


def _cmd_gui(_args: argparse.Namespace | None = None) -> int:
    from slidedrop.ui import App

    configure_logging()
    App().mainloop()
    return 0


def _cmd_convert(args: argparse.Namespace) -> int:
    configure_logging()
    paths = [Path(p).expanduser().resolve() for p in args.paths]
    engine_path = Path(args.soffice).expanduser().resolve() if args.soffice else None
    manager = ConversionManager(engine=LibreOfficeStrategy(engine_path, timeout_seconds=args.timeout))
    added = manager.add_paths(paths)
    if not added:
        print("No PowerPoint files found.", file=sys.stderr)
        return 2

    extra_props: dict = {}
    if args.pdf_extra_json:
        extra_props = json.loads(args.pdf_extra_json)

    options = ConversionOptions(
        timeout_seconds=max(30, args.timeout),
        skip_if_unchanged=args.skip_unchanged,
        export_notes_pages=args.export_notes,
        impress_pdf_extra_properties=extra_props,
    )

    pending = manager.convertable_items()
    exit_code = 0
    for item in pending:
        result = manager.engine.convert(item, options)
        line = {
            "source": str(item.source_path),
            "success": result.success,
            "pdf": str(result.output_pdf) if result.output_pdf else None,
            "message": result.message,
        }
        print(json.dumps(line))
        if result.success:
            item.status = FileStatus.DONE
            item.output_pdf = result.output_pdf
            item.message = result.message
        else:
            item.status = FileStatus.FAILED
            item.message = result.message
            exit_code = 1

    return exit_code


def _cmd_api(args: argparse.Namespace) -> int:
    configure_logging()
    from slidedrop.services.local_api import serve_convert_api

    serve_convert_api(port=args.port)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="slidedrop", description="SlideDrop PowerPoint to PDF converter")
    sub = parser.add_subparsers(dest="command", required=True)

    p_gui = sub.add_parser("gui", help="Launch the desktop interface")
    p_gui.set_defaults(func=_cmd_gui)

    p_convert = sub.add_parser("convert", help="Convert paths headlessly (files or folders)")
    p_convert.add_argument("paths", nargs="+", help="Files or folders to scan")
    p_convert.add_argument("--soffice", help="Path to soffice executable")
    p_convert.add_argument("--timeout", type=int, default=300, help="Per-file LibreOffice timeout (seconds)")
    p_convert.add_argument("--skip-unchanged", action="store_true", help="Skip when PDF meta matches file hash")
    p_convert.add_argument("--export-notes", action="store_true", help="Include speaker notes pages for .pptx")
    p_convert.add_argument(
        "--pdf-extra-json",
        default="",
        help="Optional JSON merged into impress_pdf_Export properties for .pptx (advanced)",
    )
    p_convert.set_defaults(func=_cmd_convert)

    p_api = sub.add_parser(
        "api",
        help="Loopback-only HTTP JSON API (POST /v1/convert); binds 127.0.0.1",
    )
    p_api.add_argument(
        "--port",
        type=int,
        default=8765,
        help="TCP port (server always listens on 127.0.0.1 only)",
    )
    p_api.set_defaults(func=_cmd_api)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    func = getattr(args, "func", None)
    if func is None:
        parser.print_help()
        return 2
    return func(args)


if __name__ == "__main__":
    raise SystemExit(main())
