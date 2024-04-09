import re
from .page_stack import PageStack
from .log import logger
from .. import globals, consts


class CreditsManager:
    parse_pages = [
        consts.world_series,
        consts.limited_series,
        consts.trial_series,
        consts.select_car,
        consts.multi_player,
        consts.carhunt,
        consts.legendary_hunt,
        consts.daily_events,
        consts.car_info,
    ]

    def __init__(self):
        self.blue_stack = PageStack(max_length=3)
        self.gold = 0
        self.blue = 0
        self.gold_history = []
        self.init_gold = 0
        self.count_gold = 0

    def parse_text(self, text, page_name):
        if page_name not in self.parse_pages:
            return
        results = re.findall(r"[,1234567890]+", text)
        filtered_num = []
        for r in results:
            if "," in r and len(r) >= 3:
                filtered_num.append(r)
        if len(filtered_num) >= 2:
            blue = int(filtered_num[0].replace(",", ""))
            gold = filtered_num[1]
            split_num = gold.split(",")
            if len(split_num[-1]) > 3:
                return
            if len(split_num[-1]) < 3:
                split_num[-1] = split_num[-1] + "0" * (3 - len(split_num[-1]))
            gold = int("".join(split_num))
            self.add_item(blue, gold)
            logger.info(f"blue = {self.blue} gold = {self.gold}")
            globals.output_queue.put(
                {"当前蓝币": self.blue, "当前金币": self.gold, "获得金币": self.count_gold}
            )

    def add_item(self, blue, gold):
        self.blue_stack.add_item(blue)
        if self.blue_stack.check_uniform():
            self.blue = self.blue_stack.items[0]
        if gold > self.gold:
            self.gold = gold
            self.gold_history.append(gold)
            if len(self.gold_history) >= 5 and not self.init_gold:
                for g in self.gold_history[:-1]:
                    g = str(g)
                    last_gold = str(self.gold_history[-1])
                    if len(g) == len(last_gold) and g[:2] == last_gold[:2]:
                        self.init_gold = int(g)
                        break
            if self.init_gold:
                self.count_gold = self.gold - self.init_gold


credits = CreditsManager()
