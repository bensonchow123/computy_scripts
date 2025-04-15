import os
from os import getenv
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

LINUX_PLAYLISTS_FOLDER_PATH = getenv("LINUX_PLAYLISTS_FOLDER_PATH")
SPLITTED_PLAYLIST_FOLDER_PATH = getenv("SPLITTED_PLAYLIST_FOLDER_PATH")

def is_valid_path_line(line: str) -> bool:
    # Ignore M3U commands (like #EXTM3U, #EXTINF)
    return line.strip() and not line.strip().startswith("#")

def split_m3u_file(filepath: Path, output_dir: Path, base_name: str, chunk_size: int = 100):
    with filepath.open("r", encoding="utf-8", errors="ignore") as f:
        lines = [line.strip() for line in f if is_valid_path_line(line)]

    os.makedirs(output_dir, exist_ok=True)

    for i in range(0, len(lines), chunk_size):
        chunk = lines[i:i + chunk_size]
        chunk_number = i // chunk_size + 1
        output_file = output_dir / f"{base_name}_{chunk_number}.m3u"

        with output_file.open("w", encoding="utf-8") as out:
            out.write("#EXTM3U\n")
            out.write("\n".join(chunk))

def main():
    linux_playlists = Path(LINUX_PLAYLISTS_FOLDER_PATH)
    splitted_playlists = Path(SPLITTED_PLAYLIST_FOLDER_PATH)

    for m3u_file in linux_playlists.glob("*.m3u"):
        base_name = m3u_file.stem
        output_dir = splitted_playlists / base_name
        split_m3u_file(m3u_file, output_dir, base_name)

if __name__ == "__main__":
    main()