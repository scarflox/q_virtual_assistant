# core/utils.py

from TTS.api import TTS
import psutil
import win32com.client
import time

_global_tts = None
SPOTIFY_PROC = "Spotify.exe"

def get_tts():
    global _global_tts
    if _global_tts is None:
        print("Initializing TTS model...")
        _global_tts = TTS(model_name="tts_models/en/vctk/vits", progress_bar=True)
    return _global_tts


# SPOTIFY UTIL -----------------------


def find_spotify_process():
    for p_spotify in psutil.process_iter():
        if p_spotify.name().lower() == SPOTIFY_PROC.lower():
            return True
    return False
        
def start_spotify_exe():
    shell = win32com.client.Dispatch("Shell.Application")
    folder_items = shell.Namespace("shell:AppsFolder")
    for item in folder_items.Items():
        if "Spotify" in item.Name:
           item.InvokeVerbEx()
           break
        

def wait_for_spotify_boot(max_timeout=30):
    start_time = time.time()
    while time.time() - start_time < max_timeout:
        if find_spotify_process():
            print('Spotify is up.')
            time.sleep(2.5)
            return True
        else:
            time.sleep(0.5)
    return False


# SPOTIFY UTIL -----------------------