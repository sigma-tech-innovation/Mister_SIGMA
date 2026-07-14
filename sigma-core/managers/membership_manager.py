import uuid


class MembershipManager:
    """
    Association User ↔ Organization ↔ Workspace ↔ Role.
    Source locale transitoire.
    """

    DATABASE_NAME = "memberships"

    REQUIRED_FIELDS = {
        "id",
        "organization_id",
        "workspace_id",
        "user_id",
        "role",
        "status",
    }

    STATUSES = {
        "active",
        "disabled",
        "archived",
    }

    def __init__(self, engine):
        self.engine = engine

    def records(self):
        return self.engine.database.load(
            self.DATABASE_NAME
        )

    def save_records(self, records):
        self.engine.database.save(
            self.DATABASE_NAME,
            records
        )

    def list(self):
        return self.records()

    def count(self):
        return len(self.records())

    def next_id(self):
        return f"MEM-{uuid.uuid4()}"

    def get(self, membership_id):
        for membership in self.records():
            if membership.get("id") == membership_id:
                return membership
        return None

    def exists(self, membership_id):
        return self.get(membership_id) is not None

    def validate_record(self, membership):
        errors = []

        missing = sorted(
            field
            for field in self.REQUIRED_FIELDS
            if not membership.get(field)
        )

        if missing:
            errors.append(
                "Missing fields: "
                + ", ".join(missing)
            )

        if membership.get("status") not in self.STATUSES:
            errors.append("Invalid status")

        if not self.engine.authorization.role_exists(
            membership.get("role")
        ):
            errors.append("Invalid role")

        return {
            "valid": not errors,
            "errors": errors,
        }

    def get_by_user(self, user_id):
        return [
            membership
            for membership in self.records()
            if membership.get("user_id") == user_id
        ]

    def get_by_workspace(self, workspace_id):
        return [
            membership
            for membership in self.records()
            if membership.get("workspace_id") == workspace_id
        ]

    def create(self, data):
        membership = dict(data)

        membership.setdefault(
            "id",
            self.next_id()
        )

        membership.setdefault(
            "organization_id",
            self.engine.context.organization_id()
        )

        membership.setdefault(
            "workspace_id",
            self.engine.context.workspace_id()
        )

        membership.setdefault(
            "status",
            "active"
        )

        membership.setdefault(
            "created_at",
            self.engine.now()
        )

        membership["updated_at"] = self.engine.now()

        validation = self.validate_record(
            membership
        )

        if not validation["valid"]:
            raise ValueError(
                "; ".join(validation["errors"])
            )

        records = self.records()
        records.append(membership)
        self.save_records(records)

        self.engine.event.emit(
            "membership.created",
            membership
        )

        return membership

    def update(
        self,
        membership_id,
        **fields
    ):
        records = self.records()

        for membership in records:

            if membership["id"] != membership_id:
                continue

            membership.update(fields)
            membership["updated_at"] = (
                self.engine.now()
            )

            validation = self.validate_record(
                membership
            )

            if not validation["valid"]:
                raise ValueError(
                    "; ".join(validation["errors"])
                )

            self.save_records(records)

            self.engine.event.emit(
                "membership.updated",
                membership
            )

            return membership

        return None


    def validate(self):
        errors = []

        for index, membership in enumerate(self.records()):
            result = self.validate_record(membership)

            for error in result["errors"]:
                errors.append(
                    f"Record {index}: {error}"
                )

        return {
            "valid": not errors,
            "count": self.count(),
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
            "memberships": self.records(),
        }
