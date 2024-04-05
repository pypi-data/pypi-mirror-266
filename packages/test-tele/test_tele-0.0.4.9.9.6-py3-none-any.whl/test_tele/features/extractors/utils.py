import os
import json
import shlex
import aiohttp
import asyncio
import logging

OFFSET_PID = 50
IMG_EXT = ['jpg', 'webp', 'png', 'heic', 'jpeg']
GIF_EXT = ['gif']
VID_EXT = ['mp4', 'webm']


async def clean_up_tags(query: str, modes: list = [], prefix: str = None):
    """Setting searching mode"""
    example_query = ".px sangonomiya kokomi loli no_ai no_tag no_button safe"
    def_modes = ['no_tag', 'no_button']
    modes += def_modes
    current_modes = {}
    if prefix:
        query = query.strip().lower().replace(prefix, "").lstrip()
    keywords = query.split()

    for keyword in keywords:
        if keyword in modes:
            current_modes[keyword] = True
            query = query.replace(keyword, '')
            continue
        elif keyword.isdigit():
            if prefix == '.px':
                current_modes['illust_detail'] = True
            continue
        elif 'no_inline' in keyword:
            current_modes['no_inline'] = True
            query = query.replace(keyword, '')
            continue
        elif 'file' in keyword:
            if current_modes.get('no_inline'):
                current_modes['file'] = True
            query = query.replace(keyword, '')
            continue
        elif 'limit:' in keyword:
            if current_modes.get('no_inline'):
                limit = keyword.split('limit:')[-1]
                current_modes['limit'] = int(limit)
            query = query.replace(keyword, '')
            continue
        elif 'offset:' in keyword:
            if current_modes.get('no_inline'):
                offset = keyword.split('offset:')[-1]
                current_modes['offset'] = int(offset)
            query = query.replace(keyword, '')
            continue

    return current_modes, query.strip()


async def get_tags(tags: list[str], limit: int = 0) -> str:
    real_tags = []
    i = 0
    for tag in tags:
        if limit != 0:
            i += 1
        decoded_str = tag.encode('utf-8').decode('utf-8')
        real_tags.append(f"`{decoded_str}`")
        if limit != 0 and i == limit:
            break
    all_tags = f'{(", ").join(real_tags)}'
    return all_tags


async def gallery_dl(url: str, pid=0, offset: int=OFFSET_PID, force_kill: float=None, filter='--range', download=False):
    """Start subprocess gallery-dl"""
    mode = "-j" if not download else "--no-part"
    command = shlex.split(f'gallery-dl \"{url}\" --config-ignore -c config/config.json {mode} {filter} {pid + 1}-{pid + offset}')
    
    try:
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        if force_kill:
            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=force_kill)
            except asyncio.TimeoutError:
                process.kill()
        else:
            stdout, stderr = await process.communicate()

        if process.returncode != 0:
            if not force_kill:
                raise Exception(f'gallery-dl failed with return code {process.returncode}: {stderr.decode()}')
        else:
            try:
                result = json.loads(stdout.decode())
                return result
            except:
                return stdout.decode()
        
    except Exception as err:
        logging.error(err)


async def turn_into_gif(elemen) -> str:
    if elemen[2]['extension'] == 'webm':
        url = elemen[1]
        gif_url = url[:-5] + ".gif"
        return gif_url
    return elemen[1]


async def autocomplete(keywords: dict, input_text: str, ret_key=True):
    """Search autocomplete, tag must be provided"""
    if ret_key:
        suggestions = next((key for key in keywords.keys() if input_text in key), None)
    else:
        suggestions = next((keywords[key] for key in keywords.keys() if input_text in key), None)

    return suggestions


async def download_media(session, elemen):
    nama_file =  elemen['category'] + "_" + elemen['index'] + "." + elemen['extension']
    folder = f"temps/{elemen['user_id']}/{elemen['category']}"
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    path_file = os.path.join(folder, nama_file)
    async with session.get(elemen['img_url']) as response:
        if response.status == 200:
            with open(path_file, 'wb') as f:
                f.write(await response.read())
        else:
            logging.warning(f'Failed to download file {nama_file}')


async def download_from_url(dict_info_lists:list=[]):
    """Download media from given url

    Args:
    dict_info_lists (list[dict]): iterable dictionary containing media information

    Note:
    dict_info_lists must include keys: ['user_id', 'category', 'img_url', 'index', 'extension']

    Return:
    None, but folder temps/{user_id}/{category} is created
    """
    # Bagian download gambar secara paralel
    async with aiohttp.ClientSession() as session:
        tasks = [download_media(session, element) for element in dict_info_lists]
        await asyncio.gather(*tasks)
    
