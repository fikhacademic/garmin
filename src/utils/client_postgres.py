
import os

import psycopg
from psycopg import sql


class PostgresClient:
    def __init__(self):
        self.connection = psycopg.connect(
            host=os.environ["POSTGRES_HOST"],
            port=os.environ["POSTGRES_PORT"],
            dbname=os.environ["POSTGRES_DB"],
            user=os.environ["POSTGRES_USER"],
            password=os.environ["POSTGRES_PASSWORD"],
            autocommit=True,
        )

    
    def schema_exists(self, schema_name: str) -> bool:
        query = """
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.schemata
                WHERE schema_name = %s
            )
        """

        with self.connection.cursor() as cursor:
            cursor.execute(query, (schema_name,))
            return cursor.fetchone()[0]


    def create_schema(self, schema_name):
        query = sql.SQL(
            "CREATE SCHEMA IF NOT EXISTS {}"
        ).format(sql.Identifier(schema_name))

        with self.connection.cursor() as cursor:
            cursor.execute(query)

    def close(self):
            self.connection.close()
