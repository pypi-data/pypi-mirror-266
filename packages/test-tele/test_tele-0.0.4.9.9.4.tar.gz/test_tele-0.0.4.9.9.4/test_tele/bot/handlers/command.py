import re
import yaml
import time
import asyncio
import logging

from telethon import events
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram import filters
from pyrogram.handlers import MessageHandler

from test_tele.bot.utils import (
    query, 
    get_args, 
    start_sending,
    remove_source,
    admin_protect,
    registered_user,
    display_forwards,
    get_command_prefix,
    get_command_suffix,
    model, image_model,
    config, CONFIG, write_config
)
from test_tele.bot.bot_header import get_entity
from test_tele.plugin_models import Style
from test_tele.config_bot import BOT_CONFIG
from test_tele.plugins import TgcfMessage

timeout = 60
proxies = None
web_pattern = r'https?:\/\/([\.\w]+)\.[a-z]{2,4}\/'

# Basic handlers

async def start_command_handler(event):
    """Handle the /start command"""
    event = event.message
    chat_id = event.chat_id

    try:
        if not query.read_datas('users', None, 'chat_id = %s', [chat_id]):
            user = await event.client.get_entity(chat_id)
            query.create_data(
                'users', 
                ['chat_id', 'username', 'firstname', 'is_subscriber', 'is_full_subscriber', 'is_block'], 
                [chat_id, user.username, user.first_name, 0, 0, 0]
            )
            query.create_data(
                'settings',
                ['lang', 'def_inline', 'caption', 'keyboard', 'chat_id'],
                ['en', 'Gelbooru', 1, 1, chat_id]
            )

        await event.respond(BOT_CONFIG.bot_messages.start)
    except:
        pass
    finally:
        raise events.StopPropagation


async def help_command_handler(event):
    """Handle the /help command."""

    await event.respond(BOT_CONFIG.bot_messages.bot_help)


async def report_command_handler(event):
    """Handle the /report command"""
    notes = """The command `/report` allows you to send a message to the bot Admin.

    Command: `/report`
    Usage: MESSAGE..

    **Example**
    `/report Bot is not responding. Not sure if you received this or not.. lol`
    """.replace(
        "    ", ""
    )

    try:
        args = get_args(event.message.text)
        if not args:
            raise ValueError(f"{notes}\n")
        
        tm = TgcfMessage(event.message)
        tm.text = f"**-= New Message =-**\nfrom: `{tm.message.chat_id}`\n———————————\n" + args
        tm.text += f"\n———————————\n#report"

        admin = query.read_datas('admins', ['chat_id'], "role = 'admin'")
        if admin:
            await start_sending(admin[0][0], tm)
            await event.respond("We have received your message. Please wait while the Admin attempts to fix it")
        
    except ValueError as err:
        await event.respond(str(err))
    finally:
        raise events.StopPropagation


# Forwarder handlers

@admin_protect
async def forward_command_handler(event):
    """Handle the `/forward` command."""
    notes = """The `/forward` command allows you to add a new forward.
    Example: suppose you want to forward from a to (b and c)

    ```/forward source: a
    dest: [b,c]
    ```
    a,b,c are chat ids
    """.replace("    ", "")

    try:
        args = get_args(event.message.text)
        if not args:
            raise ValueError(f"{notes}\n{display_forwards(config.CONFIG.forwards)}")

        parsed_args = yaml.safe_load(args)
        forward = config.Forward(**parsed_args)
        try:
            remove_source(forward.source, config.CONFIG.forwards)
        except:
            pass
        CONFIG.forwards.append(forward)
        try:
            config.from_to, config.reply_to = await config.load_from_to(config.client, config.CONFIG.forwards)
            logging.warning("bisa di pake cara ini..")
        except:
            logging.warning("error bos..")
            config.from_to, config.reply_to = await config.load_from_to(event.client, config.CONFIG.forwards)

        await event.respond("Success")
        write_config(config.CONFIG)
    except ValueError as err:
        await event.respond(str(err))
    except Exception as err:
        logging.error(err, exc_info=True)

    finally:
        raise events.StopPropagation


