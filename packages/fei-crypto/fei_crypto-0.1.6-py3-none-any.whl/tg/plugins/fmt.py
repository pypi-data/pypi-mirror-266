import logging
from tg.plugin_models import STYLE_CODES, Style
from tg.plugins import TgMessage, TgPlugin


class TgFmt(TgPlugin):
    id_ = "fmt"

    def __init__(self, data) -> None:
        super().__init__(data)
        self.format = self.data
        logging.info(self.format)

    def modify(self, tm: TgMessage) -> TgMessage:
        if self.format['style'] is Style.PRESERVE:
            return tm
        msg_text: str = tm.raw_text
        if not msg_text:
            return tm
        style = STYLE_CODES.get(self.format['style'])
        tm.text = f"{style}{msg_text}{style}"
        return tm
