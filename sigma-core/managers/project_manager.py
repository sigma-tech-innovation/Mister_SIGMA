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
        projects = sorted(self.projects.iterdir())

        for p in projects:
            if p.is_dir():
                print("-", p.name)

        return [p.name for p in projects if p.is_dir()]

    def records(self):
        return self.database.load("projects")

    def next_id(self):
        db = self.records()

        if not db:
            return "PRJ-0001"

        last = max(
            int(x["id"].split("-")[1])
            for x in db
        )

        return f"PRJ-{last+1:04d}"

    def get(self, project_id):
        for project in self.records():
            if project.get("id") == project_id:
                return project
        return None

    def exists(self, project_id):
        return self.get(project_id) is not None

    def create(self, project):
        db = self.records()

        if "id" not in project:
            project["id"] = self.next_id()

        db.append(project)
        self.database.save("projects", db)
        return project

    def update(self, project_id, **fields):
        db = self.records()

        for project in db:
            if project.get("id") == project_id:
                project.update(fields)
                self.database.save("projects", db)
                return project

        return None

    def delete(self, project_id):
        db = self.records()
        new_db = [p for p in db if p.get("id") != project_id]

        if len(new_db) == len(db):
            return False

        self.database.save("projects", new_db)
        return True

    def count(self):
        return len(self.records())
