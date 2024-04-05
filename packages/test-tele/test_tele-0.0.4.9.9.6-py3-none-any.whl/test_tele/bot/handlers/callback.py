import re
import logging

from telethon import events, Button
from pyrogram import filters
from pyrogram.types import CallbackQuery
from pyrogram.handlers import CallbackQueryHandler

from test_tele.config_bot import BOT_CONFIG
from test_tele.bot.utils import registered_user
from test_tele.bot.bot_header import loop_message
from test_tele.features.pyrogram.pixiv import get_px_file
from test_tele.features.pyrogram.furry import get_fur_file
from test_tele.features.pyrogram.gelbooru import get_gb_file
from test_tele.features.pyrogram.realperson import get_nude_file
from test_tele.plugins import TgcfMessage


@registered_user
async def callback_get_message(event, is_premium:bool = False):
    """Handle callback for get messages"""
    try:
        pattern = r'gt(?:p|n)_(\w+)_(\d+)'
        text = event.data.decode('utf-8')
        match = re.match(pattern, text)
        id_post = 2

        if match:
            ent_chnl = match.group(1)
            id_post = int(match.group(2))

            if text.startswith("gtp_"):
                id_post -= 1
                message = await loop_message(event, ent_chnl, id_post, False)
            if text.startswith("gtn_"):
                id_post += 1
                message = await loop_message(event, ent_chnl, id_post)

            tm = TgcfMessage(message)
            msg_text = tm.text + f"\n\n👉 {BOT_CONFIG.bot_name} 👈 | `t.me/{ent_chnl}/{tm.message.id}`"
            return await event.edit(text=msg_text, file=message.media, buttons=[
                                Button.inline('◀️', f'gtp_{ent_chnl}_{tm.message.id}'),
                                Button.inline('▶️', f'gtn_{ent_chnl}_{tm.message.id}')
                            ])

    except Exception as err:
        logging.error(err)

    finally:
        raise events.StopPropagation


# Callback button from inline query result
    
async def callback_query_handler(app, callback_query: CallbackQuery):
    """Get callback query from inline keyboard"""
    handlers = {
        "md": None,
        "gb": get_gb_file,
        "px": get_px_file,
        "rp": get_nude_file,
        "fur": get_fur_file
        # "2d": get_vr_file
    }

    for prefix, handler in handlers.items():
        if callback_query.data.startswith(prefix):
            image_file = await handler(callback_query.data.replace(f"{prefix} ", ''))
            if callback_query.data.startswith("md"):
                await app.send_photo(callback_query.from_user.id, image_file)
            else:
                await app.send_document(callback_query.from_user.id, image_file)
            break
    else:
        pass


def get_callback_handlers_telethon(val) -> dict:
    """Get only callback handlers for telethon"""
    bot_handler_only = {
        "cb_get_post": (callback_get_message, events.CallbackQuery(pattern=r'gt(?:p|n)_')),
    }
    if val == 0: # bot
        return bot_handler_only
    return {}


def get_callback_handlers_pyrogram(val) -> dict:
    """Get only callback handlers for pyrogram"""
    cb_for_image = r"(?:md|gb|px|rp|fur|2d)"
    pyrogram_handler = {
        "callback_query": CallbackQueryHandler(callback_query_handler, filters.regex(cb_for_image)),
    }
    if val == 0:
        return pyrogram_handler
    return {}

