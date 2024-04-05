import logging
from tg.plugins import TgMessage, TgPlugin
from tg.utils import replace


class TgReplace(TgPlugin):
    id_ = "replace"

    def __init__(self, data):
        super().__init__(data)
        self.replace = self.data
        logging.info(self.replace)

    def modify(self, tm: TgMessage) -> TgMessage:
        msg_text: str = tm.text
        if not msg_text:
            return tm
        for original, new in self.replace.text.items():
            msg_text = replace(original, new, msg_text, self.replace.regex)
        tm.text = msg_text
        return tm
