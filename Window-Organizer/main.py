import os
from utils.file_sorter import organize_files
from utils.undo_sort import undo_last_actions
from config import CATEGORIES

def get_target_path():
    # Your specific Desktop folder
    return r"C:\Users\omega\OneDrive\Desktop" # Define Users Desktop file

def main():
    desktop_path = get_target_path()
    print(" Desktop Organizer Bot")
    print("==========================")
    print(f"Target folder: {desktop_path}")
    print("1  Organize this folder")
    print("2️  Undo last organization")
    print("==========================")

    choice = input("Choose an option (1 or 2): ").strip()

    if choice == "1":
        print(f"\n Scanning: {desktop_path}")
        organize_files(desktop_path, CATEGORIES)
        print("\n Desktop organized successfully!")
    elif choice == "2":
        undo_last_actions()
    else:
        print(" Invalid choice. Exiting.")

if __name__ == "__main__":
    main()
