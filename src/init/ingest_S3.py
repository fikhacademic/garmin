from src.utils.client_S3 import S3Client
import os
from pathlib import Path
from dotenv import load_dotenv
from collections import Counter

load_dotenv()

storage = S3Client()

raw_dir = Path(os.environ["GARMIN_FIT_DIR"])

def get_extensions(path) :

    files = [
        file for file in path.rglob("*")
        if file.is_file()
    ]

    extensions = Counter(file.suffix.lower() for file in files)

    liste_extensions = [ext.lstrip(".") for ext in extensions.keys()]

    return liste_extensions

liste_extensions = get_extensions(raw_dir)

# for ext in liste_extensions :
#     storage.create_bucket(ext)

