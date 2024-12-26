import os
from config import Config
from werkzeug.utils import secure_filename

def save_uploaded_file(uploaded_file):
    file_path = os.path.join(Config.UPLOAD_DIR, secure_filename(uploaded_file.name))
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

def list_files():
    directory_path = Config.UPLOAD_DIR
    # List all files and directories
    all_items = os.listdir(directory_path)

    # Filter only files
    files = [os.path.join(directory_path, f) for f in all_items if os.path.isfile(os.path.join(directory_path, f))]
    return files

def delete_files(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
        return f"Successfully removed {file_path}"

