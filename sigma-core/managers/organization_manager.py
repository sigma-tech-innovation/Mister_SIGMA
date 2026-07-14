import re
import uuid


class OrganizationManager:
    """
    Gestionnaire des organisations Sigma.

    Version locale transitoire. PostgreSQL et Sigma API deviendront
    ensuite les sources de vérité centrales.
    """

    STATUSES = {
        "active",
        "suspended",
        "archived",
    }

    REQUIRED_FIELDS = {
        "id",
        "name",
        "slug",
        "owner_user_id",
        "status",
    }

    DATABASE_NAME = "organizations"

    def __init__(self, engine):
        self.engine = engine

    def records(self):
        return self.engine.database.load(
            self.DATABASE_NAME
        )

    def list(self):
        return self.records()

    def count(self):
        return len(self.records())

    def get(self, organization_id):
        for organization in self.records():
            if organization.get("id") == organization_id:
                return organization

        return None

    def get_by_slug(self, slug):
        normalized = self.normalize_slug(slug)

        for organization in self.records():
            if organization.get("slug") == normalized:
                return organization

        return None

    def exists(self, organization_id):
        return self.get(organization_id) is not None

    def slug_exists(self, slug):
        return self.get_by_slug(slug) is not None

    def normalize_slug(self, value):
        slug = str(value or "").strip().lower()
        slug = re.sub(r"[^a-z0-9]+", "-", slug)
        return slug.strip("-")

    def next_id(self):
        return f"ORG-{uuid.uuid4()}"

    def validate_record(self, organization):
        errors = []

        if not isinstance(organization, dict):
            return {
                "valid": False,
                "errors": [
                    "Organization must be a dictionary"
                ],
            }

        missing = sorted(
            field
            for field in self.REQUIRED_FIELDS
            if not organization.get(field)
        )

        if missing:
            errors.append(
                "Missing fields: "
                + ", ".join(missing)
            )

        status = organization.get("status")

        if status and status not in self.STATUSES:
            errors.append(
                f"Invalid status: {status}"
            )

        slug = organization.get("slug")

        if slug and slug != self.normalize_slug(slug):
            errors.append(
                "Slug is not normalized"
            )

        return {
            "valid": not errors,
            "errors": errors,
        }

    def create(self, data):
        if not isinstance(data, dict):
            raise TypeError(
                "Organization must be a dictionary"
            )

        organization = dict(data)

        organization.setdefault(
            "id",
            self.next_id()
        )

        organization["slug"] = self.normalize_slug(
            organization.get("slug")
            or organization.get("name")
        )

        organization.setdefault(
            "owner_user_id",
            self.engine.context.user_id()
        )

        organization.setdefault(
            "status",
            "active"
        )

        organization.setdefault(
            "description",
            ""
        )

        organization.setdefault(
            "metadata",
            {}
        )

        organization.setdefault(
            "created_at",
            self.engine.now()
        )

        organization["updated_at"] = (
            organization["created_at"]
        )

        validation = self.validate_record(
            organization
        )

        if not validation["valid"]:
            raise ValueError(
                "; ".join(validation["errors"])
            )

        if self.exists(organization["id"]):
            return None

        if self.slug_exists(organization["slug"]):
            return None

        records = self.records()
        records.append(organization)

        self.engine.database.save(
            self.DATABASE_NAME,
            records
        )

        self.engine.event.emit(
            "organization.created",
            organization
        )

        return organization

    def update(self, organization_id, **fields):
        records = self.records()

        for organization in records:
            if organization.get("id") != organization_id:
                continue

            if "slug" in fields:
                normalized = self.normalize_slug(
                    fields["slug"]
                )

                existing = self.get_by_slug(
                    normalized
                )

                if (
                    existing is not None
                    and existing.get("id")
                    != organization_id
                ):
                    return None

                fields["slug"] = normalized

            updated = {
                **organization,
                **fields,
                "updated_at": self.engine.now(),
            }

            validation = self.validate_record(
                updated
            )

            if not validation["valid"]:
                raise ValueError(
                    "; ".join(validation["errors"])
                )

            organization.clear()
            organization.update(updated)

            self.engine.database.save(
                self.DATABASE_NAME,
                records
            )

            self.engine.event.emit(
                "organization.updated",
                organization
            )

            return organization

        return None

    def set_status(
        self,
        organization_id,
        status
    ):
        if status not in self.STATUSES:
            raise ValueError(
                f"Invalid status: {status}"
            )

        return self.update(
            organization_id,
            status=status
        )

    def delete(self, organization_id):
        return self.set_status(
            organization_id,
            "archived"
        )

    def current(self):
        organization_id = (
            self.engine.context.organization_id()
        )

        return self.get(organization_id)

    def validate(self):
        records = self.records()
        errors = []
        ids = set()
        slugs = set()

        for index, organization in enumerate(
            records
        ):
            validation = self.validate_record(
                organization
            )

            for error in validation["errors"]:
                errors.append(
                    f"Record {index}: {error}"
                )

            organization_id = organization.get(
                "id"
            )
            slug = organization.get("slug")

            if organization_id in ids:
                errors.append(
                    f"Duplicate organization id: "
                    f"{organization_id}"
                )

            if slug in slugs:
                errors.append(
                    f"Duplicate organization slug: "
                    f"{slug}"
                )

            ids.add(organization_id)
            slugs.add(slug)

        return {
            "valid": not errors,
            "count": len(records),
            "errors": errors,
        }

    def snapshot(self):
        return {
            "current_organization_id": (
                self.engine.context.organization_id()
            ),
            "organizations": self.records(),
            "validation": self.validate(),
        }
