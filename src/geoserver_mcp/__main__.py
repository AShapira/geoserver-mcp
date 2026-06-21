from __future__ import annotations

import argparse
import os
from collections.abc import Sequence

from geoserver_mcp import __version__
from geoserver_mcp.server import run_server

TRANSPORTS = ("stdio", "sse", "streamable-http")


def parse_port(value: str) -> int:
    try:
        port = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be an integer") from exc
    if not 1 <= port <= 65535:
        raise argparse.ArgumentTypeError("must be between 1 and 65535")
    return port


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="geoserver-mcp")
    parser.add_argument(
        "--transport",
        choices=TRANSPORTS,
        default=os.getenv("GEOSERVER_MCP_TRANSPORT", "stdio"),
        help="MCP transport to use.",
    )
    parser.add_argument(
        "--host",
        default=os.getenv("GEOSERVER_MCP_HOST", "127.0.0.1"),
        help="Host for HTTP-based transports.",
    )
    parser.add_argument(
        "--port",
        default=os.getenv("GEOSERVER_MCP_PORT", "8000"),
        type=parse_port,
        help="Port for HTTP-based transports.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"geoserver-mcp {__version__}",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.transport not in TRANSPORTS:
        parser.error(
            "argument --transport: invalid choice: "
            f"{args.transport!r} (choose from {', '.join(repr(item) for item in TRANSPORTS)})"
        )
    run_server(transport=args.transport, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
