# core/terminal_gui.py
"""
Terminal GUI — cleaned up input handler and sanitized system summary.
"""
import time
import threading
import platform
import datetime
from rich.text import Text
from textual.app import App, ComposeResult
from core.utils import stream_ai_response
from core.config import (
    last_3_lines,
    CLIENT,
    OPENAI_MODEL_NAME,
    openai_tools,
    messages,
    mic,
    recognizer,
    TRIGGER_WORD,
    CONVERSATION_TIMEOUT,
)
from textual.widgets import Static, RichLog, Input
import core.audio_feedback as af
import speech_recognition as sr
import psutil


def _get_system_summary() -> str:
    """Return a short, ASCII-safe system summary (no fancy box art)."""
    try:
        uname = platform.uname()
        cpu = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        uptime_seconds = time.time() - psutil.boot_time()
        uptime = str(datetime.timedelta(seconds=int(uptime_seconds)))
        return (
            f"{uname.system} {uname.release} ({uname.machine})\n"
            f"CPU: {cpu:.0f}%  Mem: {mem.percent:.0f}% ({int(mem.used/1024**2)}MB/{int(mem.total/1024**2)}MB)\n"
            f"Disk: {disk.percent:.0f}%  Uptime: {uptime}"
        )
    except Exception:
        return "System info unavailable."


