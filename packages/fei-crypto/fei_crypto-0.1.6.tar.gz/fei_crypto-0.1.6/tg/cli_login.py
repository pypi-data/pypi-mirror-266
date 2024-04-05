from typing import Optional
import typer
from .login import login
from rich import console

from fei_crypto import __version__


tg_login_app = typer.Typer(add_completion=False)

con = console.Console()


def version_callback(value: bool):
    """Show current version and exit."""

    if value:
        con.print(__version__)
        raise typer.Exit()


@tg_login_app.command()
def main(
        api_id: int = typer.Option(
            ...,
            "--API_ID",
            help="API ID obtained from my.telegram.org",
            # envvar="TG_LOGIN_API_ID",
            prompt="Paste your API ID (input hidden)",
            hide_input=False,
        ),
        api_hash: str = typer.Option(
            ...,
            "--API_HASH",
            help="API HASH obtained from my.telegram.org",
            # envvar="TG_LOGIN_API_HASH",
            prompt="Paste your API HASH (input hidden)",
            hide_input=False,
        ),
        proxy: str = typer.Option(
            # proxy: str = typer.Option(
            "",
            "--PROXY",
            help="Set proxy.",
            # envvar="TG_LOGIN_PROXY",
            prompt="Optional! paste your proxy example:socks5://127.0.0.1:7890;",
            hide_input=False,
        ),
        version: Optional[bool] = typer.Option(  # pylint: disable=unused-argument
            None,
            "--version",
            "-v",
            callback=version_callback,
            help="Show version and exit.",
        ),
):
    """ A command line tool to login into Telegram with user or bot accounts. """

    login(api_id, api_hash, proxy)
