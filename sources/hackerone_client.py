import requests
from typing import Dict, List


class HackerOneClient:
    BASE_URL = "https://api.hackerone.com/v1"

    def __init__(self, username: str, token: str):
        self.auth = (username, token)
        self.session = requests.Session()
        self.session.auth = self.auth
        self.session.headers.update({"Accept": "application/json"})

    def list_programs(self) -> List[str]:
        programs = []
        url = f"{self.BASE_URL}/hackers/programs"

        while url:
            r = self.session.get(url, timeout=15)
            r.raise_for_status()
            data = r.json()

            for p in data["data"]:
                programs.append(p["attributes"]["handle"])

            url = data.get("links", {}).get("next")

        return programs

    def get_structured_scopes(self, handle: str) -> List[Dict]:
        url = f"{self.BASE_URL}/hackers/programs/{handle}/structured_scopes"
        r = self.session.get(url, timeout=15)
        r.raise_for_status()
        return r.json()["data"]