@admin_protect
async def remove_command_handler(event):
    """Handle the /remove command."""
    notes = """The `/remove` command allows you to remove a source from forwarding.
    Example: Suppose you want to remove the channel with id -100, then run

    `/remove source: -100`

    """.replace("    ", "")
    try:
        args = get_args(event.message.text)
        if not args:
            raise ValueError(f"{notes}\n{display_forwards(config.CONFIG.forwards)}")

        parsed_args = yaml.safe_load(args)
        source_to_remove = parsed_args.get("source")
        CONFIG.forwards = remove_source(source_to_remove, config.CONFIG.forwards)
        config.from_to, config.reply_to = await config.load_from_to(event.client, config.CONFIG.forwards)

        await event.respond("Success")
        write_config(config.CONFIG)
    except ValueError as err:
        await event.respond(str(err))
    except Exception as err:
        logging.error(err, exc_info=True)

    finally:
        raise events.StopPropagation


@admin_protect
async def style_command_handler(event):
    """Handle the /style command"""
    notes = """This command is used to set the style of the messages to be forwarded.

    Example: `/style bold`

    Options are preserve,normal,bold,italics,code, strike

    """.replace(
        "    ", ""
    )

    try:
        args = get_args(event.message.text)
        if not args:
            raise ValueError(f"{notes}\n")
        _valid = [item.value for item in Style]
        if args not in _valid:
            raise ValueError(f"Invalid style. Choose from {_valid}")
        CONFIG.plugins.fmt.style = args
        await event.respond("Success")
        write_config(CONFIG)
    except ValueError as err:
        await event.respond(str(err))

    finally:
        raise events.StopPropagation


# test 
@admin_protect
async def subscribe_channel_handler(event):
    """Handle /subscribe command"""
    notes = """
    This command is used to mirror posts from a channel to a topic group
    If you want to use it in a general group, use the /forward command instead

    Command: `/subscribe`
    Usage: [OPTIONS]..
    Options: USERNAME | CHANNEL_ID

    Note: Only use this command in selected topic group
    """.replace("    ", "")

    try:
        args = get_args(event.message.text)
        if not args:
            raise ValueError(f"{notes}\n")
        
        chat = await event.client.get_entity(event.chat_id)
        if not event.is_reply and not chat.megagroup:
            return
        
        topic_id = event.reply_to.reply_to_msg_id
        chat_id = chat.id
        
        new_fwd_dict = {
            'source': args,
            'dest': [f'-100{chat_id}/{topic_id}']
        }
        forward = config.Forward(**new_fwd_dict)
        try:
            remove_source(forward.source, config.CONFIG.forwards)
        except:
            pass
        CONFIG.forwards.append(forward)
        config.from_to, config.reply_to = await config.load_from_to(event.client, config.CONFIG.forwards)
        write_config(config.CONFIG)

        msg = await event.reply(f"Successfully subscribed to {args}\nUse /remove to unsubscribe\n{display_forwards(config.CONFIG.forwards)}")
        time.sleep(5)
        await event.client.delete_messages(chat_id, [msg.id, event.message.id])
        
    except ValueError as err:
        await event.reply(str(err))
    except Exception as e:
        logging.error(e, exc_info=True)

    finally:
        raise events.StopPropagation


# Additional handlers for ttloli_bot

@admin_protect
async def respond_command_handler(event):
    """
    Handle the /reply command handler

    Usage:
        /reply [user_id].
    """
    
    try:
        args = get_args(event.message.text)
        if not args:
            return

        tm = TgcfMessage(event.message)
        
        matches = re.match(r'(\d+)\s(.+)', args, re.DOTALL)
        id_user = matches.group(1)
        isi_pesan = matches.group(2)

        tm.text = f'Admin says: "{isi_pesan}"'
        await start_sending(int(id_user), tm)

    except Exception as err:
        logging.error(err)
    finally:
        raise events.StopPropagation


