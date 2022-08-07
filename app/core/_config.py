from typing import Any, Dict, List

from pydantic import BaseSettings


class Config(BaseSettings):
    client_id: str
    client_secret: str
    username: str
    password: str

    user_agent: str = (
        "Mozilla/5.0 (Linux; Android 6.0; "
        "Nexus 5 Build/MRA58N) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/103.0.0.0 Mobile Safari/537.36"
    )

    subreddits: List[str] = []
    categories: Dict[str, Any] = {}


settings = Config()
