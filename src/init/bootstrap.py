from src.utils.client_S3 import S3Client
from src.utils.client_postgres import PostgresClient

storage = S3Client()
storage.create_bucket("garmin")

db_client = PostgresClient()
print("Connexion postgres établie")
try:
    for schema in ["staging", "intermediate", "marts"]:
        if db_client.schema_exists(schema):
            print(f"Le schéma {schema} existe déjà")
        else:
            db_client.create_schema(schema)
            print(f"Le schéma {schema} a été créé")
finally:
    db_client.close()



