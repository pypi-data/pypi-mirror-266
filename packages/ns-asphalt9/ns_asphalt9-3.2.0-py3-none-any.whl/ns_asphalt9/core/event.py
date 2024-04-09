import requests
import threading


class Event(object):
    def __init__(self) -> None:
        self.url = "https://unedge.myds.me:28080/api/tracking/update"

    def update(self, name: str, content: dict = None) -> None:
        if not content:
            content = {}
        try:
            data = {
                "name": name,
                "content": content,
            }
            requests.post(self.url, json=data)
        except Exception as err:
            pass


if __name__ == "__main__":
    track = Event()
    track.update(name="test", content={"a": 1})
