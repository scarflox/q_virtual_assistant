# import os
# import logging
# import time
# import json
# from openai import OpenAI
# from dotenv import load_dotenv
# from core.utils import tool_to_openai
# import core.audio_feedback as af
# import speech_recognition as sr
# from langchain_ollama import ChatOllama, OllamaLLM
# # from langchain_openai import ChatOpenAI # if you want to use openai
# from langchain_core.messages import HumanMessage
# from langchain.agents import AgentExecutor, create_tool_calling_agent
# from langchain_core.prompts import ChatPromptTemplate
# # importing tools
# from tools.spotify_player import query_and_play_track, stop_current_playback
# # from tools.time_tool import get_time
# # from tools.OCR import read_text_from_latest_image
# # from tools.arp_scan import arp_scan_terminal
# # from tools.duckduckgo import duckduckgo_search_tool
# # from tools.matrix import matrix_mode
# # from tools.screenshot import take_screenshot

# load_dotenv()

# token = os.environ["GITHUB_TOKEN"]
# endpoint = "https://models.github.ai/inference"
# model_name = "openai/gpt-4o"

# MIC_INDEX = None
# TRIGGER_WORD = "Supporter"
# CONVERSATION_TIMEOUT = 30  # seconds of inactivity before exiting conversation mode

# logging.basicConfig(level=logging.DEBUG)  # logging

# recognizer = sr.Recognizer()
# mic = sr.Microphone(device_index=MIC_INDEX)



# # Define a function tool that the model can ask to invoke in order to retrieve flight information

# tools = [
#         query_and_play_track,
#         stop_current_playback]

# openai_tools = [tool_to_openai(t) for t in tools]

# tool_map = {t.name: t for t in tools}


# client = OpenAI(
#     base_url=endpoint,
#     api_key=token,
# )

# messages=[
#     {"role": "system", "content": """You are 'Supporter', a smart and friendly AI assistant.
#             You can chat casually, answer questions, give advice, perform web searches, and assist with tasks.
#             Only use specialized tools when explicitly needed.

#             For music requests:
#             - If the user explicitly asks to play a song, artist, or playlist, you may use the `query_and_play_track` tool.
#             - If the user says "play [song/artist]" or something similar, treat everything after "play" as the song name and use the tool.
#             - If the user requests to stop the music or playback, you may use the `stop_current_playback` tool.
#             - Otherwise, do not assume the user wants music; respond naturally.

#             For all other requests:
#             - Respond directly and helpfully.
#             - Use your knowledge or other available tools if relevant.
#             - Reason step by step if needed, but keep your final answer concise unless the user asks for full details.

#             Examples:
#             - User: "Look up Avast"
#             Response: "Avast is a cybersecurity software company that provides antivirus and internet security solutions."
#             - User: "Play Blinding Lights by The Weeknd"
#             Response: (Use `query_and_play_track` tool)
#             - User: "Tell me a joke"
#             Response: "Why did the computer go to therapy? It had too many bugs!"

# Always be friendly and helpful. Only invoke Spotify when the user clearly requests it.
# """},
    
# ]

# # Main interaction loop
# def write():
    
#     conversation_mode = False
#     last_interaction_time = None
    

#     try:
#         with mic as source:
#             recognizer.adjust_for_ambient_noise(source)
#             while True:
                
#                 try:
#                     current_time = time.time()
#                     if conversation_mode and last_interaction_time is not None:
#                         if current_time - last_interaction_time > CONVERSATION_TIMEOUT:
#                             logging.debug("Timeout reached, returning to wake word mode")
#                             conversation_mode = False

#                     if not conversation_mode:
#                         logging.info("🎤 Listening for wake word...")
#                         audio = recognizer.listen(source, timeout=10)
#                         transcript = recognizer.recognize_google(audio)
#                         logging.info(f"🗣 Heard: {transcript}")

#                         if TRIGGER_WORD.lower() in transcript.lower():
#                             logging.info(f"🗣 Triggered by: {transcript}")
#                             af.initiate_tts(text="Hey! How can i help you?")
#                             conversation_mode = True
#                             last_interaction_time = time.time()
#                         else:
#                             logging.debug("Wake word not detected, continuing...")
#                     else:
#                         logging.info("🎤 Listening for next command...")
#                         audio = recognizer.listen(source, timeout=10)
#                         command = recognizer.recognize_google(audio)
#                         last_interaction_time = time.time()
#                         logging.info(f"📥 Command: {command}")
#                         logging.info("🤖 Sending command to agent...")
#                         messages.append({
#                             "role": "user",
#                             "content": command,
#                         })
#                         response = client.chat.completions.create(
#                             messages=messages,
#                             tools=openai_tools,
#                             model=model_name,
#                         )
#                         if response.choices[0].finish_reason == "tool_calls":
#                             for tool_call in response.choices[0].message.tool_calls:
#                                 if tool_call.type == "function":
#                                     func_name = tool_call.function.name
#                                     func_args = json.loads(tool_call.function.arguments)
#                                     if func_name in tool_map:
#                                         callable_tool = tool_map[func_name]
#                                         print(f"Calling tool `{func_name}` with args {func_args}")
#                                         function_return = callable_tool.run(func_args)
#                                         print(f"Tool returned = {function_return}")
#                                         messages.append({
#                                         "tool_call_id": tool_call.id,
#                                         "role": "system",
#                                         "name": func_name,
#                                         "content": function_return
#                                     })
#                                     else:
#                                         logging.warning(F"Tool `{func_name}` was not found in tool_map.")
                                    
#                         tts_text = function_return if function_return else response.choices[0].message.content
#                         af.initiate_tts(text=tts_text)
#                         print(tts_text)
                        
#                 except sr.WaitTimeoutError:
#                     logging.warning("⚠️ Timeout waiting for audio.")
#                     if (
#                         conversation_mode
#                         and time.time() - last_interaction_time > CONVERSATION_TIMEOUT
#                     ):
#                         logging.info(
#                             "⌛ No input in conversation mode. Returning to wake word mode."
#                         )
#                         conversation_mode = False
#                 except sr.UnknownValueError:
#                     logging.warning("⚠️ Could not understand audio.")
#                 except Exception as e:
#                     logging.error(f"❌ Error during recognition or tool call: {e}")
#                     time.sleep(1)

#     except Exception as e:
#         logging.critical(f"❌ Critical error in main loop: {e}")


# if __name__ == "__main__":
#     write()