import json
from sigma.config import REGISTRY_PATH

def load():
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

def list_registry():
    data = load()
    print(f"Σ Sigma Registry v{data['version']}")
    for obj in data["objects"]:
        print(f"- {obj['id']} | {obj['name']} | {obj['type']} | {obj['status']}")

def show_registry(object_id):
    data = load()
    for obj in data["objects"]:
        if obj["id"] == object_id:
            for k, v in obj.items():
                print(f"{k}: {v}")
            return
    print("Object not found")
