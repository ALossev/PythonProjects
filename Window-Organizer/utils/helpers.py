import os

def format_size(bytes_size):
    """Convert bytes to a human-readable format (KB, MB, GB)."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024

def get_file_size(path):
    """Return size of a file in human-readable format."""
    if not os.path.isfile(path):
        return "0 B"
    return format_size(os.path.getsize(path))

def safe_move(src, dest):
    """
    Move a file safely, handling duplicates.
    If a file with the same name exists, rename it.
    """
    base, ext = os.path.splitext(dest)
    counter = 1
    while os.path.exists(dest):
        dest = f"{base} ({counter}){ext}"
        counter += 1
    return dest
