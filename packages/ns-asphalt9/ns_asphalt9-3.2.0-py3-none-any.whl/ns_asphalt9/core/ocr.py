import os
import re
import time
import threading

import pytesseract
from PIL import Image, ImageFilter

from . import consts, globals
from .page_factory import factory
from .screenshot import screenshot
from .utils.count import count
from .utils.log import logger
from .utils.track_data import track_data


class LogManager:
    log_texts = None
    log_text_index = 0

    @classmethod
    def get_text(cls):
        if not cls.log_texts:
            cls.log_texts = []
            with open("logs/race.log") as file:
                lines = file.readlines()
            for line in lines:
                match = re.search(r"'text':\s*'(.*?)'", line)
                match1 = re.search(r"'text':\s*\"(.*?)\"", line)
                if match:
                    text = match.group(1)
                    cls.log_texts.append(text)
                elif match1:
                    text = match1.group(1)
                    cls.log_texts.append(text)
        text = cls.log_texts[cls.log_text_index]
        cls.log_text_index += 1
        return text


class OCR:
    filename = "output.jpg"
    ticket = -1
    next_page = None
    text = ""
    image = None
    last_progress = -1

    def __init__(self, image):
        self.image = image

    @classmethod
    def get_text(cls, debug_level="DEBUG"):
        debug = os.environ.get("A9_DEBUG", 0)
        if debug:
            text = LogManager.get_text()
        else:
            text = cls._get_text(
                config="--psm 11", replace=True, convert="L", debug_level=debug_level
            )
        return text

    @classmethod
    def get_page(cls):
        """获取匹配页面"""
        result = cls.verify_next_page()
        if result:
            page = factory.create_page(cls.text, cls.next_page)
            cls.next_page = None
        else:
            text = cls.get_text()
            page = factory.create_page(text)
        logger.info(f"ocr page dict = {page.dict}")
        return page

    @classmethod
    def verify_next_page(cls):
        verify_method_mapping = {
            consts.world_series: cls.is_series,
            consts.limited_series: cls.is_series,
            consts.custom_event: cls.is_custom_event,
            consts.carhunt: cls.is_car_hunt,
            consts.legendary_hunt: cls.is_legendary_hunt,
            consts.select_car: cls.is_select_car,
        }
        verify_method = verify_method_mapping.get(cls.next_page, None)
        if verify_method:
            return verify_method(ctx={"capture": False})

    @classmethod
    def get_track(cls):
        """识别赛道"""
        text = cls._get_text(crop=(0, 0, 600, 300), replace=True)
        logger.info(f"ocr page map result = {text}")
        for track in track_data:
            if track["tracken"] in text:
                logger.info(f"Get track = {track}")
                return track
        count.not_recongnized_track_inc(text)

    @classmethod
    def get_player_info(cls):
        """识别玩家信息"""
        player_name = cls._get_text(crop=(300, 300, 700, 380), replace=True)
        club_name = cls._get_text(crop=(300, 370, 700, 430), replace=True)
        if player_name and club_name:
            data = {"player_name": player_name, "club_name": club_name}
        else:
            data = {}
        return data

    @classmethod
    def get_division(cls):
        division = ""
        img = Image.open(cls.filename)
        img = cls._crop_image(img, (735, 535, 1185, 655))
        threshold = 150
        width, height = img.size
        # 遍历每个像素
        for y in range(height):
            for x in range(width):
                pixel = img.getpixel((x, y))
                red, green, blue = pixel
                if red > threshold and green > threshold and blue > threshold:
                    # 将红色部分变为白色
                    img.putpixel((x, y), (255, 255, 255))
                else:
                    # 其他部分变成黑色
                    img.putpixel((x, y), (0, 0, 0))
        text: str = pytesseract.image_to_string(img, lang="eng", config="--dpi 72")
        img.close()
        text = text.replace("\n", " ")
        divisions = re.findall("BRONZE|SILVER|GOLD|PLATINUM", text)
        if divisions:
            division = consts.divisions_zh.get(divisions[0], "")
        return division

    @classmethod
    def get_progress(cls, image_path=None, capture=False):
        """识别进度"""
        for _ in range(2):
            text = cls._get_text(
                crop=(155, 82, 373, 130), replace=True, config="--psm 11"
            )
            pattern = r"\b\d{1,3}\b"
            match = re.search(pattern, text)
            if match and "%" in text:
                m = match.group()
                if int(m) > 100:
                    num = int(m[:2])
                else:
                    num = int(m)
                return num
        return -1

    @classmethod
    def get_pos(cls):
        img = Image.open(cls.filename)
        img = cls._crop_image(img, (240, 20, 380, 80))
        img = cls.convert_red2white(img)
        img = img.convert("L")
        text: str = pytesseract.image_to_string(img, lang="eng", config="--dpi 72")
        img.close()
        text = text.replace("\n", " ")
        logger.info(f"Get pos text text = {text}")
        match = re.match(r"(\d)/\d", text)
        if match:
            return int(match.group(1))

    @classmethod
    def convert_red2white(cls, img):
        # 设定红色阈值
        red_threshold = 200
        # 获取图片的宽和高
        width, height = img.size
        # 遍历每个像素
        for y in range(height):
            for x in range(width):
                pixel = img.getpixel((x, y))
                red, green, blue = pixel
                if red > red_threshold:
                    # 将红色部分变为白色
                    img.putpixel((x, y), (255, 255, 255))
                else:
                    # 其他部分变成黑色
                    img.putpixel((x, y), (0, 0, 0))
        return img

    @classmethod
    def get_touchdriver(cls):
        """识别touchdriver模式"""
        text = cls._get_text(crop=(286, 150, 360, 190), convert="L", replace=True)
        if "ON" in text:
            return 1
        if "OFF" in text:
            return 0

        img = Image.open(cls.filename)
        img = cls._crop_image(img, (286, 150, 360, 190))
        img = img.filter(ImageFilter.SHARPEN)
        img = cls.convert_red2white(img)
        text: str = pytesseract.image_to_string(img, lang="eng", config="--dpi 72")
        img.close()
        text = text.replace("\n", " ")
        if "ON" in text:
            return 1
        if "OFF" in text:
            return 0
        return -1

    @classmethod
    def has_play(cls, mode):
        """是否有PLAY按钮"""
        if mode in [
            consts.car_hunt_zh,
            consts.legendary_hunt_zh,
            consts.custom_event_zh,
        ]:
            crop = (1550, 900, 1675, 1080)
        else:
            crop = (1580, 900, 1750, 1060)
        text = cls._get_text(
            crop=crop,
            filter=ImageFilter.SHARPEN,
            convert="L",
            replace=True,
        )
        return "PLAY" in text or "PL" in text or "AY" in text

    @classmethod
    def has_claim(cls):
        """是否有CLAIM按钮"""
        crop = (735, 585, 1185, 655)
        text = cls._get_text(
            crop=crop,
            replace=True,
        )
        return "READY TO CLAIM" in text

    @classmethod
    def has_event_claim(cls):
        """每日活动中是否有CLAIM按钮"""
        crop = (1500, 950, 1780, 1040)
        text = cls._get_text(
            crop=crop,
            replace=True,
        )
        return "CLAIM" in text

    @classmethod
    def has_daily_claim(cls):
        """每日中是否有CLAIM按钮"""
        crop = (1500, 720, 1750, 800)
        text = cls._get_text(
            crop=crop,
            replace=True,
        )
        return len(re.findall("C|L|A|I|M", text)) > 2

    @classmethod
    def has_next(cls, image_path="", capture=False):
        """是否有NEXT按钮"""
        text = cls._get_text(
            crop=(1460, 900, 1750, 1040),
            filter=ImageFilter.SHARPEN,
            replace=True,
        )
        return "NEXT" in text

    @classmethod
    def get_carinfo_ticket(cls):
        """获取车辆信息页的票数"""
        text = cls._get_text(
            crop=(1620, 250, 1755, 300),
            filter=ImageFilter.SHARPEN,
            convert="L",
            replace=True,
        )
        text = text.replace("A", "4")
        r = re.findall("(\d+)/10", text)
        if r and int(r[0]) <= 10 and int(r[0]) >= 0:
            cls.ticket = int(r[0])
        else:
            cls.ticket = cls.ticket - 1
        if cls.ticket < 0:
            cls.ticket = 0
        return cls.ticket

    @classmethod
    def get_ticket(cls):
        """获取票数"""
        text = cls._get_text(crop=(1640, 140, 1770, 180), replace=True, convert="L")
        text = text.replace("A", "4")
        r = re.findall("(\d+)/10", text)
        if not r:
            text = cls._get_text(config="--psm 11", replace=True, convert="L")
            r = re.findall("(\d+)/10", text)
        if r and int(r[0]) <= 10 and int(r[0]) >= 0:
            cls.ticket = int(r[0])
        else:
            cls.ticket = cls.ticket - 1
        if cls.ticket < 0:
            cls.ticket = 0
        return cls.ticket

    @classmethod
    def is_custom_event(cls, ctx=None):
        """自定义页面"""
        text = cls._get_text(
            crop=(100, 280, 1000, 430), replace=True, config=None, convert="L"
        )
        feature = globals.CONFIG["自定义"]["feature"].split(".")[0]
        logger.info(f"Verify {feature} in {text}")
        if re.findall(feature, text):
            return True
        return False

    @classmethod
    def is_car_hunt(cls, ctx=None):
        """每日carhunt页面"""
        text = cls._get_text(
            crop=(100, 280, 1000, 430), replace=True, config=None, convert="L"
        )
        if "feature" in globals.CONFIG["寻车"] and globals.CONFIG["寻车"]["feature"]:
            has_feature = globals.CONFIG["寻车"]["feature"] in text
        else:
            has_feature = True
        has_carhunt = re.findall("CAR HUNT(?!\sRIOT)", text)
        if has_carhunt and has_feature:
            return True
        return False

    @classmethod
    def get_daily_event(cls):
        """获取每日活动"""
        text = cls._get_text(
            crop=(100, 280, 1000, 430), replace=True, config=None, convert="L"
        )
        return text

    @classmethod
    def is_legendary_hunt(cls, ctx=None):
        """每日lengedd hunt页面"""
        text = cls._get_text(
            crop=(100, 280, 1000, 430), replace=True, config=None, convert="L"
        )
        if re.findall("LEGENDARY HUNT(?!\sRIOT)", text):
            return True
        return False

    @classmethod
    def is_series(cls, ctx=None):
        """是否是series"""
        text = cls._get_text(
            crop=(735, 300, 1185, 375), config="--psm 11", replace=True
        )
        if "SERIES" in text:
            return True
        return False

    @classmethod
    def is_select_car(cls, ctx=None):
        """是否是选车"""
        text = cls._get_text(crop=(120, 100, 580, 175), replace=True)
        if "CAR SELECTION" in text:
            return True
        return False

    @classmethod
    def _crop_image(cls, img, crop):
        resize = False
        width, height = img.size
        if width != 1920:
            x_scale = width / 1920
            y_scale = height / 1080
            crop = (
                int(crop[0] * x_scale),
                int(crop[1] * y_scale),
                int(crop[2] * x_scale),
                int(crop[3] * y_scale),
            )
            resize = True
        img = img.crop(crop)
        if resize:
            img = img.resize((img.width * 2, img.height * 2), resample=Image.LANCZOS)
        return img

    @classmethod
    def save_image(cls, img):
        def save(img):
            try:
                img.save("output.jpg")
            except Exception as e:
                logger.info(f"保存图像时发生错误: {e}")

        thread = threading.Thread(target=save, args=(img,))
        thread.start()

    @classmethod
    def _get_text(
        cls,
        crop=None,
        filter=None,
        convert=None,
        replace=None,
        config="--dpi 72",
        debug_level="DEBUG",
    ):
        start_time = time.time()
        img = screenshot()
        cls.save_image(img)
        if crop:
            img = cls._crop_image(img, crop)
        if filter:
            img = img.filter(filter)
        if convert:
            img = img.convert(convert)
        text: str = pytesseract.image_to_string(img, lang="eng", config=config)
        if replace:
            text = text.replace("\n", " ")
        if text:
            if debug_level == "DEBUG":
                logger.debug(
                    f"Get text from page, text = {text}, cost time = {time.time() - start_time}"
                )
            else:
                logger.info(
                    f"Get text from page, text = {text}, cost time = {time.time() - start_time}"
                )
        cls.text = text
        return text


if __name__ == "__main__":
    OCR.get_text()
