import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "base_manager",
    Path.cwd() / "sigma-core/managers/base_manager.py"
)

base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)

class NodeManager(base.BaseManager):

    def list(self):
        for node in self.database.load("nodes"):
            print(
                f'{node["id"]} | {node["name"]} | {node["status"]}'
            )

    def next_id(self):
        db = self.database.load("nodes")

        if not db:
            return "NODE-0001"

        last = max(
            int(x["id"].split("-")[1])
            for x in db
        )

        return f"NODE-{last+1:04d}"
