import time
import shutil

from .. import consts, globals
from ..controller import Buttons, pro
from ..ocr import OCR
from ..utils.decorator import retry
from ..utils.log import logger
from ..utils.notify import Notify


def enter_game():
    """进入游戏"""
    buttons = [
        Buttons.B,
        Buttons.DPAD_UP,
        Buttons.DPAD_LEFT,
        Buttons.DPAD_LEFT,
        Buttons.A,
        Buttons.A,
    ]
    pro.press_group(buttons, 0.5)


@retry(max_attempts=3)
def reset_to_career(attempts):
    """重置到生涯"""
    pro.press_group([Buttons.B] * 5, 2)
    pro.press_group([Buttons.DPAD_DOWN] * 4, 0.1)
    pro.press_group([Buttons.DPAD_RIGHT] * 7, 0.1)
    pro.press_group([Buttons.A], 2)
    pro.press_group([Buttons.B], 2)


def in_series(page, mode):
    if (
        mode == consts.mp1_zh
        and page.name == consts.world_series
        or mode in [consts.mp2_zh, consts.mp3_zh]
        and page.name
        in [
            consts.trial_series,
            consts.limited_series,
        ]
    ):
        return True
    return False


@retry(max_attempts=3)
def enter_series(attempts, page=None, mode=None):
    """进入多人赛事"""
    event_type = None
    if not mode:
        mode = globals.CONFIG["模式"]
    if page and in_series(page, mode):
        return
    if page and page.name in [consts.carhunt, consts.legendary_hunt] and attempts < 1:
        page_config_mapping = {consts.carhunt: "寻车", consts.legendary_hunt: "传奇寻车"}
        config_key = page_config_mapping.get(page.name)
        if config_key in ["寻车", "自定义"]:
            event_type = globals.CONFIG[config_key]["活动"]
        pro.press_group([Buttons.B] * 3, 2)
        pro.press_group([Buttons.ZR], 0.5)
        if event_type == "特殊":
            pro.press_group([Buttons.ZR], 0.5)
    else:
        reset_to_career()
        pro.press_group([Buttons.ZL] * 4, 0.5)
    if mode == consts.mp2_zh:
        pro.press_group([Buttons.DPAD_DOWN], 0.5)
    if mode == consts.mp3_zh:
        pro.press_group([Buttons.DPAD_DOWN] * 2, 0.5)
    time.sleep(2)
    pro.press_group([Buttons.A], 2)
    page = OCR.get_page()
    if in_series(page, mode):
        pass
    else:
        raise Exception(f"Failed to access {mode}, current page = {page.name}")


@retry(max_attempts=3)
def enter_career(attempts, page=None, mode=None):
    """进入生涯"""
    if not mode:
        mode = globals.CONFIG["模式"]
    if page and in_series(page, mode):
        return
    reset_to_career()
    pro.press_group([Buttons.A], 2)
    page = OCR.get_page()
    if page.name == consts.career:
        pro.press_button(Buttons.ZR, 2)
        pro.press_button(Buttons.DPAD_UP, 1)
        pro.press_a()
    else:
        raise Exception(f"Failed to access {mode}, current page = {page.name}")


def _enter_daily_events(page=None, mode=0, attempts=0):
    """进入每日活动如寻车/传奇寻车
    0 寻车
    1 传奇寻车
    2 自定义
    """
    if mode == 0:
        page_name = consts.carhunt
        config_key = "寻车"
        verify_page = OCR.is_car_hunt
    if mode == 1:
        page_name = consts.legendary_hunt
        config_key = "传奇寻车"
        verify_page = OCR.is_legendary_hunt
    if mode == 2:
        page_name = consts.custom_event
        config_key = "自定义"
        verify_page = OCR.is_custom_event

    if page:
        logger.info(f"page = {page}, page.name = {page.name}")
    if page and page.name == page_name:
        return

    event_type = "每日"
    if config_key in ["寻车", "自定义"]:
        event_type = globals.CONFIG[config_key]["活动"]

    if event_type == "特殊":
        reset_to_career()
        pro.press_group([Buttons.DPAD_DOWN] * 3, 0.2)
        pro.press_group([Buttons.DPAD_LEFT] * 6, 0.2)
        pro.press_group([Buttons.A], 0.5)
        pro.press_group([Buttons.DPAD_UP] * 8, 0.2)
        if not globals.CONFIG[config_key]["位置"]:
            logger.info(f"Please set {config_key} position!")
            return
        pro.press_group([Buttons.DPAD_DOWN] * globals.CONFIG[config_key]["位置"], 0.5)
        pro.press_group([Buttons.A] * 2, 3)
        page = OCR.get_page()
        if page.name == page_name:
            pro.press_a()
        else:
            raise Exception(f"Failed to access {config_key}.")
    else:
        if (
            page
            and page.name
            in [
                consts.world_series,
                consts.limited_series,
                consts.trial_series,
            ]
            and attempts < 1
        ):
            pro.press_group([Buttons.B, Buttons.B, Buttons.B, Buttons.ZL], 2)
        else:
            reset_to_career()
            pro.press_group([Buttons.ZL] * 5, 0.5)

        # 自动领取
        if OCR.has_daily_claim():
            pro.press_group([Buttons.A] * 3, 3)
            pro.press_group([Buttons.ZL], 1)

            last_event = ""
            for _ in range(20):
                event = OCR.get_daily_event()
                if event == last_event:
                    break
                else:
                    last_event = event
                    pro.press_a()
                    if OCR.has_event_claim():
                        pro.press_a()
                        pro.press_b()
                    else:
                        pro.press_b()
                pro.press_group([Buttons.ZR], 0.5)

            pro.press_group([Buttons.ZL] * 12, 0)

        else:
            pro.press_group([Buttons.A], 3)

        pro.press_group([Buttons.ZR] * (globals.CONFIG[config_key]["位置"] - 1), 0.5)
        time.sleep(1)
        ctx = {"capture": True}
        if verify_page(ctx):
            pro.press_a()
        else:
            pro.press_group([Buttons.ZL] * 12, 0)
            for i in range(1, 20):
                if verify_page(ctx):
                    globals.CONFIG[config_key]["位置"] = i + 1
                    pro.press_a()
                    break
                pro.press_group([Buttons.ZR], 1)
            else:
                raise Exception(f"Failed to access {config_key}.")


