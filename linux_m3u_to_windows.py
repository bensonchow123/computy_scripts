import os

from dotenv import load_dotenv

load_dotenv()

LINUX_PLAYLISTS_FOLDER_PATH = os.getenv("LINUX_PLAYLISTS_FOLDER_PATH")
WINDOWS_PLAYLISTS_FOLDER_PATH = os.getenv("WINDOWS_PLAYLISTS_FOLDER_PATH")

def convert_line(line):
    if line.strip() and not line.startswith('#'):
        line = line.replace('/media/benson/SSD_960GB/music/library/', r'Z:\music\library\\')
        return line.replace('/', '\\')
    return line

def convert_all_m3u_files():
    if not os.path.isdir(LINUX_PLAYLISTS_FOLDER_PATH):
        print(f"Linux playlists folder not found: {LINUX_PLAYLISTS_FOLDER_PATH}")
        return
    if not os.path.isdir(WINDOWS_PLAYLISTS_FOLDER_PATH):
        os.makedirs(WINDOWS_PLAYLISTS_FOLDER_PATH, exist_ok=True)

    for filename in os.listdir(LINUX_PLAYLISTS_FOLDER_PATH):
        if filename.lower().endswith('.m3u'):
            input_path = os.path.join(LINUX_PLAYLISTS_FOLDER_PATH, filename)
            output_path = os.path.join(WINDOWS_PLAYLISTS_FOLDER_PATH, filename)
            with open(input_path, 'r', encoding='utf-8') as infile, \
                 open(output_path, 'w', encoding='utf-8') as outfile:
                for line in infile:
                    outfile.write(convert_line(line))

if __name__ == "__main__":
    convert_all_m3u_files()