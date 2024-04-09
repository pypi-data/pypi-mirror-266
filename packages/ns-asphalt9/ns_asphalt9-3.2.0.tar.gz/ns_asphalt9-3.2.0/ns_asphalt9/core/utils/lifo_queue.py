from multiprocessing import Manager, Lock


class LIFOQueue:
    def __init__(self, maxsize=5):
        self.manager = Manager()
        self.queue = self.manager.list()
        self.lock = Lock()
        self.maxsize = maxsize

    def push(self, item):
        with self.lock:
            self.queue.append(item)
            if len(self.queue) > self.maxsize:
                self.queue.pop(0)  # 移除队列的第一个元素

    def pop(self):
        with self.lock:
            if self.queue:
                return self.queue.pop()  # 移除队列的最后一个元素
            return None

    def tail(self):
        with self.lock:
            if self.queue:
                return self.queue[-1]
            return None

    def size(self):
        with self.lock:
            return len(self.queue)
