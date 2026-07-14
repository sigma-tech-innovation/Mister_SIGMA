from pathlib import Path
import json

ROOT = Path.cwd()

PROJECTS_DIR = ROOT / "sigma-projects"
DB = ROOT / "sigma-db" / "projects.json"


def load_db():
    if not DB.exists():
        return []

    txt = DB.read_text().strip()

    if txt == "":
        return []

    return json.loads(txt)


def save_db(data):
    DB.write_text(
        json.dumps(data, indent=4),
        encoding="utf-8"
    )


def list_projects():

    print("===================================")
    print("        Σ SIGMA PROJECTS")
    print("===================================")

    for p in sorted(PROJECTS_DIR.iterdir()):
        if p.is_dir():
            print("-", p.name)


def create_project(name):

    project = PROJECTS_DIR / name

    if project.exists():
        print("Project already exists.")
        return

    (project / "src").mkdir(parents=True)

    (project / "docs").mkdir()

    (project / "config").mkdir()

    (project / "data").mkdir()

    (project / "logs").mkdir()

    (project / "tests").mkdir()

    (project / "README.md").write_text(
        f"# {name}\n",
        encoding="utf-8"
    )

    db = load_db()

    db.append(
        {
            "id": f"PRJ-{len(db)+1:04d}",
            "name": name,
            "status": "active"
        }
    )

    save_db(db)

    print("Project created:", name)


def run(args):

    if len(args) == 0:
        list_projects()
        return

    if args[0] == "create":

        if len(args) < 2:
            print("Usage:")
            print("sigma projects create NAME")
            return

        create_project(args[1])
        return

    list_projects()
