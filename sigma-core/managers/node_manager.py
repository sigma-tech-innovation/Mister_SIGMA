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
        nodes = self.database.load("nodes")

        for node in nodes:
            print(
                f'{node["id"]} | {node["name"]} | {node["status"]}'
            )

        return nodes

    def next_id(self):
        db = self.database.load("nodes")

        if not db:
            return "NODE-0001"

        last = max(
            int(x["id"].split("-")[1])
            for x in db
        )

        return f"NODE-{last+1:04d}"

    def get(self, node_id):
        for node in self.database.load("nodes"):
            if node.get("id") == node_id:
                return node
        return None

    def exists(self, node_id):
        return self.get(node_id) is not None

    def count(self):
        return len(self.database.load("nodes"))
