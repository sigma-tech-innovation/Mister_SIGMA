import subprocess
from datetime import datetime, timezone


class SyncManager:
    """
    Socle de synchronisation Sigma.

    Cette version inspecte l'état local et prépare la synchronisation.
    Elle n'exécute aucun pull, push ou appel distant automatiquement.
    """

    def __init__(self, engine):
        self.engine = engine

    def configuration(self):
        return {
            "enabled": self.engine.config.get(
                "sync_enabled",
                False
            ),
            "registry_url": self.engine.config.get(
                "registry_url",
                ""
            ),
            "api_endpoint": self.engine.config.get(
                "api_endpoint",
                ""
            ),
            "last_sync": self.engine.local_config.get(
                "last_sync",
                ""
            ),
        }

    def git(self):
        def run(*args):
            result = subprocess.run(
                ["git", *args],
                cwd=self.engine.root,
                capture_output=True,
                text=True,
                check=False,
            )

            return {
                "returncode": result.returncode,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
            }

        branch_result = run(
            "branch",
            "--show-current"
        )
        status_result = run(
            "status",
            "--short"
        )
        remote_result = run(
            "remote",
            "get-url",
            "origin"
        )

        return {
            "available": (
                branch_result["returncode"] == 0
            ),
            "branch": branch_result["stdout"],
            "clean": (
                status_result["returncode"] == 0
                and status_result["stdout"] == ""
            ),
            "changes": status_result["stdout"].splitlines(),
            "origin": remote_result["stdout"],
            "errors": [
                item["stderr"]
                for item in (
                    branch_result,
                    status_result,
                    remote_result,
                )
                if item["stderr"]
            ],
        }

    def identity(self):
        global_config = self.engine.config.load()
        local_config = self.engine.local_config.load()

        return {
            "organization_id": global_config.get(
                "organization_id"
            ),
            "user_id": global_config.get("user_id"),
            "workspace_id": global_config.get(
                "workspace_id"
            ),
            "installation_id": local_config.get(
                "installation_id"
            ),
            "machine_id": local_config.get(
                "machine_id"
            ),
            "node_id": local_config.get("node_id"),
        }

    def snapshot(self):
        return {
            "configuration": self.configuration(),
            "identity": self.identity(),
            "git": self.git(),
        }

    def validate(self):
        snapshot = self.snapshot()
        identity = snapshot["identity"]
        configuration = snapshot["configuration"]
        git_state = snapshot["git"]

        required_identity = (
            "organization_id",
            "user_id",
            "workspace_id",
            "installation_id",
            "machine_id",
            "node_id",
        )

        missing = [
            key
            for key in required_identity
            if not identity.get(key)
        ]

        errors = []

        if missing:
            errors.append(
                "Missing identity fields: "
                + ", ".join(missing)
            )

        if not configuration["enabled"]:
            errors.append(
                "Synchronization is disabled"
            )

        if not configuration["registry_url"]:
            errors.append(
                "Registry URL is missing"
            )

        if not git_state["available"]:
            errors.append(
                "Git repository is unavailable"
            )

        if git_state["available"] and not git_state["clean"]:
            errors.append(
                "Git working tree is not clean"
            )

        return {
            "ready": not errors,
            "missing": missing,
            "errors": errors,
            "snapshot": snapshot,
        }

    def plan(self):
        validation = self.validate()

        return {
            "ready": validation["ready"],
            "steps": [
                "validate-identity",
                "validate-local-installation",
                "validate-git-repository",
                "fetch-remote-state",
                "detect-conflicts",
                "synchronize-shared-data",
                "update-local-sync-state",
                "emit-sync-event",
            ],
            "validation": validation,
        }

    def mark_synced(self, timestamp=None):
        value = timestamp or datetime.now(
            timezone.utc
        ).isoformat()

        self.engine.local_config.set(
            "last_sync",
            value
        )

        self.engine.event.emit(
            "sync.completed",
            value
        )

        return value