@registered_user
async def get_message_command_handler(event, is_premium:bool = False):
    """Handle the command /get"""
    notes = """The command `/get` is used to retrieve messages from a public channel or group even if forwarding is not allowed.

    Command: `/get`
    Usage: LINK..
    Note: copy the message link from the public channel or group, and paste it here as argument
    
    **Example** 
    `/get https://t.me/username/post_id`
    """.replace("    ", "")

    try:
        args = get_args(event.message.text)

        if not args:
            raise ValueError(f"{notes}\n")

        pattern = r'(t.me/(c/)?|)(-?\w+)/(\d+)'
        match = re.search(pattern, args)

        if match:
            entity = str(match.group(3))
            ids = int(match.group(4))
            chat = await get_entity(event, entity)

            if chat is None:
                raise ValueError("Unable to get post")

            message = await event.client.get_messages(chat, ids=ids)
            caption = message.text + f"\n\n👉 {BOT_CONFIG.bot_name} 👈"

            if message.grouped_id is not None and message.media:
                from test_tele.live_pyrogram import BOT as app
                await app.copy_media_group(
                    event.message.chat_id, 
                    chat.username, 
                    message.id, 
                    captions=caption,
                    disable_notification=True,
                    reply_to_message_id=event.message.id
                )
            elif message.grouped_id is None and message.media:
                from test_tele.live_pyrogram import BOT as app
                await app.copy_message(
                    event.message.chat_id, 
                    chat.username, 
                    message.id, 
                    caption=caption,
                    disable_notification=True,
                    reply_to_message_id=event.message.id
                )

    except ValueError as err:
        await event.respond(str(err))

    except Exception as err:
        await event.respond("Something's wrong! Please report it to the bot Admin")
        logging.error(err, exc_info=True)

    finally:
        raise events.StopPropagation


# Helper for reverse image search

async def saucenao_image_search(file_path, url:str = None) -> list:
    """Image search using saucenao"""
    from PicImageSearch import SauceNAO

    ehentai = SauceNAO(api_key=BOT_CONFIG.apis.saucenao_api, numres=3, minsim=80)
    resp = await ehentai.search(url=url, file=file_path)
    
    results = []
    seen_categories = set()

    if resp.status_code == 200:
        for selected in (i for i in resp.raw if i.title and i.url and i.similarity > 80):
            match = re.search(web_pattern, selected.url)
            if match:
                category = match.group(1).replace('www.', '').split('.')[0].capitalize()
                if category in seen_categories:
                    continue
                seen_categories.add(category)
            else:
                category = 'Unknown'

            my_dict = {
                "title": selected.title,
                "url": selected.url,
                "category": category,
                "author": selected.author,
                "author_url": selected.author_url,
            }
            results.append(my_dict)

        return results
    else:
        return await ascii_image_search(file_path, url)


async def ascii_image_search(file_path, url:str = None) -> list:
    """Image search using ASCII2D"""
    from PicImageSearch import Ascii2D

    ascii2d = Ascii2D(proxies=proxies)
    resp = await ascii2d.search(url=url, file=file_path)
    
    results = []
    seen_categories = set()

    for selected in (i for i in resp.raw if (i.title or i.url_list) and i.url):
        match = re.search(web_pattern, selected.url)
        if match:
            category = match.group(1).replace('www.', '').split('.')[0].capitalize()
            if category in seen_categories:
                continue
            seen_categories.add(category)
        else:
            category = 'Unknown'

        my_dict = {
            "title": selected.title,
            "url": selected.url,
            "category": category,
            "author": selected.author,
            "author_url": selected.author_url,
        }
        results.append(my_dict)

    return results


async def ehentai_image_search(file_path, url:str = None) -> list:
    """Image search using e-hentai"""
    from PicImageSearch import EHentai, Network

    ehentai = EHentai(proxies=proxies, cookies=BOT_CONFIG.apis.ehentai_cookies, timeout=timeout)
    resp = await ehentai.search(url=url, file=file_path)
    
    results = []
    seen_categories = set()

    for selected in (i for i in resp.raw if i.title and i.url):
        match = re.search(web_pattern, selected.url)
        if match:
            category = match.group(1).replace('www.', '').split('.')[0].capitalize()
            if category in seen_categories:
                continue
            seen_categories.add(category)
        else:
            category = 'Unknown'

        my_dict = {
            "title": selected.title,
            "url": selected.url,
            "category": category
        }
        results.append(my_dict)

    return results


