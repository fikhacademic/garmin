from src.utils.client_S3 import S3Client
import fitdecode

storage = S3Client()
list_files = list(storage.list_files("fit","garmin"))
print(len(list_files))