class TerminalGUI(App):
    CSS_PATH = None

    def __init__(self):
        super().__init__()
        self.mode = "chat"
        self.input_widget = None
        self.chat_log = None
        self.conversation_mode = False
        self.last_interaction_time = None

        self._response_lock = threading.Lock()
        self._stop_threads = False

    def compose(self) -> ComposeResult:
        yield Static("Loading...", id="startup_status") 
        yield Static(_get_system_summary(), id="system_summary")
        self.chat_log = RichLog(id="chat_log")
        yield self.chat_log
        self.input_widget = Input(placeholder="What's on your mind?", id="chat_input")
        yield self.input_widget

    def on_mount(self):
        self._update_input_placeholder()
        self.set_focus(self.input_widget)
        self.query_one("#startup_status", Static).update("Loading...")

        def _init_heavy():
            from core.utils import get_tts
            try:
                get_tts()  # preload model
            except Exception as e:
                self.call_from_thread(
                    self.query_one("#startup_status", Static).update,
                    f"Load failed: {e}"
                )
                return
            
            # mark ready once finished
            
            self.call_from_thread(
                self.query_one("#startup_status", Static).update,
                "Ready."
            )

        threading.Thread(target=_init_heavy, daemon=True).start()
        # refresh the system summary periodically in the background
        threading.Thread(target=self._system_summary_refresher, daemon=True).start()
        # start voice listener in background
        threading.Thread(target=self.voice_loop, daemon=True).start()

    def on_unmount(self) -> None:
        self._stop_threads = True

    def _system_summary_refresher(self, interval: float = 5.0):
        while not self._stop_threads:
            try:
                summary = _get_system_summary()
                # update widget safely on the main thread
                try:
                    self.call_from_thread(self._update_system_summary, summary)
                except Exception:
                    pass
            except Exception:
                pass
            time.sleep(interval)

    def _update_input_placeholder(self):
        placeholder = f"Mode: {self.mode} - What's on your mind?"
        try:
            input_w = self.query_one("#chat_input", Input)
            input_w.placeholder = placeholder
        except Exception:
            pass



    def _update_system_summary(self, text: str):
        try:
            widget = self.query_one("#system_summary", Static)
            widget.update(text)
        except Exception:
            pass

    # Textual expects this handler name for Input.Submitted
    def on_input_submitted(self, event: Input.Submitted) -> None:
        user_input = event.value.strip()
        # clear and refocus the input
        try:
            self.input_widget.value = ""
            self.set_focus(self.input_widget)
        except Exception:
            pass

        if not user_input:
            return
        # delegate
        self.handle_input(user_input)

    def handle_input(self, text: str):
        """Common handler for typed and voice text."""
        cmd = text.strip().lower()

        # Mode switching
        if cmd == "/voice":
            self.mode = "voice"
            self.conversation_mode = True
            self.last_interaction_time = time.time()
            self.chat_log.write(Text("Switched to VOICE mode — listening for your voice.", style="bold green"))
            self._update_input_placeholder()
            return
        if cmd == "/chat":
            self.mode = "chat"
            self.conversation_mode = False
            self.chat_log.write(Text("Switched to CHAT mode — type to interact.", style="bold yellow"))
            self._update_input_placeholder()
            return

        # Log user message
        global last_3_lines, messages
        self.chat_log.write(Text(f"You: {text}", style="bold magenta"))
        last_3_lines.append(text)
        last_3_lines[:] = last_3_lines[-3:]
        messages.append({"role": "user", "content": text})

        # Start assistant in a thread (no lock here)
        threading.Thread(
            target=self._background_stream_and_display,
            args=(messages.copy(),),
            daemon=True
        ).start()

    
    
    def _background_stream_and_display(self, messages_for_call):
        """Stream AI responses, handle tool calls safely, and update the UI with RichLog."""
        import json
        try:
            buffer = []
            last_flush = time.time()
            flush_interval = 0.12  # seconds
            final_text = ""
            prefix_written = False
            tool_calls = []
            current_tool_call = None

            # ---------------- STREAMING ----------------
            try:
                # Create the stream properly
                stream = CLIENT.chat.completions.create(
                    messages=messages_for_call,
                    tools=openai_tools,
                    model=OPENAI_MODEL_NAME,
                    stream=True  # Enable streaming mode
                )

                # Iterate over the stream
                for chunk in stream:
                    # Get the delta from the first choice
                    if chunk.choices and chunk.choices[0].delta:
                        delta = chunk.choices[0].delta
                        
                        # Handle regular content
                        if delta.content:
                            token = delta.content
                            buffer.append(token)
                            final_text += token

                            now = time.time()
                            if now - last_flush >= flush_interval:
                                chunk_text = "".join(buffer)
                                buffer.clear()
                                last_flush = now
                                if not prefix_written:
                                    self.call_from_thread(self.chat_log.write, Text(f"Supporter: {chunk_text}"))
                                    prefix_written = True
                                else:
                                    self.call_from_thread(self.chat_log.write, chunk_text)
                        
                        # Handle tool calls
                        if delta.tool_calls:
                            for tool_call_chunk in delta.tool_calls:
                                # Start of a new tool call
                                if tool_call_chunk.id:
                                    current_tool_call = {
                                        "id": tool_call_chunk.id,
                                        "name": "",
                                        "arguments": ""
                                    }
                                    tool_calls.append(current_tool_call)
                                
                                # Accumulate function name
                                if tool_call_chunk.function and tool_call_chunk.function.name:
                                    if current_tool_call:
                                        current_tool_call["name"] = tool_call_chunk.function.name
                                
                                # Accumulate arguments
                                if tool_call_chunk.function and tool_call_chunk.function.arguments:
                                    if current_tool_call:
                                        current_tool_call["arguments"] += tool_call_chunk.function.arguments

                # Execute any tool calls that were accumulated
                if tool_calls:
                    self.call_from_thread(self.chat_log.write, Text("\n[Executing tools...]", style="bold cyan"))
                    
                    for tool_call in tool_calls:
                        try:
                            from core.config import tool_map
                            tool_name = tool_call["name"]
                            tool_args = json.loads(tool_call["arguments"])
                            
                            self.call_from_thread(self.chat_log.write, 
                                Text(f"[Calling {tool_name} with args: {tool_args}]", style="cyan"))
                            
                            result = tool_map[tool_name].run(tool_args)
                            
                            self.call_from_thread(self.chat_log.write, 
                                Text(f"[Tool result]: {result}", style="green"))
                            
                            # Add tool result to messages for potential follow-up
                            messages.append({
                                "role": "assistant",
                                "content": None,
                                "tool_calls": [{
                                    "id": tool_call["id"],
                                    "type": "function",
                                    "function": {
                                        "name": tool_name,
                                        "arguments": tool_call["arguments"]
                                    }
                                }]
                            })
                            messages.append({
                                "role": "tool",
                                "content": str(result),
                                "tool_call_id": tool_call["id"]
                            })
                            
                        except Exception as e:
                            error_msg = f"Error executing tool {tool_call.get('name', 'unknown')}: {e}"
                            self.call_from_thread(self.chat_log.write, Text(error_msg, style="red"))

            except Exception as e:
                # Non-stream fallback (create())
                self.call_from_thread(self.chat_log.write, Text(f"Stream failed, using non-stream: {e}", style="yellow"))
                
                resp = CLIENT.chat.completions.create(
                    messages=messages_for_call,
                    model=OPENAI_MODEL_NAME,
                    tools=openai_tools,
                    stream=False  # Explicitly disable streaming for fallback
                )
                
                message = resp.choices[0].message
                
                # Handle content
                if message.content:
                    final_text = message.content
                    self.call_from_thread(self.chat_log.write, Text(f"Supporter: {final_text}"))
                
                # Handle tool calls
                if message.tool_calls:
                    self.call_from_thread(self.chat_log.write, Text("\n[Executing tools...]", style="bold cyan"))
                    
                    for tool_call in message.tool_calls:
                        try:
                            from core.config import tool_map
                            tool_name = tool_call.function.name
                            tool_args = json.loads(tool_call.function.arguments)
                            
                            self.call_from_thread(self.chat_log.write, 
                                Text(f"[Calling {tool_name} with args: {tool_args}]", style="cyan"))
                            
                            result = tool_map[tool_name].run(tool_args)
                            
                            self.call_from_thread(self.chat_log.write, 
                                Text(f"[Tool result]: {result}", style="green"))
                            
                            # Add to messages
                            messages.append({
                                "role": "assistant",
                                "content": None,
                                "tool_calls": [{
                                    "id": tool_call.id,
                                    "type": "function",
                                    "function": {
                                        "name": tool_name,
                                        "arguments": tool_call.function.arguments
                                    }
                                }]
                            })
                            messages.append({
                                "role": "tool",
                                "content": str(result),
                                "tool_call_id": tool_call.id
                            })
                            
                        except Exception as e:
                            error_msg = f"Error executing tool: {e}"
                            self.call_from_thread(self.chat_log.write, Text(error_msg, style="red"))

            # Flush remaining buffer if any
            if buffer:
                chunk_text = "".join(buffer)
                if not prefix_written:
                    self.call_from_thread(self.chat_log.write, Text(f"Supporter: {chunk_text}"))
                else:
                    self.call_from_thread(self.chat_log.write, chunk_text)

            # Add assistant message to history if there was text content
            if final_text:
                def _append_messages():
                    messages.append({"role": "assistant", "content": final_text})
                    last_3_lines.append(final_text)
                    last_3_lines[:] = last_3_lines[-3:]
                
                self.call_from_thread(_append_messages)

                # TTS announcement
                import core.audio_feedback as af
                threading.Thread(target=af.initiate_tts, args=(final_text,), daemon=True).start()

        except Exception as e:
            self.call_from_thread(self.chat_log.write, Text(f"Error in response: {e}", style="red"))
        finally:
            try:
                self._response_lock.release()
            except Exception:
                pass

    def voice_loop(self):
        """Continuously listens to mic input for wake word / prompts."""
    
        try:
            with mic as source:
                recognizer.adjust_for_ambient_noise(source)
                while not self._stop_threads:
                    try:
                        audio = recognizer.listen(source, timeout=10)
                        try:
                            transcript = recognizer.recognize_google(audio)
                        except sr.UnknownValueError:
                            continue
                        except Exception as e:
                            self.call_from_thread(self.chat_log.write, f"Speech recognition error: {e}")
                            continue

                        current_time = time.time()
                        if TRIGGER_WORD.lower() in transcript.lower():
                            self.conversation_mode = True
                            self.last_interaction_time = time.time()
                            threading.Thread(target=self.handle_input, args=("Hey! How can i help you today?",), daemon=True).start()
                            continue
                        
                        if self.mode == "voice" and self.conversation_mode:    
                            if current_time - (self.last_interaction_time or 0) > CONVERSATION_TIMEOUT:
                                self.conversation_mode = False
                                continue
                            self.last_interaction_time = current_time
                            threading.Thread(target=self.handle_input, args=(transcript,), daemon=True).start()


                        elif self.mode == "chat":
                            continue
                    except sr.WaitTimeoutError:
                        continue
                    except sr.UnknownValueError:
                        continue
                    except Exception as e:
                        self.call_from_thread(self.chat_log.write, f"Voice loop error: {e}")
        except Exception as e:
            self.call_from_thread(self.chat_log.write, f"Voice setup error: {e}")
