
from TTS.api import TTS
from ctypes import cast, POINTER
from langchain.tools import tool
from comtypes import CLSCTX_ALL
import psutil
import threading
import sys
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import os
import subprocess
from contextlib import contextmanager
import win32com.client
import time

# ---------------- GLOBALS ----------------
_global_tts = None
SPOTIFY_PROC = "Spotify.exe"
WINFETCH_TIMEOUT = 5 
# ---------------- WINFETCH ----------------

winfetch_refresh_lock = threading.Lock()
last_3_lines=["","",""] 

def initiate_winfetch():
    """Run Winfetch and return its output as string."""
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", "winfetch"],
            capture_output=True,
            text=True
        )
        return result.stdout
    except Exception as e:
        return f"Winfetch error: {e}\n"


# Fix terminal positioning for AI text & winfetch.


_last_winfetch_output = ""
_last_ai_lines = ["", "", ""]

def redraw_terminal(force=False):
    """Clear terminal, print Winfetch + last 3 AI lines, only if changed or forced."""
    global _last_winfetch_output, _last_ai_lines

    with winfetch_refresh_lock:
        winfetch_output = initiate_winfetch()

        # Check if anything changed
        if force or winfetch_output != _last_winfetch_output or last_3_lines != _last_ai_lines:
            _last_winfetch_output = winfetch_output
            _last_ai_lines = last_3_lines.copy()

            sys.stdout.write('\x1b[H\x1b[2J')  # clear screen
            sys.stdout.flush()

            # Print Winfetch
            print(winfetch_output, end="")

            # Print last 3 AI lines
            for line in last_3_lines:
                print((line or "").ljust(80))

            sys.stdout.flush()


def winfetch_refresher_loop():
    """Refresh only when content changes, every few seconds as a fallback."""
    while True:
        redraw_terminal()
        time.sleep(WINFETCH_TIMEOUT)

            
# ---------------- TTS ----------------
@contextmanager
def suppress_stdout_stderr():
    """Context manager to suppress stdout and stderr."""
    with open(os.devnull, 'w') as devnull:
        old_out, old_err = sys.stdout, sys.stderr
        sys.stdout, sys.stderr = devnull, devnull
        try:
            yield
        finally:
            sys.stdout, sys.stderr = old_out, old_err


def get_tts():
    global _global_tts
    if _global_tts is None:
        print("Initializing TTS model...")
        with suppress_stdout_stderr():
            _global_tts = TTS(model_name="tts_models/en/vctk/vits", progress_bar=False)
    return _global_tts


# ---------------- SPOTIFY UTIL ----------------
def find_spotify_process():
    """Check if Spotify is running."""
    for p_spotify in psutil.process_iter():
        if p_spotify.name().lower() == SPOTIFY_PROC.lower():
            return True
    return False


def start_spotify_exe():
    """Start Spotify via Shell.Application."""
    shell = win32com.client.Dispatch("Shell.Application")
    folder_items = shell.Namespace("shell:AppsFolder")
    for item in folder_items.Items():
        if "Spotify" in item.Name:
            item.InvokeVerbEx()
            break


def wait_for_spotify_boot(max_timeout=30):
    """Wait for Spotify to start."""
    start_time = time.time()
    while time.time() - start_time < max_timeout:
        if find_spotify_process():
            print('Spotify is up.')
            time.sleep(2.5)
            return True
        else:
            time.sleep(0.5)
    return False


def tool_to_openai(tool):
    """Convert a Python tool object to OpenAI-compatible function schema."""
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.args_schema.schema() if tool.args_schema else {
                "type": "object",
                "properties": {},  # fallback
                "required": [],
            },
        },
    }


@tool
def change_volume(new_volume):

    """Handles Computer's volume %
       - new_volume is the argument for this function, it is a float.
       - If a user wants to change his volume, this is the right tool to do it.
       - .SetMasterVolumeLevelScalar() takes a float between 0.0 - 1.0, 1.0 is 100% volume, 0.0 is 0%, So if a user says 
       something like "Change my volume to 50" or "Make my volume 25%", just pass the whole '25' or '50' number,
       it will be divided by 100 here.
       - Returns string for tts to read with new_volume (new_volume) is a float.
       - If user asks to mute his sound, simply pass new_volume as `0.0`.
       
    """
    if 0 <= new_volume <= 100:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMasterVolumeLevelScalar(new_volume / 100, None)
        return f"Set volume to {new_volume}%"
    else:
        return f"Invalid volume requested."
