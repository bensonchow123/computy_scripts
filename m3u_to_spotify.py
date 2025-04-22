from os import getenv, path
from time import sleep
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from mutagen.flac import FLAC

load_dotenv()

SPOTIFY_CLIENT_ID = getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = getenv("SPOTIFY_CLIENT_SECRET")
M3U_FOLDER_PATH = getenv("LINUX_PLAYLISTS_FOLDER_PATH")
SPOTIFY_AUTH_CACHE_PATH = getenv("SPOTIFY_AUTH_CACHE_PATH")
SPOTIPY_REDIRECT_URI = 'http://127.0.0.1:8888/callback'
SCOPE = "playlist-modify-public playlist-read-private"

sp = Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope=SCOPE,
    open_browser=True,
    cache_path=SPOTIFY_AUTH_CACHE_PATH
))

def format_playlist_name(filename):
    return f"Synced {filename.stem.replace('_', ' ').title()}"

def get_metadata(file_path):
    try:
        audio = FLAC(file_path)
        artist = audio.get("artist", [""])[0]
        title = audio.get("title", [""])[0]
        album = audio.get("album", [""])[0]
        if artist and title and album:
            return f"{artist} - {title} (Album: {album})"
        elif artist and title:
            return f"{artist} - {title}"
    except Exception as e:
        print(f"Metadata error for {file_path}: {e}")
    return None

def read_m3u(file_path):
    songs = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                full_path = path.join(M3U_FOLDER_PATH, line)
                metadata = get_metadata(full_path)
                if metadata:
                    songs.append(metadata)
    return songs

def search_spotify_tracks(songs):
    track_uris = []
    for song in songs:
        parts = song.split(" - ")
        if len(parts) < 2:
            print(f"Skipping invalid format: {song}")
            continue

        artist = parts[0].strip()
        title_album = parts[1].split(" (Album: ")
        title = title_album[0].strip()
        album = title_album[1].rstrip(")") if len(title_album) > 1 else ""

        query = f'track:"{title}" artist:"{artist}" album:"{album}"'
        results = sp.search(q=query, limit=5, type="track")["tracks"]["items"]

        if not results:
            results = sp.search(q=song, limit=1, type="track")["tracks"]["items"]

        if results:
            track_uris.append(results[0]["uri"])
        else:
            print(f"No match found for: {song}")
    return track_uris

def get_playlist_by_name(name):
    playlists = sp.current_user_playlists()
    for playlist in playlists["items"]:
        if playlist["name"].lower() == name.lower():
            return playlist
    return None

def get_existing_tracks(playlist_id):
    uris = []
    results = sp.playlist_items(playlist_id, fields="items(track.uri),next", limit=100)
    while results:
        uris.extend([item["track"]["uri"] for item in results["items"]])
        results = sp.next(results) if results.get("next") else None
    return uris

def remove_all_tracks(playlist_id, uris):
    for i in range(0, len(uris), 100):
        sp.playlist_remove_all_occurrences_of_items(playlist_id, uris[i:i+100])
        sleep(0.5)

def update_playlist(name, track_uris):
    playlist = get_playlist_by_name(name)
    sync_time = datetime.now().strftime("%-d/%-m/%y, %H:%M")
    playlist_description = (
        f"Synced from my Jellyfin server at {sync_time}, tracks can be wrong. "
        "Using my custom M3U → Spotify sync tool, see at: github.com/bensonchow123/computy_scripts. "
        "Ordered in order of my favourites."
    )

    if playlist:
        existing_uris = get_existing_tracks(playlist["id"])
        if existing_uris == track_uris:
            print(f"✅ No update needed: {name}")
        else:
            print(f"🔁 Updating: {name}")
            remove_all_tracks(playlist["id"], existing_uris)
            for i in range(0, len(track_uris), 100):
                sp.playlist_add_items(playlist["id"], track_uris[i:i+100])

        sp.playlist_change_details(playlist["id"], description=playlist_description)
    else:
        print(f"➕ Creating new playlist: {name}")
        new_playlist = sp.user_playlist_create(sp.current_user()["id"], name, description=playlist_description)
        for i in range(0, len(track_uris), 100):
            sp.playlist_add_items(new_playlist["id"], track_uris[i:i+100])

def main():
    m3u_folder = Path(M3U_FOLDER_PATH)
    m3u_files = list(m3u_folder.glob("*.m3u"))

    for m3u_file in m3u_files:
        print(f"\n🎵 Processing: {m3u_file.name}")
        playlist_name = format_playlist_name(m3u_file)
        songs = read_m3u(m3u_file)
        if not songs:
            print("⚠️ No valid metadata in playlist's files, skipping.")
            continue
        track_uris = search_spotify_tracks(songs)
        update_playlist(playlist_name, track_uris)

if __name__ == "__main__":
    main()
