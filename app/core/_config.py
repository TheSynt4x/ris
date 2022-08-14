from typing import Any, Dict, List, Optional

from pydantic import BaseSettings


class Config(BaseSettings):
    client_id: str
    client_secret: str
    username: str
    password: str

    mega_username: Optional[str] = None
    mega_password: Optional[str] = None

    webhook_url: Optional[str] = None

    user_agent: str = (
        "Mozilla/5.0 (Linux; Android 6.0; "
        "Nexus 5 Build/MRA58N) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/103.0.0.0 Mobile Safari/537.36"
    )

    subreddits: List[str] = []
    categories: Dict[str, Any] = {}

    global_post_limit: int = 1

    db_conn: bool = False
    db_hostname: Optional[str] = None
    db_username: Optional[str] = None
    db_password: Optional[str] = None
    db_database: Optional[str] = None


settings = Config()
