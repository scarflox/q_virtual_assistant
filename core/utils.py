# core/utils.py

from TTS.api import TTS


global_tts = TTS(model_name="tts_models/en/vctk/vits", progress_bar=True)

