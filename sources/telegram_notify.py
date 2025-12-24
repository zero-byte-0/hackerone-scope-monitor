import requests
from typing import Iterable

MAX_LEN = 4000  # keep margin


class TelegramBot:
    def __init__(self, token: str, chat_id: str):
        self.url = f"https://api.telegram.org/bot{token}/sendMessage"
        self.chat_id = chat_id

    def _chunks(self, text: str) -> Iterable[str]:
        for i in range(0, len(text), MAX_LEN):
            yield text[i : i + MAX_LEN]

    def send(self, text: str) -> None:
        for chunk in self._chunks(text):
            r = requests.post(
                self.url,
                json={
                    "chat_id": self.chat_id,
                    "text": chunk,
                },
                timeout=10,
            )
            r.raise_for_status()
