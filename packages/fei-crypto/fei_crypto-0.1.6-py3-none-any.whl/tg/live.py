from telethon import TelegramClient, events, functions, types
from tg.bot import get_events
from tg import config, const
import logging
from tg import storage as st
from tg.message import send_message
from tg.plugins import apply_plugins


async def new_message_handler(event) -> None:
    chat_id = event.chat_id

    if chat_id not in config.from_to:
        return
    logging.info(f"New message received in {chat_id}")
    event_uid = st.EventUid(event)  # chart_id msg_id
    length = len(st.stored)
    exceeding = length - const.KEEP_LAST_MANY
    # stored dict 超过储存大小,删除旧数据
    if exceeding > 0:
        for key in st.stored:
            del st.stored[key]
            break

    dest = config.from_to.get(chat_id)
    tm = await apply_plugins(event.message)
    if not tm:
        return

    r_event_uid = None
    if event.is_reply:
        r_event = st.DummyEvent(chat_id, event.reply_to_msg_id)
        r_event_uid = st.EventUid(r_event)

    st.stored[event_uid] = {}
    for d in dest:
        if event.is_reply and r_event_uid in st.stored:
            tm.reply_to = st.stored.get(r_event_uid).get(d)
        fwded_msg = await send_message(d, tm)
        st.stored[event_uid].update({d: fwded_msg})
    tm.clear()


async def deleted_message_handler(event):
    chat_id = event.chat_id
    if chat_id not in config.from_to:
        return

    logging.info(f"🛩️ids:{event.deleted_ids}💢deleted in {chat_id}")

    for item in event.deleted_ids:
        event.id = item
        event_uid = st.EventUid(event)
        fwded_msgs = st.stored.get(event_uid)
        if fwded_msgs:
            for _, msg in fwded_msgs.items():
                await msg.delete()


async def edited_message_handler(event) -> None:
    message = event.message
    chat_id = event.chat_id
    if chat_id not in config.from_to:
        return

    logging.info(f"Message edited in {chat_id}")

    event_uid = st.EventUid(event)

    tm = await apply_plugins(message)

    if not tm:
        return

    fwded_msgs = st.stored.get(event_uid)

    if fwded_msgs:
        for _, msg in fwded_msgs.items():
            if config.CONFIG.live.delete_on_edit == message.text:
                await msg.delete()
                await message.delete()
            else:
                await msg.edit(tm.text)
        return

    dest = config.from_to.get(chat_id)

    for d in dest:
        await send_message(d, tm)
    tm.clear()


ALL_EVENTS = {
    "new": (new_message_handler, events.NewMessage()),
    "edited": (edited_message_handler, events.MessageEdited()),
    "deleted": (deleted_message_handler, events.MessageDeleted()),
}


async def start_sync(client: TelegramClient) -> None:
    me = await client.get_me()
    print(f'🛩️usd_id:{me.id}')
    print(f'🛩️usename:{me.username}')
    config.is_bot = await client.is_bot()
    print(f'🛩️is_bot:{config.is_bot}')
    command_events = get_events()

    await config.load_admins(client)

    ALL_EVENTS.update(command_events)

    for key, val in ALL_EVENTS.items():
        if config.CONFIG.live.delete_sync is False and key == "deleted":
            continue
        client.add_event_handler(*val)
        logging.info(f"Added event handler for {key}")

    if config.is_bot and const.REGISTER_COMMANDS:
        await client(
            functions.bots.SetBotCommandsRequest(
                scope=types.BotCommandScopeDefault(),
                lang_code="en",
                commands=[
                    types.BotCommand(command=key, description=value)
                    for key, value in const.COMMANDS.items()
                ],
            )
        )
    config.from_to = await config.load_from_to(client, config.CONFIG.forwards)
    await client.run_until_disconnected()
