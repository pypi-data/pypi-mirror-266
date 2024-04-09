import threading
from typing import Any
import uuid
import time
import json

from .. import consts, globals, ocr
from ..controller import Buttons, pro
from ..utils.log import logger
from ..utils.count import count
from ..utils.track_navi_data import get_navi_data
from ..utils.track_navi_data_v2 import track_navi_data as navi_data_v2
from .common import get_race_mode


def generate_random_filename():
    random_name = str(uuid.uuid4().hex)[:8]
    return random_name


def get_action(progress, navi_data):
    globals.output_queue.put({"比赛进度": progress})
    logger.info(f"progress = {progress}")
    if navi_data:
        for p, a, d in navi_data:
            if abs(p - progress) <= 1:
                return a, d
    return None, 0


def race_worker(
    progress_manager, navi_data, pro, race_navi_event, race_worker_quit, track_name
):
    count = 0
    processed_progress = []
    if track_name in navi_data_v2:
        action_data = navi_data_v2[track_name]["data"]
        version = 2
    else:
        action_data = navi_data
        version = 1
    while race_navi_event.is_set():
        if version == 2:
            progress = progress_manager.get_progress()
            progress = str(round(progress))
            if progress in action_data and progress not in processed_progress:
                buttons = action_data[progress]
                for button in buttons:
                    if button["key"] in ["DPAD_LEFT", "DPAD_RIGHT", "Y"]:
                        pro.press_buttons(button["key"])
                    else:
                        pro.press_buttons(
                            button["key"], down=button["down"] / 1000, up=0.05
                        )
                processed_progress.append(progress)

        else:
            progress = progress_manager.get_progress()
            action, duration = get_action(progress, action_data)
            if action:
                if action == "L":
                    pro.press_buttons(Buttons.DPAD_LEFT)
                elif action == "R":
                    pro.press_buttons(Buttons.DPAD_RIGHT)
                elif action == "LL":
                    pro.press_buttons([Buttons.DPAD_LEFT, Buttons.DPAD_LEFT])
                elif action == "RR":
                    pro.press_buttons([Buttons.DPAD_RIGHT, Buttons.DPAD_RIGHT])
                elif action == "B":
                    pro.press_buttons(Buttons.B, duration)
                elif action == "BB":
                    pro.press_buttons(Buttons.B, 0.03, 0.03)
                    pro.press_buttons(Buttons.B, 0.03, 0.03)
                elif action == "YY-1":
                    pro.press_button(Buttons.Y, 0.7)
                    pro.press_button(Buttons.Y, 0)
                    count = 0
                elif action in ["YY-2", "YY-3"]:
                    pro.press_buttons([Buttons.Y, Buttons.Y])
                    count = 0
                else:
                    logger.info(f"Action not support, action = {action}!")
            else:
                if count % 6 == 0:
                    pro.press_button(Buttons.Y, 0.7)
                    pro.press_button(Buttons.Y, 0)
                else:
                    time.sleep(0.2)
            count += 1

    logger.info("Action woker quit.")
    race_worker_quit.set()


def start_race_worker(
    progress_manager, navi_data, pro, race_navi_event, race_worker_quit, track_name
):
    t = threading.Thread(
        target=race_worker,
        args=(
            progress_manager,
            navi_data,
            pro,
            race_navi_event,
            race_worker_quit,
            track_name,
        ),
        daemon=True,
    )
    t.start()
    return t


class ProgessManager:
    fit_point_num = 2

    def __init__(self) -> None:
        self.history_progress = []
        self.start_time = time.time()
        self.offset_progress = 0
        self.enable_fit = False

    def set_offset_progress(self, start_time, end_time, track_time):
        offset_progress = (end_time - start_time) * 100 / int(track_time)
        self.offset_progress = round(offset_progress, 2)
        if end_time - start_time > 0.8:
            self.enable_fit = True

    def get_offset_progress(self):
        return self.offset_progress

    def set_start_time(self):
        self.start_time = time.time()

    def put_progress(self, progress):
        if progress > 0:
            duration = round(time.time() - self.start_time, 2)
            if self.enable_fit:
                if not self.is_m_match((duration, progress)):
                    return
            else:
                if self.history_progress and abs(progress - self.history_progress[-1][1]) > 4:
                    return
            self.history_progress.append((duration, progress))

    def get_progress(self):
        if self.enable_fit:
            fit_progress = self.get_fit_progress()
        else:
            if self.history_progress:
                fit_progress = self.history_progress[-1][1]
            else:
                fit_progress = -1
        return fit_progress

    def is_m_match(self, progress):
        # 判断斜率是否相近
        if len(self.history_progress) < 2:
            return True
        y = [p for _, p in self.history_progress[-2:]]
        x = [t for t, _ in self.history_progress[-2:]]
        # 计算拟合的斜率和截距
        mean_x = sum(x) / 2
        mean_y = sum(y) / 2
        m1 = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y)) / sum(
            (xi - mean_x) ** 2 for xi in x
        )

        y = [self.history_progress[-1][1], progress[1]]
        x = [self.history_progress[-1][0], progress[0]]
        m2 = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y)) / sum(
            (xi - mean_x) ** 2 for xi in x
        )
        # return abs(m1 - m2) < 0.5
        # logger.info(f"m1 = {m1} m2 = {m2} abs(m1 - m2) = {abs(m1 - m2)}")
        if m2 < 0:
            return False
        if m2 > 2:
            return False
        return True

    def get_fit_progress(self):
        if len(self.history_progress) >= 2:
            y = [p for _, p in self.history_progress[-2:]]
            x = [t for t, _ in self.history_progress[-2:]]
            # 计算拟合的斜率和截距
            mean_x = sum(x) / 2
            mean_y = sum(y) / 2
            m = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y)) / sum(
                (xi - mean_x) ** 2 for xi in x
            )
            b = mean_y - m * mean_x
            duration = round(time.time() - self.start_time, 2)
            fit_progress = round(duration * m + b + self.offset_progress, 2)
            return fit_progress
        if self.history_progress:
            return self.history_progress[-1][1] + self.offset_progress
        return -1


