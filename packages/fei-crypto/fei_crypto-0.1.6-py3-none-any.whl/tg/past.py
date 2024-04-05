import asyncio
import json
from datetime import datetime, timedelta, timezone
import logging
import time
from telethon import TelegramClient
from telethon.errors.rpcerrorlist import FloodWaitError
from telethon.tl.custom.message import Message
from telethon.tl.patched import MessageService

from tg import config
from tg import storage as st
from tg.config import CONFIG, write_config
from tg.plugins import apply_plugins
from tg.message import send_message


async def forward_job(client: TelegramClient) -> None:
    me = await client.get_me()
    print(f'🛩️usd_id:{me.id}')
    print(f'🛩️usename:{me.username}')

    config.from_to = await config.load_from_to(client, config.CONFIG.forwards)
    forward: config.Forward
    time_diff = datetime.now(tz=timezone.utc) - timedelta(hours=1)
    while True:
        for from_to, forward in zip(config.from_to.items(), config.CONFIG.forwards):
            src, dest = from_to
            print(f'🛩️forwarding messages from 【{src}】 to {dest},offset_id:【{forward.offset}】')
            async for message in client.iter_messages(
                    src,
                    reverse=True,
                    offset_id=forward.offset,
                    offset_date=time_diff,
                    limit=100
            ):
                message: Message

                event = st.DummyEvent(message.chat_id, message.id)
                event_uid = st.EventUid(event)

                if isinstance(message, MessageService):
                    continue
                try:
                    tm = await apply_plugins(message)
                    if not tm:
                        continue
                    st.stored[event_uid] = {}

                    r_event_uid = None
                    if message.is_reply:
                        r_event = st.DummyEvent(
                            message.chat_id, message.reply_to_msg_id
                        )
                        r_event_uid = st.EventUid(r_event)
                    for d in dest:
                        if message.is_reply and r_event_uid in st.stored:
                            tm.reply_to = st.stored.get(r_event_uid).get(d)
                        fwded_msg = await send_message(d, tm)
                        st.stored[event_uid].update({d: fwded_msg.id})
                    tm.clear()
                    last_id = message.id
                    logging.info(f"forwarding message with id = {last_id}")
                    forward.offset = last_id
                    write_config(CONFIG, persist=False)
                    time.sleep(CONFIG.past.delay)
                    logging.info(f"slept for {CONFIG.past.delay} seconds")

                except FloodWaitError as fwe:
                    logging.info(f"Sleeping for {fwe}")
                    await asyncio.sleep(delay=fwe.seconds)
                except Exception as err:
                    logging.exception(err)

        time.sleep(60)
