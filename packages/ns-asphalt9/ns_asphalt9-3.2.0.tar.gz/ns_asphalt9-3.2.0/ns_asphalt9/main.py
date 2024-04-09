import argparse
import datetime
import multiprocessing
import subprocess
import os
import shutil
import threading
import time
import traceback
import types
import inspect
import cv2
import re

from PIL import Image

from .core import consts
from .core import globals as G
from .core.controller import pro
from .core.gui.app import App
from .core.ocr import OCR
from .core.pages import Page
from .core.tasks import TaskManager
from .core.utils.log import logger
from .core.utils.online_tracker import online_tracker
from .core.utils.notify import Notify
from .core.actions import *  # noqa
from .core.utils.page_stack import page_stack
from .core.event import Event
from .core.reset_data import reset_data


G.input_packet["packet"] = pro.nx.create_input_packet()


def process_screen(page: Page):
    """根据显示内容执行动作"""

    page_stack.add_item(page.name)
    if page.name != consts.empty and page.action:
        page.call_action()

    if page_stack.check_uniform():
        if page.action:
            TaskManager.task_enter(consts.restart, page)
        else:
            TaskManager.task_enter(G.CONFIG["模式"], page)


def capture():
    debug = os.environ.get("A9_DEBUG", 0)
    filename = "".join([str(d) for d in datetime.datetime.now().timetuple()]) + ".jpg"
    if not debug:
        shutil.copy("./output.jpg", f"./{filename}")
    return filename


def event_loop():
    TaskManager.task_init()

    while G.G_RACE_RUN_EVENT.is_set() and G.G_RUN.is_set():
        try:
            page = OCR.get_page()
            if page.next_page:
                OCR.next_page = page.next_page
            if page.division:
                G.DIVISION = page.division
            if page.mode:
                G.MODE = page.mode
            dispatched = TaskManager.task_dispatch(page)
            if not dispatched:
                process_screen(page)
            else:
                time.sleep(3)
        except Exception as err:
            logger.error(
                f"Caught exception, err = {err}, traceback = {traceback.format_exc()}"
            )

    TaskManager.destroy()
    G.G_RACE_QUIT_EVENT.set()


def command_input(queue):
    while G.G_RUN.is_set():
        command = queue.get()
        logger.info(f"Get command from queue: {command}")
        if isinstance(command, str):
            if command == "stop":
                # 停止挂机
                if G.G_RACE_RUN_EVENT.is_set():
                    G.G_RACE_RUN_EVENT.clear()
                    logger.info("Stop event loop.")
                    G.G_RACE_QUIT_EVENT.wait()
                    logger.info("Event loop stoped.")
                    G.output_queue.put({"自动状态": "已停止"})
                else:
                    logger.info("Event loop not running.")

            elif command == "run":
                # 开始挂机
                if G.G_RACE_RUN_EVENT.is_set():
                    logger.info("Event loop is running.")
                else:
                    G.G_RACE_RUN_EVENT.set()
                    G.G_RACE_QUIT_EVENT.clear()
                    logger.info("Start run event loop.")
                    G.output_queue.put({"自动状态": "运行中"})

            elif command == "quit":
                # 退出程序
                logger.info("Quit main.")
                G.G_RUN.clear()
                logger.info(f"G_RUN status = {G.G_RUN.is_set()}")
                for timer in TaskManager.timers:
                    timer.cancel()

            elif command == "ocr":
                OCR.get_page()

            elif "code" in command:
                from .core.actions.autocode import enter_code, batch_enter_code
                if command == "batch_code":
                    batch_enter_code()
                else:
                    _, redeem_code = command.split(" ")
                    enter_code(redeem_code)
    
            elif re.findall(r"\S \d+", command):
                button, count = command.split(" ")
                for i in range(int(count)):
                    pro.press_button(button.upper(), 0)

            elif command == "help":
                # 帮助
                lines = [
                    "支持以下命令:",
                    "run: 进入自动执行模式",
                    "stop: 退出自动模式",
                    "quit: 退出程序",
                    "支持的按键操作:",
                    "1: L",
                    "2: ZL",
                    "8: R",
                    "9: ZR",
                    "6: MINUS",
                    "7: PLUS",
                    "[: CAPTURE",
                    "]: HOME",
                    "i: X",
                    "j: Y",
                    "l: A",
                    "k: B",
                    "s: DPAD_DOWN",
                    "w: DPAD_UP",
                    "a: DPAD_LEFT",
                    "d: DPAD_RIGHT",
                    "支持的内置函数:",
                ]

                import builtins

                non_builtin_functions = {
                    name: obj.__doc__
                    for name, obj in globals().items()
                    if callable(obj)
                    and name not in dir(builtins)
                    and not inspect.isclass(obj)
                }
                for name, doc in non_builtin_functions.items():
                    lines.append(f"{name}: {doc}")
                logger.info("\n".join(lines))

            elif command in consts.KEY_MAPPING:
                # 手柄操作
                control_data = consts.KEY_MAPPING.get(command)
                if isinstance(control_data, str):
                    pro.press_button(control_data, 0)
                if isinstance(control_data, types.FunctionType):
                    control_data()
            else:
                global_vars = globals()
                func = global_vars.get(command, "")
                if isinstance(func, types.FunctionType):
                    logger.info(f"{command} process start!")
                    try:
                        func()
                        logger.info(f"{command} process end!")
                    except Exception as err:
                        logger.info(f"{command} process err = {err}")
                else:
                    logger.info(f"{command} command not support!")

        elif isinstance(command, dict):
            try:
                if "action" in command:
                    control_data = consts.KEY_MAPPING.get(command["key"])
                    packet = G.input_packet["packet"]
                    if command["action"] == "press":
                        packet[control_data] = True
                    else:
                        packet[control_data] = False
                    G.input_packet["packet"] = packet
                else:
                    logger.info("Received config update message.")
                    G.CONFIG = command
            except Exception as err:
                logger.info(
                    f"{command} process err = {err} traceback = {traceback.format_exc()}"
                )

        else:
            logger.info(f"{command} command not support!")


