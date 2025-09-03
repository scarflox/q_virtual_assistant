"""
Tools and helper functions for OpenAI integration.
"""
import json
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from langchain.tools import tool
from comtypes import CLSCTX_ALL

# --------------------- Volume Tool ---------------------
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
    
# --------------------- JSON CONVERTER FOR OPENAI FUNC ---------------------

def tool_to_openai(tool):
    """Convert a Python tool object to OpenAI-compatible function schema."""
    # Get the schema from the tool
    if hasattr(tool, 'args_schema') and tool.args_schema:
        schema = tool.args_schema.schema()
    else:
        # Fallback: try to parse from the docstring or use empty schema
        schema = {
            "type": "object",
            "properties": {},
            "required": []
        }
    
    # Extract just the properties and required fields
    parameters = {
        "type": "object",
        "properties": schema.get("properties", {}),
        "required": schema.get("required", [])
    }
    
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description or tool.__doc__ or "No description available",
            "parameters": parameters
        }
    }