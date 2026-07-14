import importlib.util
import json
from pathlib import Path


ROOT = Path.cwd()

spec = importlib.util.spec_from_file_location(
    "engine",
    ROOT / "sigma-core/engine.py"
)

engine_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine_module)


def print_json(data):
    print(
        json.dumps(
            data,
            indent=4,
            ensure_ascii=False
        )
    )


def snapshot():
    data = engine_module.engine.sync.snapshot()

    print("===================================")
    print("       Σ SIGMA SYNC SNAPSHOT")
    print("===================================")
    print_json(data)

    return data


def validate():
    data = engine_module.engine.sync.validate()

    print("===================================")
    print("       Σ SIGMA SYNC VALIDATE")
    print("===================================")
    print(f"Prêt : {data['ready']}")

    if data["errors"]:
        print("\nErreurs :")

        for error in data["errors"]:
            print(f"- {error}")
    else:
        print("Validation : OK")

    return data


def plan():
    data = engine_module.engine.sync.plan()

    print("===================================")
    print("         Σ SIGMA SYNC PLAN")
    print("===================================")
    print(f"Prêt : {data['ready']}")
    print("\nÉtapes :")

    for index, step in enumerate(
        data["steps"],
        start=1
    ):
        print(f"{index}. {step}")

    if data["validation"]["errors"]:
        print("\nErreurs :")

        for error in data["validation"]["errors"]:
            print(f"- {error}")

    return data


def run(args):
    if not args or args[0] == "snapshot":
        return snapshot()

    if args[0] == "validate":
        return validate()

    if args[0] == "plan":
        return plan()

    print(
        "Usage: sync "
        "[snapshot|validate|plan]"
    )
    return None
