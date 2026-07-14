import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "base_manager",
    Path.cwd() / "sigma-core/managers/base_manager.py"
)

base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)


class NodeManager(base.BaseManager):

    def records(self):
        return self.database.load("nodes")

    def list(self):
        nodes = self.records()

        for node in nodes:
            print(
                f'{node["id"]} | {node["name"]} | {node["status"]}'
            )

        return nodes

    def next_id(self):
        db = self.records()

        if not db:
            return "NODE-0001"

        last = max(
            int(x["id"].split("-")[1])
            for x in db
        )

        return f"NODE-{last+1:04d}"

    def get(self, node_id):
        for node in self.records():
            if node.get("id") == node_id:
                return node
        return None

    def exists(self, node_id):
        return self.get(node_id) is not None

    def create(self, node):
        db = self.records()

        if "id" not in node:
            node["id"] = self.next_id()

        db.append(node)
        self.database.save("nodes", db)
        return node

    def update(self, node_id, **fields):
        db = self.records()

        for node in db:
            if node.get("id") == node_id:
                node.update(fields)
                self.database.save("nodes", db)
                return node

        return None

    def delete(self, node_id):
        db = self.records()

        new_db = [n for n in db if n.get("id") != node_id]

        if len(new_db) == len(db):
            return False

        self.database.save("nodes", new_db)
        return True

    def count(self):
        return len(self.records())
