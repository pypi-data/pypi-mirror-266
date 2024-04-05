import logging
from typing import Dict, Any
from tg.plugins import TgMessage, TgPlugin


class TgCaption(TgPlugin):
    id_ = "caption"

    def __init__(self, data: Dict[str, Any]) -> None:
        super().__init__(data)
        self.caption = self.data
        logging.info(self.caption)

    def modify(self, tm: TgMessage) -> TgMessage:
        tm.text = f"{self.caption['header']}{tm.text}{self.caption['footer']}"
        return tm
