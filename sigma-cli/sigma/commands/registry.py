import json
from sigma.config import REGISTRY_PATH

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
