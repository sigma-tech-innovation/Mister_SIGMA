import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "base_manager",
    Path.cwd() / "sigma-core/managers/base_manager.py"
)

base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)

class ProjectManager(base.BaseManager):

    def __init__(self, engine):
        super().__init__(engine)

    def list(self):
        for p in sorted(self.projects.iterdir()):
            if p.is_dir():
                print("-", p.name)

    def db(self):
        return self.database.load("projects")

    def next_id(self):
        db = self.db()

        if not db:
            return "PRJ-0001"

        last = max(
            int(x["id"].split("-")[1])
            for x in db
        )

        return f"PRJ-{last+1:04d}"

    def get(self, project_id):
        for project in self.db():
            if project.get("id") == project_id:
                return project
        return None

    def exists(self, project_id):
        return self.get(project_id) is not None

    def count(self):
        return len(self.db())
