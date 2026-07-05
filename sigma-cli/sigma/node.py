import platform
import socket
import uuid
from pathlib import Path

def get_node():
    return {
        "hostname": socket.gethostname(),
        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "python": platform.python_version(),
        "uuid": hex(uuid.getnode()),
        "workspace": str(Path.cwd())
    }
