from src.utils.client_S3 import S3Client
import os
from pathlib import Path
from dotenv import load_dotenv
from collections import Counter

load_dotenv()

def get_files(path) :

    files = [
        file for file in path.rglob("*")
        if file.is_file()
    ]

    return files



def upload_files(storage, list_files) :
    for file in list_files :
        ext = file.suffix.lower()
        prefix = ext.lstrip(".")
        storage.upload_file(file,"garmin",prefix)


if __name__ == "__main__":

    storage = S3Client()
    raw_dir = Path(os.environ["GARMIN_FIT_DIR"])

    list_files = get_files(raw_dir)
    upload_files(storage,list_files)