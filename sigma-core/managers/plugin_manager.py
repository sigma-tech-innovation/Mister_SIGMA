import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "base_manager",
    Path.cwd() / "sigma-core/managers/base_manager.py"
)

base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)

class PluginManager(base.BaseManager):

    def db(self):
        return self.database.load("plugins")

    def save(self,data):
        self.database.save("plugins",data)

    def list(self):
        for p in self.db():
            print(f'{p["id"]} | {p["name"]} | {p["version"]} | {p["status"]}')

    def next_id(self):
        db=self.db()
        if not db:
            return "PLG-0001"
        return f'PLG-{max(int(x["id"].split("-")[1]) for x in db)+1:04d}'

    def add(self,name,version="1.0.0"):
        db=self.db()
        db.append({
            "id":self.next_id(),
            "name":name,
            "version":version,
            "status":"active"
        })
        self.save(db)
