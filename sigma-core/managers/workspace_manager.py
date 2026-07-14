import uuid
from pathlib import Path
import shutil


class WorkspaceManager:

    DATABASE_NAME = "workspaces"

    REQUIRED_FIELDS = {
        "id",
        "organization_id",
        "name",
        "slug",
        "owner_user_id",
        "status",
        "root_path",
    }

    STATUSES = {
        "active",
        "archived",
        "suspended",
    }

    def __init__(self, engine):
        self.engine = engine

    # =====================================================
    # Compatibilité V1
    # =====================================================

    def root(self):
        return self.engine.root

    def path(self, *parts):
        return self.engine.root.joinpath(*parts)

    def exists(self, *parts):
        return self.path(*parts).exists()

    def list(self, *parts):
        target = self.path(*parts)

        if not target.exists() or not target.is_dir():
            return []

        return sorted(
            target.iterdir(),
            key=lambda item: item.name,
        )

    def count(self, *parts):
        if parts:
            return len(self.list(*parts))

        if hasattr(self.engine, "database"):
            return len(self.records())

        return len(self.list())

    def create(self, *parts, content=None, directory=False):
        if parts and isinstance(parts[0], dict):
            return self.create_record(parts[0])

        target = self.path(*parts)

        if target.exists():
            return None

        if directory:
            target.mkdir(parents=True)
        else:
            target.parent.mkdir(
                parents=True,
                exist_ok=True,
            )
            target.write_text(
                content or "",
                encoding="utf-8",
            )

        return target

    def update(self, *parts, content=None, **fields):
        if len(parts) == 1 and fields:
            return self.update_record(
                parts[0],
                **fields,
            )

        target = self.path(*parts)

        if not target.exists() or target.is_dir():
            return None

        target.write_text(
            content,
            encoding="utf-8",
        )

        return target

    def delete(self, *parts):
        if len(parts) == 1 and str(parts[0]).startswith("WS-"):
            return self.archive(parts[0])

        target = self.path(*parts)

        if not target.exists():
            return False

        if target.is_dir():
            shutil.rmtree(target)
        else:
            target.unlink()

        return True

    # =====================================================
    # Workspace Database V2
    # =====================================================

    def records(self):
        return self.engine.database.load(
            self.DATABASE_NAME
        )

    def save_records(self, records):
        self.engine.database.save(
            self.DATABASE_NAME,
            records
        )

    def normalize_slug(self, value):
        return (
            str(value or "")
            .strip()
            .lower()
            .replace(" ", "-")
        )

    def next_id(self):
        return f"WS-{uuid.uuid4()}"

    def get(self, workspace_id):
        for workspace in self.records():
            if workspace.get("id") == workspace_id:
                return workspace
        return None

    def get_by_slug(self, slug):
        slug = self.normalize_slug(slug)

        for workspace in self.records():
            if workspace.get("slug") == slug:
                return workspace

        return None

    def exists_record(self, workspace_id):
        return self.get(workspace_id) is not None

    def validate_record(self, workspace):
        errors = []

        missing = [
            field
            for field in self.REQUIRED_FIELDS
            if not workspace.get(field)
        ]

        if missing:
            errors.append(
                "Missing fields: "
                + ", ".join(sorted(missing))
            )

        if (
            workspace.get("status")
            not in self.STATUSES
        ):
            errors.append("Invalid status")

        return {
            "valid": not errors,
            "errors": errors,
        }

    def create_record(self, data):
        workspace = dict(data)

        workspace.setdefault(
            "id",
            self.next_id()
        )

        workspace.setdefault(
            "organization_id",
            self.engine.context.organization_id()
        )

        workspace.setdefault(
            "owner_user_id",
            self.engine.context.user_id()
        )

        workspace["slug"] = self.normalize_slug(
            workspace.get("slug")
            or workspace.get("name")
        )

        workspace.setdefault(
            "status",
            "active"
        )

        workspace.setdefault(
            "root_path",
            str(self.engine.root)
        )

        workspace.setdefault(
            "description",
            ""
        )

        workspace.setdefault(
            "metadata",
            {}
        )

        workspace.setdefault(
            "created_at",
            self.engine.now()
        )

        workspace["updated_at"] = (
            self.engine.now()
        )

        validation = self.validate_record(
            workspace
        )

        if not validation["valid"]:
            raise ValueError(
                "; ".join(validation["errors"])
            )

        if self.get(workspace["id"]):
            return None

        if self.get_by_slug(
            workspace["slug"]
        ):
            return None

        records = self.records()
        records.append(workspace)
        self.save_records(records)

        self.engine.event.emit(
            "workspace.created",
            workspace
        )

        return workspace

    def update_record(
        self,
        workspace_id,
        **fields
    ):
        records = self.records()

        for workspace in records:

            if workspace["id"] != workspace_id:
                continue

            workspace.update(fields)
            workspace["updated_at"] = (
                self.engine.now()
            )

            validation = self.validate_record(
                workspace
            )

            if not validation["valid"]:
                raise ValueError(
                    "; ".join(validation["errors"])
                )

            self.save_records(records)

            self.engine.event.emit(
                "workspace.updated",
                workspace
            )

            return workspace

        return None

    def create_record(self, data):
        workspace = dict(data)

        workspace.setdefault(
            "id",
            self.next_id()
        )

        workspace.setdefault(
            "organization_id",
            self.engine.context.organization_id()
        )

        workspace.setdefault(
            "owner_user_id",
            self.engine.context.user_id()
        )

        workspace["slug"] = self.normalize_slug(
            workspace.get("slug")
            or workspace.get("name")
        )

        workspace.setdefault(
            "status",
            "active"
        )

        workspace.setdefault(
            "root_path",
            str(self.engine.root)
        )

        workspace.setdefault(
            "description",
            ""
        )

        workspace.setdefault(
            "metadata",
            {}
        )

        workspace.setdefault(
            "created_at",
            self.engine.now()
        )

        workspace["updated_at"] = (
            self.engine.now()
        )

        validation = self.validate_record(
            workspace
        )

        if not validation["valid"]:
            raise ValueError(
                "; ".join(validation["errors"])
            )

        if self.get(workspace["id"]):
            return None

        if self.get_by_slug(
            workspace["slug"]
        ):
            return None

        records = self.records()
        records.append(workspace)
        self.save_records(records)

        self.engine.event.emit(
            "workspace.created",
            workspace
        )

        return workspace

    def update_record(
        self,
        workspace_id,
        **fields
    ):
        records = self.records()

        for workspace in records:

            if workspace["id"] != workspace_id:
                continue

            workspace.update(fields)
            workspace["updated_at"] = (
                self.engine.now()
            )

            validation = self.validate_record(
                workspace
            )

            if not validation["valid"]:
                raise ValueError(
                    "; ".join(validation["errors"])
                )

            self.save_records(records)

            self.engine.event.emit(
                "workspace.updated",
                workspace
            )

            return workspace

        return None

    def archive(self, workspace_id):
        return self.update_record(
            workspace_id,
            status="archived"
        )

    def current(self):
        return self.get_by_slug(
            self.engine.context.workspace_id()
        )

    def validate(self):
        records = self.records()
        errors = []

        for index, workspace in enumerate(records):
            result = self.validate_record(workspace)

            for error in result["errors"]:
                errors.append(
                    f"Record {index}: {error}"
                )

        return {
            "valid": not errors,
            "count": len(records),
            "errors": errors,
        }

    def snapshot(self):
        return {
            "organization_id": (
                self.engine.context.organization_id()
            ),
            "workspace_id": (
                self.engine.context.workspace_id()
            ),
            "user_id": (
                self.engine.context.user_id()
            ),
            "validation": self.validate(),
            "workspaces": self.records(),
        }
