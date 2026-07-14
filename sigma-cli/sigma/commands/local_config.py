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


def preview():
    manager = engine_module.engine.local_config_migration
    plan = manager.migrate(dry_run=True)

    print("===================================")
    print("   Σ SIGMA LOCAL CONFIG PREVIEW")
    print("===================================")
    print(f"Source       : {plan['source_path']}")
    print(f"Source existe: {plan['source_exists']}")
    print(f"Cible        : {plan['target_path']}")
    print(f"Cible existe : {plan['target_exists']}")
    print(f"Écriture     : {plan['written']}")
    print()

    print("Clés à migrer :")
    print_json(plan["migrated"])

    print("\nClés préservées :")
    print_json(plan["preserved"])

    print("\nClés interdites :")
    print_json(plan["forbidden_found"])

    print("\nRésultat prévu :")
    print_json(plan["result"])

    return plan


def apply():
    manager = engine_module.engine.local_config_migration
    result = manager.migrate(dry_run=False)

    print("===================================")
    print("    Σ SIGMA LOCAL CONFIG APPLY")
    print("===================================")
    print("Migration      : OK")
    print(f"Source         : {result['source_path']}")
    print(f"Cible          : {result['target_path']}")
    print(f"Sauvegarde     : {result['backup_path']}")
    print(f"Écriture       : {result['written']}")
    print()

    print("Configuration locale :")
    print_json(
        engine_module.engine.local_config.load()
    )

    return result


def show():
    manager = engine_module.engine.local_config

    print("===================================")
    print("     Σ SIGMA LOCAL CONFIG")
    print("===================================")
    print(f"Fichier : {manager.path}")
    print(f"Existe  : {manager.exists()}")
    print()

    if not manager.exists():
        print("Configuration locale absente.")
        return {}

    data = manager.load()
    print_json(data)
    return data


def run(args):
    if not args or args[0] == "preview":
        return preview()

    if args[0] == "show":
        return show()

    if args[0] == "apply":
        return apply()

    print(
        "Usage: local-config "
        "[preview|show|apply]"
    )
    return None
