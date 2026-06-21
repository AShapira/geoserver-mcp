import subprocess
import sys

import pytest


def test_package_imports() -> None:
    import geoserver_mcp

    assert geoserver_mcp.__version__ == "0.1.0"


def test_server_app_factory_constructs_without_geoserver_config() -> None:
    from geoserver_mcp.server import create_app

    app = create_app()

    assert app is not None
    assert app.name == "GeoServer MCP"


def test_module_entrypoint_starts_far_enough_to_report_version() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "geoserver_mcp", "--version"],
        capture_output=True,
        check=False,
        text=True,
    )

    assert result.returncode == 0
    assert "geoserver-mcp" in result.stdout


def test_invalid_env_port_reports_argparse_error(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    from geoserver_mcp.__main__ import build_parser

    monkeypatch.setenv("GEOSERVER_MCP_PORT", "not-a-port")

    with pytest.raises(SystemExit) as exc_info:
        build_parser().parse_args([])

    assert exc_info.value.code == 2
    assert "must be an integer" in capsys.readouterr().err


def test_out_of_range_env_port_reports_argparse_error(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    from geoserver_mcp.__main__ import build_parser

    monkeypatch.setenv("GEOSERVER_MCP_PORT", "65536")

    with pytest.raises(SystemExit) as exc_info:
        build_parser().parse_args([])

    assert exc_info.value.code == 2
    assert "must be between 1 and 65535" in capsys.readouterr().err


def test_invalid_env_transport_reports_argparse_error(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    from geoserver_mcp.__main__ import main

    monkeypatch.setenv("GEOSERVER_MCP_TRANSPORT", "bogus")

    with pytest.raises(SystemExit) as exc_info:
        main([])

    assert exc_info.value.code == 2
    assert "invalid choice" in capsys.readouterr().err
