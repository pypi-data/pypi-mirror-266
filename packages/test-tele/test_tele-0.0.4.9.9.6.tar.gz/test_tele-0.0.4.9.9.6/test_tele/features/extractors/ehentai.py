import os
import logging
import aiohttp
import requests

from PIL import Image
from bs4 import BeautifulSoup

from test_tele.features.extractors.utils import  *
# from test_tele.features.extractors.telegraph import generate_new_telepage, images_in_folder

async def get_doujin_list(url: str):
    """Get doujin list from hentaifox website"""
    url = 'https://hentaifox.com/search/?q='
    query_example = "otou-san no onahole +loli -pregnant"
    query = query.strip().lower().replace(".md", "").replace("-r18", "").lstrip()
    query = query.replace(" ", "+")

    response = requests.get(url)
    if response.status_code == 200:
        return await set_info_dict(response)
    else:
        return None


async def set_info_dict(response):
    soup = BeautifulSoup(response.text, 'html.parser')
    my_list = []
    thumbs = soup.find_all('div', class_='thumb')
    for thumb in thumbs:
        link = thumb.find('h2', class_='g_title').find('a')['href']
        my_dict = {
            "title": thumb.find('h2', class_='g_title').find('a').text,
            "category": thumb.find('a', class_='t_cat').text,
            "thumbnail": thumb.find('img')['src'],
            "doujin_url": "https://hentaifox.com" + link,
            "code": link.split("/gallery/")[-1].replace("/", "")
        }
        my_list.append(my_dict)
    
    return my_list


async def get_img_list_gellerydl(kode):
    example_input = "115161"
    base_url = "https://hentaifox.com/gallery/"
    result_json = await gallery_dl(base_url + kode)

    my_dict = {}
    lists: list = []

    elemen = result_json[-1]

    if elemen[0] == 3:
        my_dict = {
            'img_urls': [],
            'id': str(elemen[2]['filename']),
            'title': elemen[2]['title'],
            'languange': elemen[2]['language'],
            'extension': elemen[2]['extension'],
            'category': elemen[2]['type'],
            'artist': await get_tags(elemen[2]['artist']) if elemen[2]['artist'] else "AI",
            'tags': await combine_tags(elemen),
        }
    
    for elemen in result_json:
        if elemen[0] == 3:
            img_lists = {
                 'url': elemen[1] 
            }
            my_dict['img_urls'].append(img_lists)

    lists.append(my_dict)
    return lists


async def combine_tags(elemen):
    tags = await get_tags(elemen[2]['tags'], 40)
    group = await get_tags(elemen[2]['group'], 40)
    parody = await get_tags(elemen[2]['parody'], 40)
    char = await get_tags(elemen[2]['characters'], 40)
    tags_combined = ', '.join([char, tags, parody, group])
    return tags_combined

