from test_tele.features.extractors.utils import *


async def set_info_dict(gallery_dl_result) -> list[dict]:
    """Set dict based on website"""
    my_dict = {}
    lists: list = []

    if gallery_dl_result:
        for elemen in gallery_dl_result:
            if elemen[0] == 3 and elemen[2]["extension"] in IMG_EXT:
                my_dict = {
                    'img_url': elemen[1],
                    'caption': elemen[2]['description'],
                    'id': str(elemen[2]['shortcode']),
                    'width': int(elemen[2]['width']),
                    'height': int(elemen[2]['height']),
                    'filename': str(elemen[2]['filename']),
                    'author': elemen[2]['username'],
                    'fullname': elemen[2]['fullname'],
                    'extension': elemen[2]['extension'],
                }
                lists.append(my_dict)
    return lists


async def get_ig_album_list(query: str, pid: int=0):
    gallery_dl_result = await gallery_dl(query, pid=pid)
    return await set_info_dict(gallery_dl_result)
