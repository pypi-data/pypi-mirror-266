import pytesseract
from PIL import Image

from test_tele.plugins import TgcfMessage, TgcfPlugin
from test_tele.utils import cleanup


class TgcfOcr(TgcfPlugin):
    id_ = "ocr"

    def __init__(self, data) -> None:
        pass

    async def modify(self, tm: TgcfMessage) -> TgcfMessage:

        if not tm.file_type in ["photo"]:
            return tm

        file = await tm.get_file()
        tm.text = pytesseract.image_to_string(Image.open(file))
        cleanup(file)
        return tm
