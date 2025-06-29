import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
LINUX_PLAYLISTS_FOLDER_PATH = os.getenv("LINUX_PLAYLISTS_FOLDER_PATH")

# Configurable mount point variables
OLD_MOUNT_POINT = "/media/benson/"
NEW_MOUNT_POINT = "/mnt/"

def convert_mount_point_line(line):
    """Convert only the mount point from OLD_MOUNT_POINT to NEW_MOUNT_POINT"""
    if line.strip() and not line.startswith('#'):
        return line.replace(OLD_MOUNT_POINT, NEW_MOUNT_POINT)
    return line

def convert_mount_points_in_m3u_files():
    """Convert mount points in M3U files"""
    if not LINUX_PLAYLISTS_FOLDER_PATH:
        print("LINUX_PLAYLISTS_FOLDER_PATH environment variable not set")
        return
        
    if not os.path.isdir(LINUX_PLAYLISTS_FOLDER_PATH):
        print(f"Playlists folder not found: {LINUX_PLAYLISTS_FOLDER_PATH}")
        return

    converted_count = 0
    
    for filename in os.listdir(LINUX_PLAYLISTS_FOLDER_PATH):
        if filename.lower().endswith('.m3u'):
            input_path = os.path.join(LINUX_PLAYLISTS_FOLDER_PATH, filename)
            
            # Read the file first to check if conversion is needed
            with open(input_path, 'r', encoding='utf-8') as infile:
                lines = infile.readlines()
            
            # Check if any lines need conversion
            needs_conversion = any(OLD_MOUNT_POINT in line for line in lines)
            
            if needs_conversion:
                # Create backup
                backup_path = input_path + '.backup'
                if not os.path.exists(backup_path):
                    os.rename(input_path, backup_path)
                    
                    # Convert the file
                    with open(backup_path, 'r', encoding='utf-8') as infile, \
                         open(input_path, 'w', encoding='utf-8') as outfile:
                        for line in infile:
                            outfile.write(convert_mount_point_line(line))
                    
                    print(f"✓ Converted {filename} (backup saved as {filename}.backup)")
                    converted_count += 1
                else:
                    print(f"⚠ Skipped {filename} (backup already exists)")
            else:
                print(f"- No conversion needed for {filename}")
    
    print(f"\nConversion complete! Processed {converted_count} files.")
    print(f"Mount point changed from '{OLD_MOUNT_POINT}' to '{NEW_MOUNT_POINT}'")

def show_config():
    """Display current configuration"""
    print("Current Configuration:")
    print(f"  Playlists folder: {LINUX_PLAYLISTS_FOLDER_PATH}")
    print(f"  Old mount point:  {OLD_MOUNT_POINT}")
    print(f"  New mount point:  {NEW_MOUNT_POINT}")
    print()

if __name__ == "__main__":
    import sys
    
    print("M3U Mount Point Converter")
    print("=" * 30)
    
    show_config()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--help" or sys.argv[1] == "-h":
            print("Usage:")
            print("  python change_mount_point.py           # Convert mount points")
            print("  python change_mount_point.py --help    # Show this help")
            print("  python change_mount_point.py --config  # Show configuration only")
        elif sys.argv[1] == "--config":
            pass  # Config already shown above
        else:
            print(f"Unknown option: {sys.argv[1]}")
            print("Use --help for usage information")
    else:
        convert_mount_points_in_m3u_files()
