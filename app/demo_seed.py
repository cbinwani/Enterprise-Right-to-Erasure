import os
from .file_store import ensure_data, read_json, write_json
from .config import settings

def seed():
    ensure_data()
    path=os.path.join(settings.data_dir,"requests.json")
    if not os.path.exists(path):
        write_json("requests.json",{"version":"1.0","records":[]})
