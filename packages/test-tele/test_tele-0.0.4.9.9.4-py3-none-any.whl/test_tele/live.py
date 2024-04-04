"""The module responsible for operating tgcf in live mode"""

from test_tele.user_bot.telethon import *
from test_tele.bot.handlers import get_pyrogram_handlers, get_telethon_handlers

ALL_TELETHON_EVENTS = BOT_HANDLER
USER_TELETHON_EVENTS = {}


async def start_telethon():
    """Start tgcf live sync."""
    # clear past session files
    clean_session_files()

    USER_SESSION = StringSession(CONFIG.login.SESSION_STRING) # tambahan ku
    # SESSION = get_SESSION()
    client = TelegramClient( 
        USER_SESSION,
        CONFIG.login.API_ID,
        CONFIG.login.API_HASH,
        sequential_updates=CONFIG.live.sequential_updates,
    )
    bot_client = TelegramClient( # tambahan ku
        'tgcf_bot',
        CONFIG.login.API_ID,
        CONFIG.login.API_HASH,
        sequential_updates=CONFIG.live.sequential_updates,
    )
    
    if CONFIG.login.user_type == 0: # bot
        if CONFIG.login.BOT_TOKEN == "":
            logging.warning("Bot token not found, but login type is set to bot.")
            sys.exit()
        await bot_client.start(bot_token=CONFIG.login.BOT_TOKEN) # edit variable
    else:
        await client.start()
        await bot_client.start(bot_token=CONFIG.login.BOT_TOKEN) # tambahan ku

    config.is_bot = await bot_client.is_bot()
    logging.info(f"config.is_bot={config.is_bot}")

    await config.load_admins(bot_client)

    if CONFIG.login.user_type == 1: # user
        command_events = get_telethon_handlers(1)
        USER_TELETHON_EVENTS.update(command_events)
        for key, val in USER_TELETHON_EVENTS.items():
            if config.CONFIG.live.delete_sync is False and key == "deleted":
                continue
            client.add_event_handler(*val)

    # tambahan ku
    command_events = get_telethon_handlers(0)
    ALL_TELETHON_EVENTS.update(command_events)
    for key, val in ALL_TELETHON_EVENTS.items():
        if config.CONFIG.live.delete_sync is False and key == "deleted":
            continue
        bot_client.add_event_handler(*val)
        logging.info(f"Added event handler for {key}")

    if const.REGISTER_COMMANDS: # config.is_bot and
        await bot_client( # edit variable
            functions.bots.SetBotCommandsRequest(
                scope=types.BotCommandScopeDefault(),
                lang_code="en",
                commands=[
                    types.BotCommand(command=key, description=value)
                    for key, value in const.COMMANDS.items()
                ],
            )
        )
    if CONFIG.login.user_type == 1:
        config.client = client
        config.from_to, config.reply_to = await config.load_from_to(client, config.CONFIG.forwards)
    else:
        config.from_to, config.reply_to = await config.load_from_to(bot_client, config.CONFIG.forwards)

    if CONFIG.login.user_type == 1: # user
        await client.run_until_disconnected()
    await bot_client.run_until_disconnected()


# ====================================================

from test_tele.live_pyrogram import *

USERBOT_HANDLERS = get_pyrogram_handlers(1)
ALL_PYROGRAM_HANDLERS = get_pyrogram_handlers(0)


PYRO_APPS.append(BOT)
if CONFIG.login.user_type == 1: # user
    PYRO_APPS.append(USER)

async def start_pyrogram():
    for key, val in ALL_PYROGRAM_HANDLERS.items():
        PYRO_APPS[0].add_handler(val)

    await PYRO_APPS[0].start()

    if CONFIG.login.user_type == 1: # user
        for key, val in USERBOT_HANDLERS.items():
            PYRO_APPS[1].add_handler(val)
            
        await PYRO_APPS[1].start()
