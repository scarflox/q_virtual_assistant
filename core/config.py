from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.getenv("DATA_DIR", BASE_DIR / "data")).expanduser()


def get_env(name, required=False, default=None):
    val = os.getenv(name, default)
    if required and not val:
        raise RuntimeError(f"{name} is required. Please set it in .env or env")
    return val

OPENAI_API_KEY = get_env("OPENAI_API_KEY", required=True)
OPENAI_MODEL_NAME = get_env("OPENAI_MODEL_NAME", required=True)
OPENAI_BASE_URL = get_env("OPENAI_BASE_URL", default="https://api.openai.com/v1")

# MIC CONSISTENT - HANDLING.
_raw_mic = os.getenv("MIC_INDEX", None)
if _raw_mic is None or _raw_mic.strip() == "" or _raw_mic.lower() == "none":
    MIC_INDEX = None
else:
    try:
        MIC_INDEX = int(_raw_mic)
    except ValueError:
        MIC_INDEX = None

# SPOTIFY CONSISTENTS -------------------


# SPOTIFY_CACHE_PATH may be provided as:
# - Empty (use default DATA_DIR/.cache)
# - A dir path (We'll create a file inside it)
# - A file path (We'll use the file directly)
_raw_cache = os.getenv("SPOTIFY_CACHE_PATH", "").strip() or None

if _raw_cache:
    _cache_candidate = Path(_raw_cache).expanduser()
else:
    _cache_candidate = (DATA_DIR / ".cache").expanduser()

 # Determine a Path object for the cache area; default to DATA_DIR/.cache

# If candidate is a dir, use it as a directory and creaate a file inside.
if _cache_candidate.exists() and _cache_candidate.is_dir() or _cache_candidate.suffix == "":
    cache_dir = _cache_candidate
    SPOTIFY_CACHE_FILE = cache_dir / "spotipy_cache"
else:
    cache_dir = _cache_candidate.parent
    SPOTIFY_CACHE_FILE = _cache_candidate

cache_dir.mkdir(parents=True, exist_ok=True)

# stable cache name inside dir.
SPOTIFY_CACHE_FILE = str(SPOTIFY_CACHE_FILE.resolve())

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = "http://127.0.0.1:8888/callback"
SCOPE = "user-read-playback-state user-modify-playback-state user-read-currently-playing user-read-private"
