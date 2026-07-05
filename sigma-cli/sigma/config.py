from pathlib import Path

SIGMA_VERSION = "0.6.0"

SIGMA_ROOT = Path.cwd()
REGISTRY_PATH = SIGMA_ROOT / "sigma-core" / "registry" / "registry.json"

def get_config():
    return {
        "version": SIGMA_VERSION,
        "root": str(SIGMA_ROOT),
        "registry": str(REGISTRY_PATH)
    }
