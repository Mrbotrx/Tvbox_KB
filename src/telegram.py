import os
import requests

class Telegram:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")

        if not self.token:
            raise ValueError("Missing TELEGRAM_BOT_TOKEN (Check GitHub Secrets + workflow env)")

        self.base = f"https://api.telegram.org/bot{self.token}"

    def get_updates(self):
        return requests.get(f"{self.base}/getUpdates", timeout=15).json()

    def send_message(self, chat_id, text):
        return requests.post(
            f"{self.base}/sendMessage",
            data={"chat_id": chat_id, "text": text},
            timeout=15
        ).json()

    def send_file(self, chat_id, file_path, caption=""):
        with open(file_path, "rb") as f:
            return requests.post(
                f"{self.base}/sendDocument",
                data={"chat_id": chat_id, "caption": caption},
                files={"document": f},
                timeout=30
            ).json()
