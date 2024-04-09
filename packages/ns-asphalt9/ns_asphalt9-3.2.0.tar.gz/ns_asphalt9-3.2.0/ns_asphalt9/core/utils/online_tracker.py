import time
from datetime import timedelta

class OnlineTracker:
    def __init__(self):
        self.is_online = False
        self.start_time = None
        self.total_online_time = 0

    def start(self):
        if not self.is_online:
            self.is_online = True
            self.start_time = time.time()  # 记录开始时间

    def stop(self):
        if self.is_online:
            self.is_online = False
            if self.start_time is not None:
                end_time = time.time()  # 获取当前时间
                self.total_online_time += end_time - self.start_time  # 累加在线时长
                self.start_time = None  # 重置开始时间

    def get_total_time(self):
        if self.is_online and self.start_time is not None:
            current_time = time.time()
            return self.format_time(self.total_online_time + (current_time - self.start_time))
        return self.format_time(self.total_online_time)

    def format_time(self, seconds):
        return str(timedelta(seconds=int(seconds)))


online_tracker = OnlineTracker()


if __name__=="__main__":
    online_tracker.start()
    time.sleep(2)
    total_time = online_tracker.get_total_time()
    print(online_tracker.start_time)
    print(total_time)