"""
CLI Device Sigma (lecture seule).
"""

import json


def _manager(engine):
    return engine.device


def status(engine, *_):
    print(
        json.dumps(
            _manager(engine).snapshot(),
            indent=4,
        )
    )


def validate(engine, *_):
    print(
        json.dumps(
            _manager(engine).validate(),
            indent=4,
        )
    )


def list_devices(engine, *_):
    devices = [
        device.as_dict()
        for device in _manager(engine).list()
    ]

    print(
        json.dumps(
            devices,
            indent=4,
        )
    )


def run(args):
    import importlib.util
    from pathlib import Path

    spec = importlib.util.spec_from_file_location(
        "engine",
        Path.cwd() / "sigma-core/engine.py",
    )

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    engine = module.engine

    if not args:
        status(engine)
        return

    command = args[0]

    if command == "status":
        status(engine)

    elif command == "validate":
        validate(engine)

    elif command == "list":
        list_devices(engine)

    else:
        print("Unknown device command")