def enter_race():
    pro.press_group([Buttons.DPAD_RIGHT] * 4, 0)
    pro.press_button(Buttons.A, 3)
    process_race()


def process_race():
    logger.info("Start racing.")
    track = None
    progress = -1
    race_navi_event = threading.Event()
    race_worker_quit = threading.Event()
    mode = get_race_mode()
    enable_navi = False
    if mode in globals.CONFIG:
        enable_navi = globals.CONFIG[mode]["自动选路"]
    progress_manager = ProgessManager()
    logger.info(f"enable_navi = {enable_navi}")
    has_next = False
    race_start_time = time.time()
    final_pos = None
    ocr.OCR.last_progress = -1
    while globals.G_RACE_RUN_EVENT.is_set():
        if 0 <= progress < 100:
            progress = ocr.OCR.get_progress(capture=True)
            if progress >= 98:
                pos = ocr.OCR.get_pos()
                if pos:
                    final_pos = pos
        else:
            page = ocr.OCR.get_page()
            progress = ocr.OCR.get_progress()
            if page.name in [
                consts.loading_race,
                consts.racing,
                consts.legendary_hunt_loading,
            ]:
                track = ocr.OCR.get_track()
                if not globals.EVENT_UPDATE:
                    content = ocr.OCR.get_player_info()
                    if content:
                        globals.notify_queue.put({"event": "play", "content": content})
                        globals.EVENT_UPDATE = True
                if track:
                    logger.info(f"Current track is {track['trackcn']}")
                if mode == consts.car_hunt_zh:
                    track_name = "CAR HUNT"
                elif mode == consts.legendary_hunt_zh:
                    track_name = "LEGENDARY HUNT"
                else:
                    track_name = track["tracken"] if track else None
                navi_data = get_navi_data(track_name)
                if not navi_data:
                    count.not_support_track_inc(track_name)
                if navi_data and enable_navi:
                    logger.info("Start aciton worker")
                    race_navi_event.set()
                    race_thread = start_race_worker(
                        progress_manager,
                        navi_data,
                        pro,
                        race_navi_event,
                        race_worker_quit,
                        track_name,
                    )
                    break
            if page.name == consts.car_info:
                pro.press_a()

            if page.name in [
                consts.tickets,
            ]:
                from .. import tasks

                pro.press_group([Buttons.B] * 5, 3)
                tasks.TaskManager.set_done()
                break

            has_next = ocr.OCR.has_next()

            if has_next or page.name in [
                consts.race_score,
                consts.race_results,
                consts.race_reward,
                consts.system_error,
                consts.connect_error,
                consts.no_connection,
                consts.multi_player,
                consts.error_code,
            ]:
                break
        globals.output_queue.put({"比赛进度": progress})
        pro.press_button(Buttons.Y, 0.7)
        pro.press_button(Buttons.Y, 0)
        if time.time() - race_start_time > 180:
            break

    if race_navi_event.is_set():
        progress_manager.set_start_time()
        while globals.G_RACE_RUN_EVENT.is_set():
            start_time = time.time()
            progress = ocr.OCR.get_progress(capture=True)
            if progress >= 98:
                pos = ocr.OCR.get_pos()
                if pos:
                    final_pos = pos
                logger.info(f"Get final_pos is {final_pos}")
            end_time = time.time()
            if mode in [consts.car_hunt_zh, consts.legendary_hunt_zh]:
                track_time = 50
            else:
                track_time = int(track["time"])
            progress_manager.set_offset_progress(start_time, end_time, track_time)
            progress_manager.put_progress(progress)
            logger.info(f"Current progress is {progress}")
            if progress < 0:
                has_next = ocr.OCR.has_next()
                if has_next:
                    break
            if time.time() - race_start_time > 180:
                break
        race_navi_event.clear()
        race_worker_quit.wait(timeout=5)

    count.total_race_count_inc()
    if final_pos:
        logger.info(f"Final pos = {final_pos}")
        if track:
            count.track_rank_inc(mode, track["tracken"], final_pos)
        count.race_rank_inc(mode, final_pos)
        logger.info(
            f"mode = {mode} rank = {json.dumps(count.get_race_rank(mode), indent=2, ensure_ascii=False)}"
        )
        logger.info(
            f"mode = {mode} track rank = {json.dumps(count.get_track_rank(mode), indent=2, ensure_ascii=False)}"
        )
    logger.info(f"Already finished {count.total_race_count} times.")
    logger.info(f"Not recognized track = {count.not_recongnized_track}")
    logger.info(f"Not support track = {count.not_support_track}")
    globals.output_queue.put({"完赛次数": count.total_race_count})
    if has_next:
        pro.press_button(Buttons.B, 1)

    # race reward race result congretulations
    for _ in range(4):
        time.sleep(2)
        has_next = ocr.OCR.has_next(capture=True)
        logger.info(f"has_next = {has_next}")
        if has_next:
            pro.press_b()
        else:
            break

    ocr.OCR.next_page = consts.modes_zh_page_mapping.get(mode, "")
