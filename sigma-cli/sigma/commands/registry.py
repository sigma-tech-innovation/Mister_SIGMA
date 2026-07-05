import json
from sigma.config import REGISTRY_PATH

REQUIRED_FIELDS = ["id", "name", "type", "status"]

def load():
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

def list_registry():
    data = load()
    print(f"Σ Sigma Registry v{data['version']}")

    for obj in data["objects"]:
        print(
            f"- {obj.get('id','?')} | "
            f"{obj.get('name', obj.get('hostname','Unknown'))} | "
            f"{obj.get('type','unknown')} | "
            f"{obj.get('status','unknown')}"
        )

def show_registry(object_id):
    data = load()

    for obj in data["objects"]:
        if obj.get("id") == object_id:
            for k, v in obj.items():
                print(f"{k}: {v}")
            return

    print("Object not found")

def validate_registry():
    data = load()
    errors = 0

    print("Σ Sigma Registry Validation")

    for obj in data["objects"]:
        for field in REQUIRED_FIELDS:
            if field not in obj or obj[field] == "":
                print(f"ERROR: {obj.get('id','UNKNOWN')} missing {field}")
                errors += 1

    if errors == 0:
        print("Registry status: OK")
    else:
        print(f"Registry status: {errors} error(s)")
