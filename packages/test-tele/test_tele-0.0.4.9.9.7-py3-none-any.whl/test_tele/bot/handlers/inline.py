from pyrogram.handlers import InlineQueryHandler
from pyrogram.types import InlineQuery

from test_tele.features.pyrogram.pixiv import inline_pixiv
from test_tele.features.pyrogram.gelbooru import inline_gelbooru
from test_tele.features.pyrogram.manga import inline_mangapark, check_inline_query_type
from test_tele.features.pyrogram.realperson import inline_realperson
from test_tele.features.pyrogram.furry import inline_furry


# Inline 
async def inline_handler(app, inline_query: InlineQuery):
    """Handle inline query search"""
    query_handlers = {
        '/': check_inline_query_type,
        '.md': inline_mangapark,
        '.px': inline_pixiv,
        '.rp': inline_realperson,
        '.fur': inline_furry
        # '.2d': inline_vanillarock
    }

    for query_prefix, handler in query_handlers.items():
        if inline_query.query.lower().startswith(query_prefix):
            await handler(app, inline_query)
            break
    else:
        await inline_gelbooru(app, inline_query)


def get_inline_handler(val):
    pyrogram_inline_handler = {
        "inline_query": InlineQueryHandler(inline_handler)
    }
    if val == 0:
        return pyrogram_inline_handler
    return {}