async def search_images(file_path, url:str = None, command: bool = False) -> list:
    """Global function for search images"""

    if command:
        resp_ascii, resp_ehentai = await asyncio.gather(
            saucenao_image_search(file_path, url), 
            ehentai_image_search(file_path, url)
        )
        resp = resp_ascii + resp_ehentai
    else:
        resp = await ehentai_image_search(file_path, url)

    return resp


# Helper to download media in message and store it as byte
        
async def download_media_bytes(app, message: Message):
    """Downloads media from a message and returns its bytes."""

    file = await app.download_media(message, in_memory=True)
    return bytes(file.getbuffer())


# Incoming message containing command /sauce 

async def sauce_command_handler(app, message: Message):
    """Handles the /sauce command."""
    notes = """The command /sauce is used to search for the source or origin of the image being replied to.

    Command: `/sauce`
    Note: reply to message with media (preferably 2D/anime picture)
    """.replace("    ", "")

    try:
        if message.text == "/sauce" and not message.reply_to_message_id:
            raise ValueError(f"{notes}\n")
        
        if message.text == "/sauce":
            replied_msg = await app.get_messages(
                message.chat.id, message.reply_to_message_id
            )
            file_bytes = await download_media_bytes(app, replied_msg)
            resp = await search_images(file_bytes, command=True)
            if resp:
                author = f"[{resp[0]['author']}]({resp[0]['author_url']})" if resp[0]['author'] and resp[0]['author_url'] else 'Unknown'
            msg_to_send = (
                f"**[{resp[0]['title']}]({resp[0]['url']})**\n"
                f"Author: {author}\n"
            ) if resp else "Sorry, no matches were found"

            await send_response(msg_to_send, message, resp)
        elif message.photo and not message.outgoing:
            if message.media_group_id:
                msg_list = await message.get_media_group()
                for per_msg in msg_list:
                    file_bytes = await download_media_bytes(app, per_msg)
                    resp = await search_images(file_bytes)
                    if resp:
                        msg_to_send = (
                            "The full version is found in :\n"
                            f"{resp[0]['title']}\n"
                            "Initiating synchronization, Please wait..\n"
                        )
                        msg = await send_response(msg_to_send, message, resp)
                    # do something about ex-hent to telegraph here
            else:
                file_bytes = await download_media_bytes(app, message)
                resp = await search_images(file_bytes)
                if resp:
                    msg_to_send = (
                        "The full version is found in :\n"
                        f"{resp[0]['title']}\n"
                        "Initiating synchronization, Please wait..\n"
                    )
                    msg = await send_response(msg_to_send, message, resp)
                # do something about ex-hent to telegraph here

    except ValueError as err:
        await app.send_message(message.from_user.id, str(err))

    except Exception as err:
        logging.error(err, exc_info=True)
    finally:
        raise message.stop_propagation()


async def send_response(msg_to_send, message: Message, resp = None) -> Message:
    """Sends the response message with formatted text and reply markup."""
    reply_markup = await get_reply_markup(resp)
    sent_msg = await message.reply(
        msg_to_send,
        disable_web_page_preview=True,
        disable_notification=True,
        reply_to_message_id=message.id,
        reply_markup=reply_markup,
    )
    return sent_msg


async def get_reply_markup(results: list):
    """Returns an InlineKeyboardMarkup object based on the given URL."""
    buttons = []
    supported_url = ['pixiv']

    if results:
        for i, res in enumerate(results):
            buttons.append(
                [
                    InlineKeyboardButton(res['category'], url=res['url'])
                ]
            )
            if res['category'].lower() in supported_url:
                if 'pixiv' in res['category'].lower():
                    id_author = res['author_url'].replace("https://www.pixiv.net/users/", "")
                    id_art = res['url'].replace("https://www.pixiv.net/artworks/", "")
                    buttons[i].insert(0, InlineKeyboardButton("👤🔄", switch_inline_query_current_chat=f".px id:{id_author}"))
                    buttons[i].insert(2, InlineKeyboardButton("🔗🔄", switch_inline_query_current_chat=f".px {id_art}"))

        return InlineKeyboardMarkup(buttons)
    return None


