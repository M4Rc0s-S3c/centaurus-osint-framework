"""Installed command-line entrypoint for CENTAURUS."""

from centaurus.cli.app import app


def main() -> None:
    """Run the Typer command-line application."""

    app()
