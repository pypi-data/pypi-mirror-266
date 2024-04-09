"""autodlc"""
import time
import traceback

from ..controller import Buttons, pro
from ..utils.log import logger
from .. import ocr


KEY_POSITION = {
    "1": (1, 1),
    "2": (1, 2),
    "3": (1, 3),
    "4": (1, 4),
    "5": (1, 5),
    "6": (1, 6),
    "7": (1, 7),
    "8": (1, 8),
    "9": (1, 9),
    "0": (1, 10),
    "@": (1, 11),

    "q": (2, 1),
    "w": (2, 2),
    "e": (2, 3),
    "r": (2, 4),
    "t": (2, 5),
    "y": (2, 6),
    "u": (2, 7),
    "i": (2, 8),
    "o": (2, 9),
    "p": (2, 10),
    "+": (2, 11),

    "a": (3, 1),
    "s": (3, 2),
    "d": (3, 3),
    "f": (3, 4),
    "g": (3, 5),
    "h": (3, 6),
    "j": (3, 7),
    "k": (3, 8),
    "l": (3, 9),
    "_": (3, 10),
    ":": (3, 11),

    "z": (4, 1),
    "x": (4, 2),
    "c": (4, 3),
    "v": (4, 4),
    "b": (4, 5),
    "n": (4, 6),
    "m": (4, 7),
    ",": (4, 8),
    ".": (4, 9),
    "-": (4, 10),
    "/": (4, 11),
}


def enter_string(string):
    """输入字母"""
    for index, letter in enumerate(string):
        row, col = KEY_POSITION.get(letter.lower())
        logger.info(f"Enter letter {letter} row = {row} col = {col}")
        if letter.isupper():
            pro.press_button(Buttons.R_STICK_PRESS, 1)
        for _ in range(row - 1):
            pro.press_button(Buttons.DPAD_DOWN, 0.1)
        for _ in range(col - 1):
            pro.press_button(Buttons.DPAD_RIGHT, 0.1)
        pro.press_button(Buttons.A, 0.5)
        pro.press_button(Buttons.PLUS, 1)
        if index < len(string) - 1:
            pro.press_button(Buttons.DPAD_UP, 0.2)
            pro.press_button(Buttons.DPAD_UP, 0.2)
            pro.press_button(Buttons.A, 1)


def wait_for(target_text):
    logger.info(f"Wait for text {target_text}")
    for _ in range(20):
        text = ocr.OCR.get_text(debug_level="INFO")
        if target_text in text:
            return True
        time.sleep(1)


def enter_code(code):
    """兑换码领取"""
    try:
        logger.info(f"Start redeem code {code}")
        wait_for("GAME INFO")
        pro.press_button(Buttons.A, 1)
        wait_for("ENTER YOUR CODE")
        pro.press_button(Buttons.A, 1)
        enter_string(code)
        pro.press_button(Buttons.DPAD_DOWN, 1)
        pro.press_button(Buttons.A, 2)
        text = ocr.OCR.get_text(debug_level="INFO")
        if "CODE FAILED" in text:
            pro.press_button(Buttons.A, 1)
            pro.press_button(Buttons.B, 1)
            logger.info(f"{code} DISABLED")
        if "SELECT" in text:
            logger.info(f"{code} ENABLED")
            for _ in range(30):
                text = ocr.OCR.get_text(debug_level="INFO")
                if "GAME INFO" in text:
                    break
                if "ENTER YOUR CODE" in text:
                    pro.press_button(Buttons.B, 1)
                    break
                pro.press_button(Buttons.A, 1)
                time.sleep(2)
    except Exception as err:
        logger.info(f"Exception in enter code, err = {err} trace = {traceback.format_exc()}")


def batch_enter_code():
    with open("code", "r") as file:
        lines = file.readlines()
    for line in lines:
        line = line.replace("\n", "")
        enter_code(line)
