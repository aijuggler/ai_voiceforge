import os

def sanitize_title(title):
    """Sanitize title for safe file naming."""
    return title.replace(" ", "_").replace(":", "").replace("/", "-")

def save_text_to_file(text, file_path):
    """Save text to a file, creating directories if needed."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)

def create_folder_if_not_exists(folder_path):
    """Create folder if it doesn't exist."""
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"✅ Folder created: {folder_path}")
    else:
        print(f"📁 Folder already exists: {folder_path}")
    return folder_path

