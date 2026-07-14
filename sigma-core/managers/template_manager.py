import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "base_manager",
    Path.cwd() / "sigma-core/managers/base_manager.py"
)

base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)

class TemplateManager(base.BaseManager):

    def records(self):
        return self.database.load("templates")

    def list(self):
        templates = self.records()

        for tpl in templates:
            print(
                f'{tpl["id"]} | {tpl["name"]} | {tpl["version"]}'
            )

        return templates

    def next_id(self):
        db = self.records()

        if not db:
            return "TPL-0001"

        last = max(
            int(x["id"].split("-")[1])
            for x in db
        )

        return f"TPL-{last+1:04d}"

    def get(self, template_id):
        for template in self.records():
            if template.get("id") == template_id:
                return template
        return None

    def exists(self, template_id):
        return self.get(template_id) is not None

    def create(self, template):
        db = self.records()

        if "id" not in template:
            template["id"] = self.next_id()

        db.append(template)
        self.database.save("templates", db)
        return template

    def update(self, template_id, **fields):
        db = self.records()

        for template in db:
            if template.get("id") == template_id:
                template.update(fields)
                self.database.save("templates", db)
                return template

        return None

    def delete(self, template_id):
        db = self.records()
        new_db = [t for t in db if t.get("id") != template_id]

        if len(new_db) == len(db):
            return False

        self.database.save("templates", new_db)
        return True

    def count(self):
        return len(self.records())
