import uuid


class UserManager:
    """
    Gestionnaire des utilisateurs Sigma.

    Source locale transitoire.
    PostgreSQL deviendra ensuite la source de vérité.
    """

    DATABASE_NAME = "users"

    REQUIRED_FIELDS = {
        "id",
        "organization_id",
        "email",
        "username",
        "display_name",
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
        return f"USER-{uuid.uuid4()}"

    def get(self, user_id):
        for user in self.records():
            if user.get("id") == user_id:
                return user
        return None

    def exists(self, user_id):
        return self.get(user_id) is not None

    def get_by_email(self, email):
        email = str(email).strip().lower()

        for user in self.records():
            if (
                str(user.get("email", "")).lower()
                == email
            ):
                return user

        return None

    def get_by_username(self, username):
        username = str(username).strip().lower()

        for user in self.records():
            if (
                str(user.get("username", "")).lower()
                == username
            ):
                return user

        return None

    def validate_record(self, user):
        errors = []

        missing = sorted(
            field
            for field in self.REQUIRED_FIELDS
            if not user.get(field)
        )

        if missing:
            errors.append(
                "Missing fields: "
                + ", ".join(missing)
            )

        if (
            user.get("status")
            not in self.STATUSES
        ):
            errors.append(
                "Invalid status"
            )

        return {
            "valid": not errors,
            "errors": errors,
        }

    def create(self, data):
        user = dict(data)

        user.setdefault(
            "id",
            self.next_id()
        )

        user.setdefault(
            "organization_id",
            self.engine.context.organization_id()
        )

        user.setdefault(
            "status",
            "active"
        )

        user.setdefault(
            "created_at",
            self.engine.now()
        )

        user["updated_at"] = (
            self.engine.now()
        )

        validation = self.validate_record(user)

        if not validation["valid"]:
            raise ValueError(
                "; ".join(validation["errors"])
            )

        if self.get(user["id"]):
            return None

        if self.get_by_email(user["email"]):
            return None

        if self.get_by_username(
            user["username"]
        ):
            return None

        records = self.records()
        records.append(user)
        self.save_records(records)

        self.engine.event.emit(
            "user.created",
            user
        )

        return user

    def update(
        self,
        user_id,
        **fields
    ):
        records = self.records()

        for user in records:

            if user["id"] != user_id:
                continue

            user.update(fields)

            user["updated_at"] = (
                self.engine.now()
            )

            validation = self.validate_record(
                user
            )

            if not validation["valid"]:
                raise ValueError(
                    "; ".join(validation["errors"])
                )

            self.save_records(records)

            self.engine.event.emit(
                "user.updated",
                user
            )

            return user

        return None


    def validate(self):
        errors = []

        for index, user in enumerate(self.records()):
            result = self.validate_record(user)

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
            "user_id": (
                self.engine.context.user_id()
            ),
            "validation": self.validate(),
            "users": self.records(),
        }
