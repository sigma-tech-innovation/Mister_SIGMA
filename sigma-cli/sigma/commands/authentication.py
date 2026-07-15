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
    manager = engine_module.engine.authentication
    data = manager.snapshot()

    print("===================================")
    print("     Σ SIGMA AUTHENTICATION")
    print("===================================")
    print_json(data)

    return data


def validate():
    result = (
        engine_module.engine
        .authentication
        .validate()
    )

    print_json(result)
    return result


def list_credentials():
    records = (
        engine_module.engine
        .authentication
        .list()
    )

    print_json(records)
    return records


def show(credential_id):
    record = (
        engine_module.engine
        .authentication
        .get(credential_id)
    )

    if record is None:
        data = {
            "found": False,
            "credential_id": credential_id,
        }
    else:
        data = {
            "found": True,
            "credential": record,
        }

    print_json(data)
    return data


def audit(args):
    credential_id = None
    user_id = None

    index = 0

    while index < len(args):
        argument = args[index]

        if argument == "--credential":
            if index + 1 >= len(args):
                print(
                    "Usage: authentication audit "
                    "[--credential ID] [--user ID]"
                )
                return None

            credential_id = args[index + 1]
            index += 2
            continue

        if argument == "--user":
            if index + 1 >= len(args):
                print(
                    "Usage: authentication audit "
                    "[--credential ID] [--user ID]"
                )
                return None

            user_id = args[index + 1]
            index += 2
            continue

        print(
            "Usage: authentication audit "
            "[--credential ID] [--user ID]"
        )
        return None

    records = (
        engine_module.engine
        .authentication
        .list_audit(
            credential_id=credential_id,
            user_id=user_id,
        )
    )

    print_json(records)
    return records


def policy():
    result = (
        engine_module.engine
        .authentication
        .password_policy()
    )

    print_json(result)
    return result


def run(args):
    if not args or args[0] == "status":
        return status()

    command = args[0]

    if command == "validate":
        return validate()

    if command == "list":
        return list_credentials()

    if command == "show":
        if len(args) != 2:
            print(
                "Usage: authentication show "
                "<credential-id>"
            )
            return None

        return show(args[1])

    if command == "audit":
        return audit(args[1:])

    if command == "policy":
        return policy()

    print(
        "Usage: authentication "
        "[status|validate|list|show|audit|policy]"
    )
    return None
