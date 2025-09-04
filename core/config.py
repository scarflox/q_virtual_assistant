
"""
Global config and constants vars.
"""

from dotenv import load_dotenv
from pathlib import Path
import os
from openai import OpenAI
import speech_recognition as sr
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

CLIENT = OpenAI(
    base_url=OPENAI_BASE_URL,
    api_key=OPENAI_API_KEY,
)




# MIC ----------------------------------------
_raw_mic = os.getenv("MIC_INDEX", None)
if _raw_mic is None or _raw_mic.strip() == "" or _raw_mic.lower() == "none":
    MIC_INDEX = None
else:
    try:
        MIC_INDEX = int(_raw_mic)
    except ValueError:
        MIC_INDEX = None

recognizer = sr.Recognizer()
mic = sr.Microphone(device_index=MIC_INDEX)

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
SCOPE = "user-read-playback-state user-modify-playback-state user-read-currently-playing user-read-private user-read-playback-state user-modify-playback-state playlist-modify-public playlist-modify-private"
SPOTIFY_PROC = "Spotify.exe"


def get_tools():
    """Return tools and openai_tools, lazily imported to avoid circular imports."""
    from tools.spotify_player import (query_and_play_track,
                                  stop_current_playback,
                                  play_next_track, 
                                  play_user_playlist,
                                  add_song_to_playlist)
    from tools.tools import tool_to_openai, change_volume

    tools = [
            query_and_play_track,
            stop_current_playback,
            change_volume,
            play_next_track,
            play_user_playlist,
            add_song_to_playlist]

    openai_tools = [tool_to_openai(t) for t in tools]

    tool_map = {t.name: t for t in tools}
    return tools, openai_tools, tool_map

tools, openai_tools, tool_map = get_tools()

# ---------------- GLOBALS ----------------
_global_tts = None
last_3_lines=["","",""] 
TRIGGER_WORD = "Supporter"
CONVERSATION_TIMEOUT = 30 # seconds of inactivity before exiting conversation mode
WINFETCH_TIMEOUT = 5 
chat_mode = True

# ---------------- MESSAGES ---------------

messages=[
    {"role": "system", "content": """You are 'Supporter', a smart and friendly AI assistant.
            You can chat casually, answer questions, give advice, perform web searches, and assist with tasks.
            Only use specialized tools when explicitly needed.

            For music requests:
            - If the user explicitly asks to play a song, artist, or playlist, you may use the `query_and_play_track` tool.
            - If the user says "play [song/artist]" or something similar, treat everything after "play" as the song name and use the tool.
            - If the user requests to stop the music or playback, you may use the `stop_current_playback` tool.
            - If the user requests to play a playlist by it's name, call the `play_user_playlist` with the playlist name as an argument
            - Otherwise, do not assume the user wants music; respond naturally.

            For all other requests:
            - Respond directly and helpfully.
            - Use your knowledge or other available tools if relevant.
            - Reason step by step if needed, but keep your final answer concise unless the user asks for full details.

            Examples:
            - User: "Look up Avast"
            Response: "Avast is a cybersecurity software company that provides antivirus and internet security solutions."
            - User: "Play Blinding Lights by The Weeknd"
            Response: (Use `query_and_play_track` tool)
            - User: "Tell me a joke"
            Response: "Why did the computer go to therapy? It had too many bugs!"
            - User: "Play my playlist Don't Drake and Drive"
            Response: (Use `play_user_playlist` with "Don't Drake and Drive" as the argument.)

Always be friendly and helpful. Only invoke Spotify when the user clearly requests it.
    - While answering, don't use asterisk (*) for non-mathematical purposes.
"""},
    
]