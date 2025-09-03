
"""
    Spotify-specific tools.
"""

from langchain.tools import tool
import re
from dotenv import load_dotenv

from rapidfuzz import fuzz
from core.utils import wait_for_spotify_boot, start_spotify_exe, find_spotify_process
import spotipy
import core.audio_feedback as af
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials

load_dotenv()

_spotify_clients = None

def initiate_spotify_clients():
    global _spotify_clients
    if _spotify_clients is not None:
        return _spotify_clients
     
    from core.config import  SCOPE, REDIRECT_URI, SPOTIFY_CLIENT_SECRET, SPOTIFY_CLIENT_ID, SPOTIFY_CACHE_FILE
    # Spotify clients
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
        cache_path=SPOTIFY_CACHE_FILE
    ))

    sp_client = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET
    ))

    _spotify_clients = (sp, sp_client)
    return _spotify_clients
    
@tool
def play_user_playlist(playlist_name):
    """
    
    This function will be activated when the user wants to play one of his playlists.
    We will be getting the current user playlists in a list, each item in the list is a tuple (playlist_name, playlist_id)
    we will identify the right playlist by it's name and then use the id to play it.
    Example:
    User input - "Play my playlist `Don't Drake and Drive`"
    AI - play_user_playlist("Don't Drake and Drive")
    returns a confirm message after it plays the playlist. 

    """
    if not playlist_name:
        raise ValueError("playlist_name was not provided to play_user_playlist")
    sp, sp_client = initiate_spotify_clients()
    user_playlists = []
    for playlist in sp.current_user_playlists()["items"]:
        user_playlists.append((playlist["name"].lower(), playlist["id"]))
    
    playlist_name_lower = playlist_name.lower()
    best_match, best_score = None, 0
    final_playlist_name = ""
    for (name, id) in user_playlists:
        playlist_score = fuzz.token_set_ratio(playlist_name_lower, name.lower())

        if playlist_score > best_score:
            best_score = playlist_score
            best_match = id
            final_playlist_name = name

    if not best_match:
        return "No playlist was found."
    
    uri = "spotify:playlist:" + best_match
    
    try:
        sp.start_playback(context_uri=uri)
        return f"Playlist found! Name of playlist: {final_playlist_name}"
    except spotipy.exceptions.SpotifyException as e:
        return f"Error playing playlist: {e}"


# ------------------- Search Helpers -------------------
def regular_query(query: str, max_tracks: int = 100, artist_name: str | None = None, artist_threshold: int = 40, query_name: str = "Regular Query"):
    """Search Spotify tracks with fuzzy scoring."""
    sp, sp_client = initiate_spotify_clients()
    tracks = []
    offset = 0
    limit = 50

    while len(tracks) < max_tracks:
        result = sp.search(q=query, type="track", limit=limit, offset=offset)
        items = result.get("tracks", {}).get("items", [])
        if not items:
            break
        tracks.extend(items)
        if len(items) < limit:
            break
        offset += limit

    if not tracks:
        return None, None, None, None, 0

    # Fuzzy matching
    best_match, best_score = None, 0
    query_lower = query.lower()
    for track in tracks:
        title_score = fuzz.token_set_ratio(query_lower, track["name"].lower())
        artist_score = 0
        if artist_name:
            artist_scores = [fuzz.token_set_ratio(artist_name.lower(), a["name"].lower()) for a in track["artists"]]
            artist_score = max(artist_scores)
            if artist_score < artist_threshold:
                continue
        combined_score = 0.7 * title_score + 0.3 * artist_score
        if combined_score > best_score:
            best_match = track
            best_score = combined_score

    if not best_match:
        return None, None, None, None, 0

    track_name = best_match["name"]
    artist_name_final = ", ".join([a["name"] for a in best_match["artists"]])
    uri = best_match["uri"]

    print(f"{query_name} Matched: {track_name} - {artist_name_final} | Score: {best_score}")
    print("Spotify URL:", best_match["external_urls"]["spotify"])
    return best_match, track_name, artist_name_final, uri, best_score


def simplify_title(title: str) -> str:
    """Remove '(feat. ...)' or '(with ...)' from titles."""
    return re.sub(r'\(feat[^\)]*\)|\(with[^\)]*\)', '', title, flags=re.IGNORECASE).strip()


def new_query(query: str, max_tracks: int = 100, artist_threshold: int = 40):
    """Artist-aware fuzzy search."""
    query_lower = query.lower()
    if " by " in query_lower:
        track_name, artist_name = map(str.strip, query_lower.split(" by ", 1))
    else:
        track_name, artist_name = query_lower, None
    return regular_query(track_name, max_tracks=max_tracks, artist_name=artist_name, artist_threshold=artist_threshold, query_name="New Query")


