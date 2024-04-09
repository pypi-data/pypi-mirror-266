from .. import globals, consts


class ErrorProcess:
    error_pages = [
        consts.disconnected,
        consts.no_connection,
        consts.system_error,
        consts.switch_home,
        consts.no_opponents,
        consts.error_code,
    ]

    count = 0

    def __init__(self):
        pass

    def parse_page(self, page_name):
        if page_name in self.error_pages:
            self.count += 1
            globals.output_queue.put({"错误处理": self.count})


error_process = ErrorProcess()