# Handler for replying to existed message

@registered_user
async def get_id_command_handler(event, is_premium: bool = False):
    """Handle the /id command"""

    try:
        args = get_args(event.message.text)

        if not args and CONFIG.login.user_type == 1:
            tm = TgcfMessage(event.message)
            tm.text = ""
            i = 0

            async for dialog in event.client.iter_dialogs():
                if dialog.is_channel:
                    i += 1
                    if i <= 80:
                        ch_id = f"`{str(dialog.id)}`"
                        ch_name = str(dialog.name).replace("`", "'")
                        tm.text += ch_id + " 👉 " + ch_name + "\n"
                    else:
                        await start_sending(tm.message.chat_id, tm)
                        tm.text = ""
                        i = 0
            
            await start_sending(tm.message.chat_id, tm)

        message = await event.message.get_reply_message()
        await event.reply(f"```{message.stringify()}```")

    except Exception as err:
        logging.error(err)
        message = await event.message.get_reply_message()
        await event.reply(f"```{message.stringify()}```")

    finally:
        raise events.StopPropagation


@registered_user
async def add_tag_command_handler(event, is_premium: bool = False):
    """Handling /addtag command"""
    notes = """This command is used to add hashtags to an existed message sent by me.

    Example: `/addtag news link`
    Usage: Reply to a message

    """.replace(
        "    ", ""
    )
    try:
        args = get_args(event.message.text)
        if not args or not event.is_reply:
            raise ValueError(f"{notes}\n")
        
        msg = await event.get_reply_message()
        args = args.split()
        tags = []
        for arg in args:
            tags.append(f'#{arg.lower()}')

        await event.client.edit_message(event.message.chat_id, msg.id, msg.text + "\n" + (" ").join(tags))
        await event.client.delete_messages(event.message.chat_id, event.message.id)

    except ValueError as err:
        await event.respond(str(err))
    except Exception as err:
        logging.error(err)


# Assign command handler

def get_command_handlers_telethon(val) -> dict:
    """Get only command handlers for telethon"""
    _ = get_command_prefix(val)
    u = get_command_suffix(val)
    command_handlers = {
        "start": (start_command_handler, events.NewMessage(pattern=f"{_}start{u}")),
        "help": (help_command_handler, events.NewMessage(pattern=f"{_}help{u}")), 
        "forward": (forward_command_handler, events.NewMessage(pattern=f"{_}forward")),
        "remove": (remove_command_handler, events.NewMessage(pattern=f"{_}remove")),
        "style": (style_command_handler, events.NewMessage(pattern=f"{_}style")),
        "get_id": (get_id_command_handler, events.NewMessage(pattern=f"{_}id{u}")),
    }
    if val == 0: # bot
        bot_handler_only = {
            "report": (report_command_handler, events.NewMessage(pattern=f"{_}report")),
            "reply": (respond_command_handler, events.NewMessage(pattern=f"{_}reply")),
            "get_post": (get_message_command_handler, events.NewMessage(pattern=f"{_}get")),
            "add_tag": (add_tag_command_handler, events.NewMessage(pattern=f"{_}addtag")),
            "subscribe": (subscribe_channel_handler, events.NewMessage(pattern=f"{_}subscribe")),
        }
        command_handlers.update(bot_handler_only)

    return command_handlers


def get_command_handlers_pyrogram(val) -> dict:
    """Get only command handlers for telethon"""
    filter_for_image_search = filters.command("sauce") | (filters.photo | filters.media_group) & filters.incoming & filters.private
    command_handlers_pyrogram = {
        "image_search": MessageHandler(sauce_command_handler, filter_for_image_search)
    }

    if val == 0:
        return command_handlers_pyrogram
    return {}

