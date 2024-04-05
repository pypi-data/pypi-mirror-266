import inspect
import logging
from importlib import import_module
from typing import Any, Dict

from telethon.tl.custom.message import Message

from tg.config import CONFIG
from tg.message import TgMessage

PLUGINS = CONFIG.plugins


class TgPlugin:
    id_ = "plugin"

    def __init__(self, data: Dict[str, Any]) -> None:
        self.data = data

    def modify(self, tm: TgMessage) -> TgMessage:
        """Modify the message here."""
        return tm


def load_plugins() -> Dict[str, TgPlugin]:
    """Load the plugins specified in config."""
    _plugins = {}
    for item in PLUGINS:
        plugin_id = item[0]
        if not item[1].check:
            continue

        plugin_class_name = f"Tg{plugin_id.title()}"
        plugin_module = None
        try:  # try to load first party plugin
            plugin_module = import_module("tg.plugins." + plugin_id)
        except ModuleNotFoundError:
            logging.error(
                f"{plugin_id} is not a first party plugin. Third party plugins are not supported."
            )
        else:
            logging.info(f"First party plugin {plugin_id} loaded!")

        try:
            plugin_class = getattr(plugin_module, plugin_class_name)
            if not issubclass(plugin_class, TgPlugin):
                logging.error(
                    f"Plugin class {plugin_class_name} does not inherit TgPlugin"
                )
                continue
            plugin: TgPlugin = plugin_class(item[1])
            if not plugin.id_ == plugin_id:
                logging.error(f"Plugin id for {plugin_id} does not match expected id.")
                continue
        except AttributeError:
            logging.error(f"Found plugin {plugin_id}, but plguin class not found.")
        else:
            logging.info(f"Loaded plugin {plugin_id}")
            _plugins.update({plugin.id_: plugin})
    return _plugins


async def apply_plugins(message: Message) -> TgMessage | None:
    """Apply all loaded plugins to a message."""
    tm = TgMessage(message)

    for _id, plugin in plugins.items():
        try:
            if inspect.iscoroutinefunction(plugin.modify):
                ntm = await plugin.modify(tm)
            else:
                ntm = plugin.modify(tm)
        except Exception as err:
            logging.error(f"Failed to apply plugin {_id}. \n {err} ")
        else:
            logging.info(f"Applied plugin {_id}")
            if not ntm:
                tm.clear()
                return None
    return tm


plugins = load_plugins()
