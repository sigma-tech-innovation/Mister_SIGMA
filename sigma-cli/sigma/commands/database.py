import importlib.util
import json
from pathlib import Path


ROOT = Path.cwd()

spec = importlib.util.spec_from_file_location(
    "engine",
    ROOT / "sigma-core/engine.py",
)
engine_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine_module)


def print_json(data):
    print(
        json.dumps(
            data,
            indent=4,
            ensure_ascii=False,
        )
    )


def status():
    engine = engine_module.engine

    data = {
        "configuration": (
            engine.database_config.snapshot()
        ),
        "runtime": (
            engine.database.snapshot()
        ),
    }

    print("===================================")
    print("        Σ SIGMA DATABASE")
    print("===================================")
    print_json(data)

    return data


def backend(args):
    engine = engine_module.engine

    if not args:
        data = {
            "configured": (
                engine.database_config.backend()
            ),
            "runtime": engine.database.backend_key,
            "available": (
                engine.database.available_backends()
            ),
        }

        print_json(data)
        return data

    selected = args[0]
    url = None

    if len(args) > 1:
        url = args[1]

    result = engine.database_config.configure(
        backend=selected,
        url=url,
    )

    print_json(result)
    print(
        "Restart Sigma to activate "
        "the configured backend."
    )

    return result


def migrate(args):
    if not args:
        print(
            "Usage: database migrate "
            "<target-backend> [database ...]"
        )
        return None

    engine = engine_module.engine
    target = args[0]
    names = args[1:] or None

    result = engine.database.migrate(
        target,
        names=names,
    )

    print_json(result)
    return result


def run(args):
    if not args or args[0] == "status":
        return status()

    if args[0] == "backend":
        return backend(args[1:])

    if args[0] == "migrate":
        return migrate(args[1:])

    if args[0] == "list":
        data = engine_module.engine.database.list()

        for name in data:
            print(f"- {name}")

        return data

    print(
        "Usage: database "
        "[status|backend|migrate|list]"
    )
    return None
