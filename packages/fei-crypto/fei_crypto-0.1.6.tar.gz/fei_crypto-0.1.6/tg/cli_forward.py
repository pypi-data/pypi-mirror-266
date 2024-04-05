import logging
import sys
from enum import Enum
from typing import Optional

import typer
from rich import console, traceback
from rich.logging import RichHandler
from verlat import latest_release

from fei_crypto import __version__
from tg import config
from telethon import TelegramClient
from tg import storage as stg

from tg.parse import proxy_parse_tuple
from tg.utils import clean_session_files

tg_forward_app = typer.Typer(add_completion=False)
con = console.Console()
TG_CONFIG_FILE_NAME = ""


def topper():
    version_check()
    print("\n")


class Mode(str, Enum):
    """works in two modes."""

    PAST = "past"
    LIVE = "live"


def verbosity_callback(value: bool):
    """Set logging level."""
    traceback.install()
    if value:
        level = logging.INFO
    else:
        level = logging.WARNING
    logging.basicConfig(
        level=level,
        format="%(message)s",
        handlers=[
            RichHandler(
                rich_tracebacks=True,
                markup=True,
            )
        ],
    )
    topper()
    logging.info("Verbosity turned on! This is suitable for debugging")


def version_callback(value: bool):
    """Show current version and exit."""

    if value:
        con.print(__version__)
        raise typer.Exit()


def version_check():
    latver = latest_release("fei-crypto").version
    if __version__ != latver:
        con.print(
            f"fei-crypto.tgf has a newer release {latver} availaible!\
            \nVisit https://pypi.org/project/fei-crypto",
            style="bold yellow",
        )
    else:
        con.print(f"Running latest fei-crypto.tgf version {__version__}", style="bold green")


@tg_forward_app.command()
def main(
        mode: Mode = typer.Argument(
            ..., help="Choose the mode in which you want to run fei-crypto.tgf",
            # envvar="TGF_MODE"
        ),
        config_path: str = typer.Option(
            'tg.config.json',
            '--config-path',
            '-c',
            help='config file path,default:\"tg.config.json\"',
        ),
        verbose: Optional[bool] = typer.Option(  # pylint: disable=unused-argument
            None,
            "--loud",
            "-l",
            callback=verbosity_callback,
            # envvar="LOUD",
            help="Increase output verbosity.",
        ),
        version: Optional[bool] = typer.Option(  # pylint: disable=unused-argument
            None,
            "--version",
            "-v",
            callback=version_callback,
            help="Show version and exit.",
        ),
):
    clean_session_files()
    config.CONFIG_FILE_NAME = config_path
    stg.CONFIG_TYPE = config.detect_config_type()
    config.CONFIG = config.read_config()

    session = config.get_session()

    if mode == Mode.PAST and config.CONFIG.login.user_type != 1:
        logging.warning(
            "You cannot use bot account for tgf past mode. Telegram does not allow bots to access chat history."
        )
        return

    client = TelegramClient(
        session,
        config.CONFIG.login.API_ID,
        config.CONFIG.login.API_HASH,
        sequential_updates=config.CONFIG.live.sequential_updates,
        proxy=proxy_parse_tuple(config.CONFIG.login.PROXY)
    )
    if config.CONFIG.login.user_type == 0:
        if config.CONFIG.login.BOT_TOKEN == "":
            logging.warning("Bot token not found, but login type is set to bot.")
            sys.exit()
        client.start(bot_token=config.CONFIG.login.BOT_TOKEN)

    if mode == Mode.PAST:
        from tg.past import forward_job
        with client:
            client.loop.run_until_complete(forward_job(client))
        pass
    elif mode == Mode.LIVE:
        from tg.live import start_sync
        with client:
            client.loop.run_until_complete(start_sync(client))
