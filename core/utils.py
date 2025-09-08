
"""
Helper functions: stream_ai_response, initiate_winfetch, TTS, Spotify tools.
"""

from TTS.api import TTS
import psutil
import json
import sys
import os
import subprocess
from contextlib import contextmanager
import win32com.client
import time
# ---------------- WINFETCH ----------------
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
    import core.config as cfg
    if getattr(cfg, "_global_tts", None) is None:
        print("Initializing TTS model...")
        with suppress_stdout_stderr():
            cfg._global_tts = TTS(model_name="tts_models/en/vctk/vits", progress_bar=False)
        return cfg._global_tts
    return cfg._global_tts


# ---------------- SPOTIFY UTIL ----------------

def find_spotify_process():
    import core.config as cfg
    """Check if Spotify is running."""
    for p_spotify in psutil.process_iter():
        try:
            if p_spotify.name().lower() == cfg.SPOTIFY_PROC.lower():
                return True
        except Exception:
            continue
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

# ---------------- OPENAI TOOL HELPERS ----------------


def handle_tool_call(tool_call):
    from core.config import tool_map
    func_name = tool_call.function.name
    func_args = json.loads(tool_call.function.arguments)
    if func_name in tool_map:
        return tool_map[func_name].run(func_args)
    return f"Tool {func_name} not found"

def stream_ai_response(messages, client, model_name, openai_tools):
    """
    Replacement for streaming: synchronous .create() with manual token yielding.
    Executes any tool calls and yields strings to be displayed in the GUI.
    """
    try:
        resp = client.chat.completions.create(
            model=model_name,
            messages=messages,
            tools=openai_tools
        )

        # Extract assistant message text
        content = ""
        try:
            content = resp.choices[0].message.content
        except Exception:
            content = str(resp)

        if content:
            # Yield in word-sized chunks for incremental GUI updates
            words = content.split()
            for i, w in enumerate(words):
                yield w + (" " if i < len(words) - 1 else "")
        else:
            # If assistant returned nothing
            yield "[Empty response from assistant]"

        # Check if any tool calls are embedded in the response (e.g., JSON commands)
        # Example: {"tool":"play_user_playlist","arguments":{"playlist_name":"Dont Drake and Drive"}}
        # For each tool call, execute and yield result
        # Here we assume the assistant wraps tool calls in a recognizable format
        import re, json
        tool_matches = re.findall(r"\{.*?\"tool\".*?\}", content or "")
        for t_json in tool_matches:
            try:
                t_obj = json.loads(t_json)
                tool_name = t_obj.get("tool")
                args = t_obj.get("arguments", {})
                if tool_name in openai_tools:
                    result = openai_tools[tool_name](**args)
                    yield f"\n[Tool `{tool_name}` executed: {result}]\n"
            except Exception as e:
                yield f"\n[Error executing tool: {e}]\n"

    except Exception as e:
        yield f"[Error obtaining assistant response: {e}]"