def query_best_song(query: str, max_tracks: int = 100, confidence_threshold: int = 94):
    """Return the best matching track based on fuzzy scoring."""
    new_track, new_name, new_artist, new_uri, new_score = new_query(query, max_tracks)
    if new_score >= confidence_threshold:
        print(f"Chosen Track (artist-aware): {new_name} - {new_artist} | Score: {new_score}")
        return new_track, new_name, new_artist, new_uri, new_score

    reg_track, reg_name, reg_artist, reg_uri, reg_score = regular_query(query, max_tracks)
    if reg_score >= confidence_threshold:
        print(f"Chosen Track (regular fallback): {reg_name} - {reg_artist} | Score: {reg_score}")
        return reg_track, reg_name, reg_artist, reg_uri, reg_score

    chosen = (new_track, new_name, new_artist, new_uri, new_score) if new_score >= reg_score else (reg_track, reg_name, reg_artist, reg_uri, reg_score)
    print(f"Choosing best available: {chosen[1]} - {chosen[2]} | Score: {chosen[4]}")
    return chosen


# ------------------- Playback Helpers -------------------
def get_track_info(track_id: str) -> dict | None:
    sp, sp_client = initiate_spotify_clients()
    try:
        return sp_client.track(track_id)
    except Exception as e:
        print(f"Error fetching track info: {e}")
        return None


def get_artist_info(artist_id: str) -> dict | None:
    sp, sp_client = initiate_spotify_clients()
    try:
        return sp_client.artist_related_artists(artist_id)
    except Exception as e:
        print(f"Error fetching artist info: {e}")
        return None

def play_track(uri: str, artist_uri: str | None = None):
    """Play a track and queue recommendations based on related artists."""
    sp, sp_client = initiate_spotify_clients()
    devices = sp.devices().get("devices", [])
    if not devices:
         return "No active Spotify device found. Please open Spotify on a device."
    device_id = devices[0]["id"]
    
    sp.start_playback(device_id=device_id, uris=[uri]) # User must have spotify premium, and be active.
    print(f"Now playing: {uri}")

    if artist_uri:
        queue_recommendations(uri, artist_uri=artist_uri, max_results=20)


def queue_recommendations(track_uri, artist_uri = None, max_results = 30):
    """Queue recommended tracks using related artists and their top tracks."""
    sp, sp_client = initiate_spotify_clients()
    track_id = track_uri.split(":")[-1] if ":" in track_uri else track_uri.split("/")[-1]

    track_info = get_track_info(track_id)
    if not track_info:
        print(f"Cannot fetch track info for {track_id}")
        return []

    related_artist_ids = [a["id"] for artist in track_info["artists"] if (artist_info := get_artist_info(artist["id"])) for a in artist_info["artists"]]

    if artist_uri:
        artist_id = artist_uri.split(":")[-1] if ":" in artist_uri else artist_uri.split("/")[-1]
        if artist_id not in related_artist_ids:
            related_artist_ids.append(artist_id)

    if not related_artist_ids:
        print("No related artists found for recommendations.")
        return []

    recommended_tracks = []
    for artist_id in related_artist_ids:
        try:
            recommended_tracks.extend(sp_client.artist_top_tracks(artist_id).get("tracks", []))
        except Exception as e:
            print(f"Error fetching top tracks for artist {artist_id}: {e}")

    if not recommended_tracks:
        print("No recommended tracks found.")
        return []

    recommended_tracks = recommended_tracks[:max_results]

    devices = sp.devices().get("devices", [])
    if not devices:
        print("No active Spotify devices detected [NEED TTS]")
        return []

    device_id = devices[0]["id"]
    for t in recommended_tracks:
        try:
            sp.add_to_queue(t["uri"], device_id=device_id)
        except Exception as e:
            pass

    print(f"Queued {len(recommended_tracks)} recommended tracks based on {track_info['name']}")
    return recommended_tracks

@tool
def stop_current_playback():
    """Pauses the current spotify playback."""
    sp, sp_client = initiate_spotify_clients()
    try:
        sp.pause_playback()
        return "Playback paused successfully."
    except spotipy.exceptions.SpotifyException as e:
        return f"Error pausing playback: {e}"


@tool
def play_next_track():
    """Skips to the next song in spotify."""
    sp, sp_client = initiate_spotify_clients()
    try:
        sp.next_track()
        return "Next track played."
    except spotipy.exceptions.SpotifyException as e:
        return f"Error skipping song: {e}"


@tool
def query_and_play_track(query):
    
    """
    Search for a song on Spotify and play the best matching track.

    This function takes a song name as input, optionally including the artist
    (e.g., "Blinding Lights by The Weeknd"). It performs a fuzzy search on 
    Spotify to find the track that best matches the query. If a match is found, 
    the track is played on an active Spotify device, and the currently playing 
    track is announced using TTS (text-to-speech).

    Parameters:
        query (str): The song title, optionally followed by 'by <artist>' to 
                     improve search accuracy.

    Returns:
        str: A message indicating which track is now playing, or a message 
             stating that no valid track was found.
    """
    sp, sp_client = initiate_spotify_clients()
    if not find_spotify_process():
        start_spotify_exe()
        if not wait_for_spotify_boot():
            raise Exception("Spotify failed to execute.")
        
    chosen, chosen_name, chosen_artist, chosen_uri, chosen_score = query_best_song(query)
    if not chosen_uri:
        return f"No valid track found for '{query}'."
    
    
    play_track(chosen_uri, chosen["artists"][0]["uri"] if chosen else None)
    return f"Now playing: {chosen_name} by {chosen_artist}, Enjoy!"