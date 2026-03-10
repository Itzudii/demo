from pathlib import Path

BASE_DIR = Path(__file__).parent
LOG_DIR = BASE_DIR / "logs"

ACTIVE_LOG = LOG_DIR / "active.jsonl"
PROCESSING_LOG = LOG_DIR / "processing.jsonl"

WATCH_PATHS = [
    r"D:\don'tDelete\Desktop\new_latest_db_chnage"
]