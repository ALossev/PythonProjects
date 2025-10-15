import os
import shutil
from datetime import datetime
from utils.helpers import get_file_size, safe_move

LOG_FILE = os.path.join(os.path.dirname(__file__), "..", "logs", "actions.log")

def ensure_folder(folder_path):
    """Create folder if it doesn't exist."""
    os.makedirs(folder_path, exist_ok=True)

def log_action(action):
    """Write log entries with timestamps."""
    ensure_folder(os.path.dirname(LOG_FILE))
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now()} | {action}\n")

def get_category(filename, categories):
    """Determine which category a file belongs to based on extension."""
    ext = os.path.splitext(filename)[1].lower()
    for category, extensions in categories.items():
        if ext in extensions:
            return category
    return "Others"

def organize_files(base_path, categories):
    """Move files into categorized subfolders."""
    for filename in os.listdir(base_path):
        file_path = os.path.join(base_path, filename)

        # Skip directories and hidden/system files
        if os.path.isdir(file_path) or filename.startswith("."):
            continue

        category = get_category(filename, categories)
        target_folder = os.path.join(base_path, category)
        ensure_folder(target_folder)

        target_path = os.path.join(target_folder, filename)
        target_path = safe_move(file_path, target_path)

        try:
            shutil.move(file_path, target_path)
            file_size = get_file_size(target_path)
            log_action(f"MOVED | from={file_path} | to={target_path} | size={file_size}")
            print(f" {filename} ({file_size}) → {category}")
        except Exception as e:
            log_action(f"ERROR | {filename} | {e}")
            print(f" Failed to move {filename}: {e}")
