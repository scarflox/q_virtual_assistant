import shutil
import importlib.util

cap = {}

cap['winfetch'] = shutil.which('winfetch') is not None
cap['win32com'] = importlib.util.find_spec('win32com') is not None
cap['sounddevice'] = importlib.util.find_spec('sounddevice') is not None
cap['coqui_tts'] = importlib.util.find_spec('TTS') is not None
cap['spotipy'] = importlib.util.find_spec('spotipy') is not None

