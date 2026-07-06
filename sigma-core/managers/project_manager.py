class ProjectManager:

    def __init__(self, engine):
        self.engine = engine

    def list(self):

        for p in sorted(self.engine.projects_dir.iterdir()):
            if p.is_dir():
                print("-", p.name)

    def db(self):
        return self.engine.database.load("projects")

    def next_id(self):

        db = self.db()

        if not db:
            return "PRJ-0001"

        last = max(
            int(x["id"].split("-")[1])
            for x in db
        )

        return f"PRJ-{last+1:04d}"