@retry(max_attempts=3)
def enter_carhunt(attempts, page=None):
    """进入寻车"""
    _enter_daily_events(page, 0, attempts)


@retry(max_attempts=3)
def enter_legend_carhunt(attempts, page=None):
    """进入传奇寻车"""
    _enter_daily_events(page, 1, attempts)


@retry(max_attempts=3)
def enter_custom_event(attempts, page=None):
    """进入自定义任务"""

    _enter_daily_events(page, 2, attempts)


@retry(max_attempts=3)
def free_pack(attempts, page=None):
    """领卡"""
    reset_to_career()
    pro.press_group([Buttons.DPAD_DOWN] * 3, 0.2)
    pro.press_group([Buttons.DPAD_LEFT] * 8, 0.2)
    pro.press_group([Buttons.A], 0.5)
    pro.press_group([Buttons.DPAD_UP], 0.5)
    pro.press_group([Buttons.A] * 2, 5)
    page = OCR.get_page()
    if page.has_text("CLASSIC PACK.*POSSIBLE CONTENT"):
        pro.press_group([Buttons.A] * 3, 3)
        pro.press_group([Buttons.B], 0.5)
    else:
        raise Exception(f"Failed to access free pack, current page = {page.name}")


@retry(max_attempts=3)
def shop_notify(attempts, page=None):
    """商店刷新通知"""
    reset_to_career()
    pro.press_group([Buttons.DPAD_DOWN] * 3, 0.2)
    pro.press_group([Buttons.DPAD_LEFT] * 8, 0.2)
    pro.press_group([Buttons.A], 0.5)
    pro.press_group([Buttons.DPAD_UP], 0.5)
    pro.press_group([Buttons.A] * 1, 5)
    page = OCR.get_page()
    if page.has_text("CARD PACK LEVEL INFO"):
        pro.press_group([Buttons.DPAD_DOWN] * 1, 2)
        OCR.get_page()
        shutil.copy2("./output.jpg", "./shop.jpg")
        if "通知" in globals.CONFIG:
            globals.notify_queue.put(
                {
                    "notify": True,
                    "host": globals.CONFIG["通知"]["Host"],
                    "key": globals.CONFIG["通知"]["Key"],
                }
            )
        pro.press_group([Buttons.B] * 2, 3)
    else:
        raise Exception(f"Failed to access shop, current page = {page.name}")


@retry(max_attempts=3)
def prix_pack(attempts, page=None):
    """大奖赛领卡"""
    reset_to_career()
    pro.press_group([Buttons.DPAD_DOWN] * 3, 0.2)
    pro.press_group([Buttons.DPAD_LEFT] * 6, 0.2)
    pro.press_group([Buttons.A], 0.5)
    pro.press_group([Buttons.DPAD_UP] * 8, 0.2)
    if not globals.CONFIG["大奖赛"]["位置"]:
        logger.info("Please set grand prix position!")
        return
    pro.press_group([Buttons.DPAD_DOWN] * globals.CONFIG["大奖赛"]["位置"], 0.5)
    for _ in range(2):
        pro.press_group([Buttons.A], 5)
        page = OCR.get_page()
        if page.name == consts.grand_prix:
            pro.press_group([Buttons.DPAD_LEFT] * 4, 0.2)
            pro.press_group([Buttons.DPAD_RIGHT], 0.2)
            pro.press_group([Buttons.A] * 3, 3)
            break
    else:
        raise Exception(f"Failed to access prix pack, current page = {page.name}")
