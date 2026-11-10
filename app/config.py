import os
from dataclasses import dataclass

@dataclass
class Settings:
    host: str = os.getenv("RTBF_HOST", "127.0.0.1")
    port: int = int(os.getenv("RTBF_PORT", "8000"))
    web_port: int = int(os.getenv("WEB_APP_PORT", "8001"))
    cots_port: int = int(os.getenv("COTS_APP_PORT", "8002"))
    green_port: int = int(os.getenv("GREEN_SCREEN_PORT", "2323"))
    data_dir: str = os.getenv("DATA_DIR", "./data")

settings = Settings()
