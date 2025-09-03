
"""
    Entry point for program.
"""

from core.terminal_gui import TerminalGUI
from core.utils import get_tts

if __name__ == "__main__":
    get_tts() # Load TTS model on startup.
    TerminalGUI().run() # Start GUI (Handles chat + voice internally.)

    