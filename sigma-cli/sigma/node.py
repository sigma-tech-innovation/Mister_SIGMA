import json
import platform
import socket
import uuid
from pathlib import Path
from sigma.config import REGISTRY_PATH

def get_node():
    node_id = f"SIG-NODE-{hex(uuid.getnode())[2:].upper()}"
    hostname = socket.gethostname()

    return {
        "id": node_id,
        "name": hostname,
        "type": "node",
        "status": "active",
        "hostname": hostname,
        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "python": platform.python_version(),
        "uuid": hex(uuid.getnode()),
        "workspace": str(Path.cwd())
    }

def register_node():
    node = get_node()
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    for i, obj in enumerate(data["objects"]):
        if obj.get("id") == node["id"]:
            data["objects"][i] = node
            REGISTRY_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
            print("Node updated.")
            return

    data["objects"].append(node)
    REGISTRY_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print("Node registered.")
