import os
from os import getenv
from datetime import datetime
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

    total_chunks = (len(lines) + chunk_size - 1) // chunk_size
    written_files = set()
    any_changes = False

    for i in range(0, len(lines), chunk_size):
        chunk = lines[i:i + chunk_size]
        chunk_number = i // chunk_size + 1
        output_file = output_dir / f"{base_name}_{chunk_number}.m3u"
        written_files.add(output_file)

        new_content = "#EXTM3U\n" + "\n".join(chunk)

        if output_file.exists():
            with output_file.open("r", encoding="utf-8") as existing_file:
                existing_content = existing_file.read()
            if existing_content == new_content:
                continue

        with output_file.open("w", encoding="utf-8") as out:
            out.write(new_content)
        print(f"[WRITTEN] {output_file.name}")
        any_changes = True

    # Cleanup: Remove leftover old chunk files
    for existing_file in output_dir.glob(f"{base_name}_*.m3u"):
        if existing_file not in written_files:
            existing_file.unlink()
            print(f"[REMOVED] {existing_file.name}")
            any_changes = True
    
    if not any_changes:
        print(f"[UNCHANGED] {base_name} - no updates needed")
    
def main():
    linux_playlists = Path(LINUX_PLAYLISTS_FOLDER_PATH)
    splitted_playlists = Path(SPLITTED_PLAYLIST_FOLDER_PATH)

    for m3u_file in linux_playlists.glob("*.m3u"):
        base_name = m3u_file.stem
        output_dir = splitted_playlists / base_name
        split_m3u_file(m3u_file, output_dir, base_name)
    print(f"Splitted playlist updated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()