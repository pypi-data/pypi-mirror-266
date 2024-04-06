import re
from telethon.tl import types

## Helper function for get_message
    
async def get_entity(event, entity):
    """Get chat entity from entity parameter"""
    if entity.isdigit() or entity.startswith("-"):
        chat = types.PeerChannel(int(entity))
    else:
        try:
            chat = await event.client.get_entity(entity)
        except Exception as e:
            chat = await event.client.get_entity(types.PeerChat(int(entity)))

    return chat


async def loop_message(event, chat, ids: int, next=True):
    """Loop channel posts to get message"""
    skip = 20
    tries = 0
    while True:
        if ids > 0 and tries <= skip:
            message = await event.client.get_messages(chat, ids=ids)
            tries += 1
            if not message:
                if next:
                    ids += 1
                    continue
                else:
                    ids -= 1
                    continue
            else:
                if hasattr(message, 'message'):
                    if message.media and not (message.sticker or message.voice or message.web_preview):
                        return message
                ids = ids + 1 if next else ids - 1
        else:
            return


## Helper function for turn into telegraph
        
# async def hentaifox_to_telegraph(kode):
#     from test_tele.features.extractors.ehentai import get_img_list_gellerydl
#     lists = await get_img_list_gellerydl(kode)


## Helper to check if user is in a group
        
async def is_bot_in_group(event):
    """
    Check if the bot is running in a group.

    Args:
        client (TelegramClient): The Telegram client.
        event (Message): The message event.

    Returns:
        bool: True if the bot is running in a group, False otherwise.
    """

    chat = await event.client.get_entity(event.chat_id)
    return chat.megagroup


## REGEX

async def youtube_url_validation(url):
    youtube_regex = (
        r'(https?://)?(www\.)?'
        r'(youtube|youtu|youtube-nocookie)\.(com|be)/'
        r'(watch\?v=|embed/|v/|.+\?v=|shorts/)?([^&=%\?]{11})')

    youtube_regex_match = re.search(youtube_regex, url)
    if youtube_regex_match:
        return youtube_regex_match.group(0)

    return youtube_regex_match


async def instagram_url_validation(url):
    instagram_regex = (
        r'(https?://)?(www\.)?'
        r'(instagram.com)/'
        r'(p/[^&=%\?\s]{1,}|[^&=%\?\s]{1,}highlights/[^&=%\?\s]{1,18}|[^&=%\?\s]+)')

    instagram_regex_match = re.search(instagram_regex, url)
    if instagram_regex_match:
        link_ig = instagram_regex_match.group(0).rstrip("/")
        if "/p/" not in link_ig and "/highlights/" not in link_ig:
            link_ig = link_ig + "/posts" if "/posts" not in link_ig else link_ig
        return link_ig
    
    return instagram_regex_match


async def twitter_url_validation(url):
    twitter_regex = (
        r"(?:https?://)?(?:www\.|mobile\.)?"
        r"(?:(?:[fv]x)?twitter|(?:fixup)?x)\.com"
        r"/([^/?#]+|i/web)/status/(\d+)")

    twitter_regex_match = re.search(twitter_regex, url)
    if twitter_regex_match:
        link_tw = twitter_regex_match.group(0)
        return link_tw
    
    return twitter_regex_match


import re

async def determine_url_category(url):
    # Pola regex untuk Twitter
    twitter_regex = (
        r"(?:https?://)?(?:www\.|mobile\.)?"
        r"(?:(?:[fv]x)?twitter|(?:fixup)?x)\.com"
        r"/([^/?#]+|i/web)/status/(\d+)")

    # Pola regex untuk Instagram
    instagram_regex = (
        r'(https?://)?(www\.)?'
        r'(instagram.com)/'
        r'(p/[^&=%\?\s]{1,}|[^&=%\?\s]{1,}highlights/[^&=%\?\s]{1,18}|[^&=%\?\s]+)')

    # Pola regex untuk Newgrounds
    newgrounds_regex = (
        r'(https?://)?(www\.)?'
        r'(newgrounds.com)/'
        r'(portal/view/[^&=%\?\s]{1,})')

    # Periksa kecocokan dengan pola Twitter
    twitter_match = re.search(twitter_regex, url)

    # Periksa kecocokan dengan pola Instagram
    instagram_match = re.search(instagram_regex, url)

    # Periksa kecocokan dengan pola Newgrounds
    newgrounds_match = re.search(newgrounds_regex, url)
    
    # Tentukan kategori URL berdasarkan kecocokan
    if twitter_match:
        return "twitter"
    elif instagram_match:
        return "instagram"
    elif newgrounds_match:
        return "newgrounds"
    else:
        return "unknown"

async def accepted_url_validation(url):
    acc_url_regex = (
        r"(?:https?://)?"
        r"(?:www\.|mobile\.)?"
        r"(?:[^&%#\s]+)\.(?:[^&%#\s]{2,6})/"
        r"(?:[^&%#\s]+)")
    
    acc_url_regex_match = re.search(acc_url_regex, url)
    if acc_url_regex_match:
        link_other = acc_url_regex_match.group(0)
        return link_other
    
    return acc_url_regex_match
