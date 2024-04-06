from .command import get_command_handlers_telethon, get_command_handlers_pyrogram
from .callback import get_callback_handlers_telethon, get_callback_handlers_pyrogram
from .incoming_msg import get_incoming_msg_handlers_telethon, get_incoming_msg_handlers_pyrogram
from .inline import get_inline_handler


def get_telethon_handlers(val):
    ALL_HANDLERS_TELETHON = {}
    ALL_HANDLERS_TELETHON.update(get_command_handlers_telethon(val))
    ALL_HANDLERS_TELETHON.update(get_callback_handlers_telethon(val))
    ALL_HANDLERS_TELETHON.update(get_incoming_msg_handlers_telethon(val))
    return ALL_HANDLERS_TELETHON

def get_pyrogram_handlers(val):
    ALL_HANDLERS_PYROGRAM = {}
    ALL_HANDLERS_PYROGRAM.update(get_command_handlers_pyrogram(val))
    ALL_HANDLERS_PYROGRAM.update(get_callback_handlers_pyrogram(val))
    ALL_HANDLERS_PYROGRAM.update(get_incoming_msg_handlers_pyrogram(val))
    ALL_HANDLERS_PYROGRAM.update(get_inline_handler(val))
    return ALL_HANDLERS_PYROGRAM

