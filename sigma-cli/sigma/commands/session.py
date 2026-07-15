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
    manager = engine_module.engine.session
    data = manager.snapshot()

    print("===================================")
    print("         Σ SIGMA SESSION")
    print("===================================")
    print_json(data)

    return data


def validate():
    result = (
        engine_module.engine
        .session
        .validate()
    )

    print_json(result)
    return result


def list_sessions():
    sessions = (
        engine_module.engine
        .session
        .list()
    )

    data = [
        session.as_dict()
        for session in sessions
    ]

    print_json(data)
    return data


def show(session_id):
    session = (
        engine_module.engine
        .session
        .get(session_id)
    )

    if session is None:
        data = {
            "found": False,
            "session_id": session_id,
        }
    else:
        data = {
            "found": True,
            "session": session.as_dict(),
        }

    print_json(data)
    return data


def run(args):
    if not args or args[0] == "status":
        return status()

    if args[0] == "validate":
        return validate()

    if args[0] == "list":
        return list_sessions()

    if args[0] == "show":
        if len(args) != 2:
            print(
                "Usage: session show "
                "<session-id>"
            )
            return None

        return show(args[1])

    print(
        "Usage: session "
        "[status|validate|list|show]"
    )
    return None
