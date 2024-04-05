from typing import Sequence

from telethon.client import TelegramClient
from telethon.hints import EntityLike

from tg.config import CONFIG
from tg.plugin_models import FileType
from tg.utils import cleanup, stamp
from telethon.tl.custom.message import Message


class TgMessage:
    def __init__(self, message: Message) -> None:
        self.message = message
        self.text = self.message.text
        self.raw_text = self.message.raw_text
        self.sender_id = self.message.sender_id
        self.file_type = self.guess_file_type()
        self.new_file = None
        self.cleanup = False
        self.reply_to = None
        self.file = None

    async def get_file(self) -> str:
        """Downloads the file in the message and returns the path where its saved."""
        if self.file_type == FileType.NOFILE:
            raise FileNotFoundError("No file exists in this message.")
        self.file = stamp(await self.message.download_media(""), self.sender_id)
        return self.file

    def guess_file_type(self) -> FileType:
        for f in FileType:
            if f == FileType.NOFILE:
                return f
            try:
                obj = getattr(self.message, f.value)
            except AttributeError:
                continue
            if obj:
                return f

    def clear(self) -> None:
        if self.new_file and self.cleanup:
            cleanup(self.new_file)
            self.new_file = None


async def send_message(recipient: EntityLike, tm: TgMessage) -> Sequence[Message] | Message:
    """Forward or send a copy, depending on config."""
    client: TelegramClient = tm.message.client
    sender = await tm.message.get_sender()

    if tm.message.is_group:
        last_name = ''
        if sender.last_name is not None and sender.last_name != '':
            last_name = ' ' + sender.last_name
        from_user = f'【{sender.first_name}{last_name}】'
        tm.text = from_user + tm.text

    if CONFIG.show_forwarded_from:
        return await client.forward_messages(recipient, tm.message)
    if tm.new_file:
        message = await client.send_file(
            recipient, tm.new_file, caption=tm.text, reply_to=tm.reply_to
        )
        return message
    tm.message.text = tm.text
    return await client.send_message(recipient, tm.message, reply_to=tm.reply_to)
