import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "base_manager",
    Path.cwd() / "sigma-core/managers/base_manager.py"
)

base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)

class ReleaseManager(base.BaseManager):

    def list(self):
        releases = self.database.load("releases")

        for rel in releases:
            print(
                f'{rel["id"]} | {rel["version"]} | {rel["status"]}'
            )

        return releases

    def next_id(self):
        db = self.database.load("releases")

        if not db:
            return "REL-0001"

        last = max(
            int(x["id"].split("-")[1])
            for x in db
        )

        return f"REL-{last+1:04d}"

    def get(self, release_id):
        for release in self.database.load("releases"):
            if release.get("id") == release_id:
                return release
        return None

    def exists(self, release_id):
        return self.get(release_id) is not None

    def create(self, release):
        db = self.database.load("releases")

        if "id" not in release:
            release["id"] = self.next_id()

        db.append(release)
        self.database.save("releases", db)
        return release

    def update(self, release_id, **fields):
        db = self.database.load("releases")

        for release in db:
            if release.get("id") == release_id:
                release.update(fields)
                self.database.save("releases", db)
                return release

        return None

    def delete(self, release_id):
        db = self.database.load("releases")
        new_db = [r for r in db if r.get("id") != release_id]

        if len(new_db) == len(db):
            return False

        self.database.save("releases", new_db)
        return True

    def count(self):
        return len(self.database.load("releases"))
