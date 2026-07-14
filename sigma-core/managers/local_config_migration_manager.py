import json
import shutil
import uuid
from datetime import datetime
from pathlib import Path


class LocalConfigMigrationManager:
    """
    Migration contrôlée des données locales historiques depuis
    sigma-config.json vers .sigma-workspace/configs/local.json.
    """

    FIELD_MAPPING = {
        "machine_id": "machine_id",
        "node_id": "node_id",
        "hostname": "hostname",
        "device_type": "device_type",
        "profile": "local_profile",
        "environment": "local_environment",
        "last_sync": "last_sync",
    }

    FORBIDDEN_LOCAL_KEYS = {
        "user_id",
        "organization_id",
        "workspace_id",
        "owner",
        "role",
        "team",
        "registry_url",
        "api_endpoint",
        "sync_enabled",
        "project",
    }

    def __init__(self, engine):
        self.engine = engine
        self.source_path = engine.root / "sigma-config.json"
        self.target = engine.local_config

    def load_source(self):
        if not self.source_path.exists():
            return {}

        data = self.engine.load_json(self.source_path)

        if isinstance(data, dict):
            return data

        return {}

    def preview(self):
        source = self.load_source()
        target = self.target.load()

        result = dict(target)
        migrated = {}
        preserved = {}

        for source_key, target_key in self.FIELD_MAPPING.items():
            if target_key in result:
                preserved[target_key] = result[target_key]
                continue

            if source_key in source:
                result[target_key] = source[source_key]
                migrated[target_key] = source[source_key]

        if not result.get("installation_id"):
            result["installation_id"] = str(uuid.uuid4())
            migrated["installation_id"] = result[
                "installation_id"
            ]

        forbidden_found = sorted(
            key
            for key in self.FORBIDDEN_LOCAL_KEYS
            if key in result
        )

        return {
            "source_exists": self.source_path.exists(),
            "target_exists": self.target.exists(),
            "source_path": str(self.source_path),
            "target_path": str(self.target.path),
            "migrated": migrated,
            "preserved": preserved,
            "forbidden_found": forbidden_found,
            "result": result,
        }

    def backup_source(self):
        if not self.source_path.exists():
            return None

        backup_dir = (
            self.engine.root
            / ".sigma-workspace"
            / "backups"
            / "local-config-migration"
        )
        backup_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        timestamp = datetime.now().strftime(
            "%Y%m%d-%H%M%S-%f"
        )

        backup_path = backup_dir / (
            f"sigma-config-{timestamp}.json"
        )

        shutil.copy2(
            self.source_path,
            backup_path
        )

        return backup_path

    def migrate(self, dry_run=True):
        plan = self.preview()

        if plan["forbidden_found"]:
            raise ValueError(
                "Forbidden local keys detected: "
                + ", ".join(plan["forbidden_found"])
            )

        if dry_run:
            return {
                **plan,
                "dry_run": True,
                "written": False,
                "backup_path": None,
            }

        backup_path = self.backup_source()
        self.target.save(plan["result"])

        return {
            **plan,
            "dry_run": False,
            "written": True,
            "backup_path": (
                str(backup_path)
                if backup_path is not None
                else None
            ),
        }
