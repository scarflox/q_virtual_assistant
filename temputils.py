
# SPOTIFY UTIL -----------------------

from TTS.api import TTS
import psutil
import threading
import sys
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
def initiate_winfetch():
    """Run Winfetch and return its output and height."""
    subprocess.run(
        ["powershell", "-NoProfile", "-Command", "winfetch"],
        capture_output=True,
        text=True
    )
    


# Fix terminal positioning for AI text & winfetch.
winfetch_refresh_lock = threading.Lock()
last_3_lines=["","",""] 

def winfetch_refresher_loop():
    while True:
        time.sleep(WINFETCH_TIMEOUT)
        with winfetch_refresh_lock:
            sys.stdout.write('\x1b[?25l')
            sys.stdout.flush()

            sys.stdout.write('\x1b[H')
            sys.stdout.write('\x1b[2J')
            sys.stdout.flush()

            initiate_winfetch()

            for line in last_3_lines:
                print("\x1b[K", end="")
            
            sys.stdout.flush()

            sys.stdout.write('\x1b[?25h')
            sys.stdout.flush()


            
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
