"""Client S3 générique compatible AWS S3 et SeaweedFS."""

import os
from pathlib import Path
from typing import Iterator

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from dotenv import load_dotenv


class S3Client:
    """Opérations courantes sur un stockage objet compatible S3."""

    def __init__(
        self,
        bucket: str | None = None,
        endpoint_url: str | None = None
    ):
        load_dotenv()

        self.bucket = bucket or os.getenv("S3_BUCKET", "garmin-raw")

        self.client = boto3.client(
            "s3",
            endpoint_url=endpoint_url or os.getenv("S3_ENDPOINT_URL") or None,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
            config=Config(s3={"addressing_style": "path"}),
        )

    # ---------------------------------------------------------
    # BUCKET : EXISTENCE
    # ---------------------------------------------------------

    def bucket_exists(self, bucket: str | None = None) -> bool:
        """Vérifie si un bucket existe."""

        name = bucket or self.bucket

        try:
            self.client.head_bucket(Bucket=name)
            return True

        except ClientError as e:
            code = e.response["Error"]["Code"]

            if code in ("404", "NoSuchBucket", "NotFound"):
                return False

            raise

    def _check_bucket(self, bucket: str | None = None) -> str:
        """Vérifie que le bucket existe avant une opération."""

        name = bucket or self.bucket

        if not self.bucket_exists(name):
            raise ValueError(f"Le bucket '{name}' n'existe pas.")

        return name

    # ---------------------------------------------------------
    # BUCKET : CREATION
    # ---------------------------------------------------------

    def create_bucket(self, bucket: str | None = None) -> None:
        """Crée un bucket uniquement s'il n'existe pas."""

        name = bucket or self.bucket

        if self.bucket_exists(name):
            print(f"Le bucket '{name}' existe déjà.")
            return

        region = self.client.meta.region_name or "us-east-1"

        params = {"Bucket": name}

        if region != "us-east-1":
            params["CreateBucketConfiguration"] = {
                "LocationConstraint": region
            }

        self.client.create_bucket(**params)

        print(f"Bucket '{name}' créé.")

    # ---------------------------------------------------------
    # BUCKET : SUPPRESSION
    # ---------------------------------------------------------

    def delete_bucket(self, bucket: str | None = None) -> None:
        """Supprime un bucket vide."""

        name = self._check_bucket(bucket)

        self.client.delete_bucket(Bucket=name)

        print(f"Bucket '{name}' supprimé.")

    # ---------------------------------------------------------
    # FICHIER : UPLOAD
    # ---------------------------------------------------------

    def upload_file(
        self,
        local_path: str | Path,
        object_key: str,
        bucket: str | None = None
    ) -> None:
        """Envoie un fichier local dans un bucket."""

        name = self._check_bucket(bucket)

        path = Path(local_path)

        if not path.is_file():
            raise FileNotFoundError(
                f"Fichier introuvable : {path}"
            )

        self.client.upload_file(
            str(path),
            name,
            object_key
        )

        print(f"Fichier '{path.name}' envoyé vers '{name}/{object_key}'.")

    # ---------------------------------------------------------
    # FICHIER : DOWNLOAD
    # ---------------------------------------------------------

    def download_file(
        self,
        object_key: str,
        local_path: str | Path,
        bucket: str | None = None
    ) -> None:
        """Télécharge un objet S3 vers un fichier local."""

        name = self._check_bucket(bucket)

        path = Path(local_path)

        path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self.client.download_file(
            name,
            object_key,
            str(path)
        )

        print(f"Fichier '{object_key}' téléchargé vers '{path}'.")

    # ---------------------------------------------------------
    # FICHIER : SUPPRESSION
    # ---------------------------------------------------------

    def delete_file(
        self,
        object_key: str,
        bucket: str | None = None
    ) -> None:
        """Supprime un objet S3."""

        name = self._check_bucket(bucket)

        self.client.delete_object(
            Bucket=name,
            Key=object_key
        )

        print(f"Fichier '{object_key}' supprimé du bucket '{name}'.")

    # ---------------------------------------------------------
    # FICHIER : LISTING
    # ---------------------------------------------------------

    def list_files(
        self,
        prefix: str = "",
        bucket: str | None = None
    ) -> Iterator[str]:
        """Liste les objets d'un bucket avec pagination."""

        name = self._check_bucket(bucket)

        paginator = self.client.get_paginator("list_objects_v2")

        for page in paginator.paginate(
            Bucket=name,
            Prefix=prefix
        ):
            for obj in page.get("Contents", []):
                yield obj["Key"]

    # ---------------------------------------------------------
    # FICHIER : METADATA
    # ---------------------------------------------------------

    def get_metadata(
        self,
        object_key: str,
        bucket: str | None = None
    ) -> dict:
        """Récupère les métadonnées d'un objet S3."""

        name = self._check_bucket(bucket)

        response = self.client.head_object(
            Bucket=name,
            Key=object_key
        )

        return {
            "size_bytes": response["ContentLength"],
            "last_modified": response["LastModified"],
            "etag": response.get("ETag"),
            "content_type": response.get("ContentType"),
            "metadata": response.get("Metadata", {}),
        }


# ---------------------------------------------------------
# TEST DU CLIENT S3
# ---------------------------------------------------------

if __name__ == "__main__":

    storage = S3Client()

    print(f"Endpoint S3 : {storage.client.meta.endpoint_url}")
    print(f"Bucket configuré : {storage.bucket}")

    # Vérifier l'existence du bucket
    if storage.bucket_exists():
        print(f"Le bucket '{storage.bucket}' existe.")
    else:
        print(f"Le bucket '{storage.bucket}' n'existe pas.")

    # Créer le bucket s'il n'existe pas
    storage.create_bucket()

    # Lister les fichiers FIT
    print("\nFichiers FIT présents dans le bucket :")

    for key in storage.list_files(prefix="fit/"):
        print(key)

    # Exemples d'opérations (décommenter pour tester)

    # Upload
    # storage.upload_file(
    #     local_path="data/raw/activity.fit",
    #     object_key="fit/activity.fit"
    # )

    # Download
    # storage.download_file(
    #     object_key="fit/activity.fit",
    #     local_path="data/download/activity.fit"
    # )

    # Metadata
    # metadata = storage.get_metadata("fit/activity.fit")
    # print(metadata)

    # Suppression d'un fichier
    # storage.delete_file("fit/activity.fit")

    # Suppression du bucket (doit être vide)
    # storage.delete_bucket()