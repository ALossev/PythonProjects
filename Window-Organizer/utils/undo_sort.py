import os
import shutil
from datetime import datetime

LOG_FILE = os.path.join(os.path.dirname(__file__), "..", "logs", "actions.log")

def undo_last_actions():
    """Undo all 'MOVED' actions by moving files back to their original places."""
    if not os.path.exists(LOG_FILE):
        print(" No log file found. Nothing to undo.")
        return

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    moves = [line for line in lines if "MOVED" in line]
    if not moves:
        print(" No move actions found to undo.")
        return

    print("🔄 Undoing previous actions...")

    for line in reversed(moves):  # Reverse order (undo last first)
        try:
            parts = line.split("|")
            src = parts[1].split("from=")[1].strip()
            dest = parts[2].split("to=")[1].strip()
            if os.path.exists(dest):
                shutil.move(dest, src)
                print(f" Restored: {os.path.basename(dest)} → {os.path.dirname(src)}")
            else:
                print(f" File not found: {dest}")
        except Exception as e:
            print(f" Failed to undo: {line.strip()} | {e}")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} | UNDO completed\n")

    print("\n Undo complete")
