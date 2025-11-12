from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
DB_META_FILE = ROOT_DIR / "db_meta.json"
DATA_DIR = ROOT_DIR / "data"

VALID_TYPES = {"int", "str", "bool"}