def start_command_input(queue):
    t = threading.Thread(target=command_input, args=(queue,), daemon=True)
    t.start()


def worker(input_queue, output_queue):
    G.G_RACE_QUIT_EVENT.set()
    G.G_RUN.set()
    G.output_queue = output_queue

    console_version()
    start_command_input(input_queue)
    while G.G_RUN.is_set():
        if G.G_RACE_RUN_EVENT.is_set():
            event_loop()
        else:
            time.sleep(1)
    logger.info("Woker quit.")


def start_worker():
    p = multiprocessing.Process(target=worker, args=(G.input_queue, G.output_queue))
    p.daemon = True
    p.start()


def output_worker(app, event):
    logger.info("Start output worker.")
    while event.is_set():
        data = G.output_queue.get()
        if isinstance(data, str):
            app.show(data)
        if isinstance(data, dict):
            if "自动状态" in data:
                if data["自动状态"] == "已停止":
                    online_tracker.stop()
                else:
                    online_tracker.start()
            if "在线时长" in data:
                online_tracker.start_time = None
                online_tracker.total_online_time = 0
            data.update({"在线时长": online_tracker.get_total_time()})
            # logger.info(f"update race data = {data}")
            app.update_race_data(data)


def start_output_worker(app):
    t = threading.Thread(target=output_worker, args=(app, G.G_OUT_WORKER), daemon=True)
    t.start()


def notify_worker(event):
    logger.info("Start notify worker.")
    while event.is_set():
        if G.notify_queue.empty():
            time.sleep(1)
            continue
        data = G.notify_queue.get()
        logger.info(f"Process notify get {data}.")
        if isinstance(data, dict):
            if "event" in data:
                e = Event()
                e.update(name=data["event"], content=data["content"])
            if "notify" in data:
                notify = Notify(host=data["host"], key=data["key"])
                notify.shop_refresh()


def start_notify_worker():
    t = threading.Thread(target=notify_worker, args=(G.G_OUT_WORKER,), daemon=True)
    t.start()


def on_closing(app):
    G.G_RUN.clear()
    logger.info(f"G_RUN state {G.G_RUN.is_set()}")
    G.output_queue.put("Quit App.")
    app.destroy()


def init_config():
    parser = argparse.ArgumentParser(description="NS Asphalt9 Tool.")
    parser.add_argument("-c", "--config", type=str, default="settings", help="自定义配置文件")
    args = parser.parse_args()
    return args.config


def console_version():
    try:
        output = subprocess.check_output(
            f"pip show ns-asphalt9 | grep Version", shell=True, universal_newlines=True
        )
        output = output.strip()
    except subprocess.CalledProcessError:
        output = "Package not found."

    logger.info(output)


def stream_worker():
    cap = cv2.VideoCapture("/dev/video0")
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 20)

    if not cap.isOpened():
        logger.info("无法打开视频设备")
    # 循环读取视频帧并显示
    while True:
        # 读取一帧图像
        ret, frame = cap.read()
        # 如果正确读取帧，ret为True
        if not ret:
            logger.info("无法获取视频帧")
            continue
        # 显示帧
        G.frame_queue.push(frame)
        if G.video_queue.full():
            G.video_queue.get()
        G.video_queue.put(frame)


def start_stream_worker():
    t = threading.Thread(target=stream_worker, args=(), daemon=True)
    t.start()


def input_worker(nxbt, controller_index):
    while True:
        packet = G.input_packet["packet"]

        # Calculating left x/y stick values
        ls_x_value = 0
        ls_y_value = 0
        if packet["L_STICK"]["LS_LEFT"]:
            ls_x_value -= 100
        if packet["L_STICK"]["LS_RIGHT"]:
            ls_x_value += 100
        if packet["L_STICK"]["LS_UP"]:
            ls_y_value += 100
        if packet["L_STICK"]["LS_DOWN"]:
            ls_y_value -= 100
        packet["L_STICK"]["X_VALUE"] = ls_x_value
        packet["L_STICK"]["Y_VALUE"] = ls_y_value

        # Calculating right x/y stick values
        rs_x_value = 0
        rs_y_value = 0
        if packet["R_STICK"]["RS_LEFT"]:
            rs_x_value -= 100
        if packet["R_STICK"]["RS_RIGHT"]:
            rs_x_value += 100
        if packet["R_STICK"]["RS_UP"]:
            rs_y_value += 100
        if packet["R_STICK"]["RS_DOWN"]:
            rs_y_value -= 100
        packet["R_STICK"]["X_VALUE"] = rs_x_value
        packet["R_STICK"]["Y_VALUE"] = rs_y_value

        nxbt.set_controller_input(controller_index, packet)
        time.sleep(1 / 150)


def start_input_worker():
    input_process = multiprocessing.Process(
        target=input_worker, args=(pro.nx, pro.controller_index)
    )
    input_process.start()


def main():
    G.G_OUT_WORKER.set()
    config_name = init_config()
    start_worker()
    app = App(G.input_queue, config_name, G.video_queue)
    start_output_worker(app)
    start_input_worker()
    start_notify_worker()
    start_stream_worker()
    G.notify_queue.put({"event": "open", "content": {}})
    app.protocol("WM_DELETE_WINDOW", lambda: on_closing(app))
    app.mainloop()
    print("App quit quit.")


if __name__ == "__main__":
    main()
