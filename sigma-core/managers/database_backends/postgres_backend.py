import importlib
import json


class PostgreSQLBackend:
    """
    Backend PostgreSQL optionnel.

    Le pilote psycopg est chargé uniquement lors de la connexion.
    """

    def __init__(
        self,
        root=None,
        database_url=None,
        connect_factory=None,
    ):
        self.root = root
        self.database_url = database_url
        self.connect_factory = connect_factory

    def driver_available(self):
        if self.connect_factory is not None:
            return True

        try:
            importlib.import_module("psycopg")
            return True
        except ImportError:
            return False

    def connect(self):
        if self.connect_factory is not None:
            return self.connect_factory(
                self.database_url
            )

        try:
            psycopg = importlib.import_module(
                "psycopg"
            )
        except ImportError as error:
            raise RuntimeError(
                "PostgreSQL backend requires psycopg"
            ) from error

        if not self.database_url:
            raise RuntimeError(
                "PostgreSQL database URL is missing"
            )

        return psycopg.connect(
            self.database_url
        )

    def initialize(self):
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS sigma_records (
                        name TEXT PRIMARY KEY,
                        payload JSONB NOT NULL
                    )
                    """
                )

        return True

    def load(self, name):
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT payload
                    FROM sigma_records
                    WHERE name = %s
                    """,
                    (name,),
                )
                row = cursor.fetchone()

        if row is None:
            return []

        payload = row[0]

        if isinstance(payload, str):
            return json.loads(payload)

        return payload

    def save(self, name, data):
        payload = json.dumps(
            data,
            ensure_ascii=False,
        )

        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO sigma_records (
                        name,
                        payload
                    )
                    VALUES (%s, %s::jsonb)
                    ON CONFLICT (name)
                    DO UPDATE SET
                        payload = EXCLUDED.payload
                    """,
                    (name, payload),
                )

        return data

    def exists(self, name):
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT 1
                    FROM sigma_records
                    WHERE name = %s
                    """,
                    (name,),
                )
                row = cursor.fetchone()

        return row is not None

    def delete(self, name):
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM sigma_records
                    WHERE name = %s
                    """,
                    (name,),
                )
                deleted = cursor.rowcount

        return deleted > 0

    def list(self):
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT name
                    FROM sigma_records
                    ORDER BY name
                    """
                )
                rows = cursor.fetchall()

        return [
            row[0]
            for row in rows
        ]
