import os

MODULE_PATH = os.path.dirname(os.path.abspath(__file__))

ALLOWED_ORIGINS: list[str] = [
    "http://diary.cochaviz.internal",
    "https://diary.cochaviz.ineternal",
    "http://localhost",
] + os.getenv("ALLOWED_ORIGINS", "").split(",")

# environment variables

SERVER_PORT: int = int(os.getenv("HTTP_PORT", 8080))
DEV_MODE: bool = os.getenv("DEV_MODE") is not None
