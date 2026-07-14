import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "base_manager",
    Path.cwd() / "sigma-core/managers/base_manager.py"
)

base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)

class TemplateManager(base.BaseManager):

    def list(self):
        templates = self.database.load("templates")

        for tpl in templates:
            print(
                f'{tpl["id"]} | {tpl["name"]} | {tpl["version"]}'
            )

        return templates

    def next_id(self):
        db = self.database.load("templates")

        if not db:
            return "TPL-0001"

        last = max(
            int(x["id"].split("-")[1])
            for x in db
        )

        return f"TPL-{last+1:04d}"

    def get(self, template_id):
        for template in self.database.load("templates"):
            if template.get("id") == template_id:
                return template
        return None

    def exists(self, template_id):
        return self.get(template_id) is not None

    def count(self):
        return len(self.database.load("templates"))
