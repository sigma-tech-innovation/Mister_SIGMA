import json
import sqlite3
from pathlib import Path


class SQLiteBackend:

    def __init__(self, root):
        self.root = Path(root)
        self.path = self.root / "sigma.sqlite3"
        self._initialize()

    def connect(self):
        self.root.mkdir(
            parents=True,
            exist_ok=True
        )

        return sqlite3.connect(self.path)

    def _initialize(self):
        with self.connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS sigma_records (
                    name TEXT PRIMARY KEY,
                    payload TEXT NOT NULL
                )
                """
            )

    def load(self, name):
        with self.connect() as connection:
            row = connection.execute(
                """
                SELECT payload
                FROM sigma_records
                WHERE name = ?
                """,
                (name,)
            ).fetchone()

        if row is None:
            return []

        return json.loads(row[0])

    def save(self, name, data):
        payload = json.dumps(
            data,
            ensure_ascii=False
        )

        with self.connect() as connection:
            connection.execute(
                """
                INSERT INTO sigma_records (
                    name,
                    payload
                )
                VALUES (?, ?)
                ON CONFLICT(name)
                DO UPDATE SET payload = excluded.payload
                """,
                (name, payload)
            )

        return data

    def exists(self, name):
        with self.connect() as connection:
            row = connection.execute(
                """
                SELECT 1
                FROM sigma_records
                WHERE name = ?
                """,
                (name,)
            ).fetchone()

        return row is not None

    def delete(self, name):
        with self.connect() as connection:
            cursor = connection.execute(
                """
                DELETE FROM sigma_records
                WHERE name = ?
                """,
                (name,)
            )

        return cursor.rowcount > 0

    def list(self):
        with self.connect() as connection:
            rows = connection.execute(
                """
                SELECT name
                FROM sigma_records
                ORDER BY name
                """
            ).fetchall()

        return [
            row[0]
            for row in rows
        ]
