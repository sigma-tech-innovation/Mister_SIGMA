import uuid


class AuthenticationError(Exception):
    """
    Erreur stable du domaine d'authentification.
    """

    code = "SIGMA_AUTHENTICATION_ERROR"
    retryable = False

    def __init__(
        self,
        message,
        *,
        details=None,
    ):
        super().__init__(message)
        self.message = str(message)
        self.details = dict(details or {})

    def as_dict(self):
        return {
            "code": self.code,
            "message": self.message,
            "retryable": self.retryable,
            "details": dict(self.details),
        }


class InvalidCredentialError(AuthenticationError):
    code = "SIGMA_AUTH_INVALID_CREDENTIAL"
    retryable = False


class CredentialDisabledError(AuthenticationError):
    code = "SIGMA_AUTH_CREDENTIAL_DISABLED"
    retryable = False


class CredentialLockedError(AuthenticationError):
    code = "SIGMA_AUTH_CREDENTIAL_LOCKED"
    retryable = True


class AuthenticationManager:
    """
    Contrats du domaine d'authentification Sigma.

    Responsabilités de 4A :
    - modèle de credential ;
    - statuts et invariants ;
    - erreurs stables ;
    - représentation publique sans secret.

    Hors périmètre 4A :
    - persistance ;
    - hash de mot de passe ;
    - authentification effective ;
    - sessions ;
    - appareils ;
    - réplication.
    """

    DATABASE_NAME = "credentials"

    CREDENTIAL_TYPES = {
        "password",
        "api_key",
        "external",
    }

    STATUSES = {
        "active",
        "disabled",
        "locked",
        "revoked",
    }

    REQUIRED_FIELDS = {
        "id",
        "organization_id",
        "user_id",
        "type",
        "status",
        "version",
        "created_at",
        "updated_at",
    }

    PUBLIC_FIELDS = {
        "id",
        "organization_id",
        "user_id",
        "type",
        "status",
        "version",
        "created_at",
        "updated_at",
        "last_authenticated_at",
        "failed_attempts",
        "locked_until",
        "metadata",
    }

    SECRET_FIELDS = {
        "password",
        "password_hash",
        "secret",
        "secret_hash",
        "salt",
        "token",
        "api_key",
    }

    def __init__(self, engine):
        self.engine = engine

    def next_id(self):
        return f"CRED-{uuid.uuid4()}"

    def normalize_type(self, value):
        return str(value or "").strip().lower()

    def normalize_status(self, value):
        return str(value or "").strip().lower()

    def new_record(
        self,
        *,
        user_id,
        credential_type="password",
        organization_id=None,
        status="active",
        metadata=None,
    ):
        now = self.engine.now()

        record = {
            "id": self.next_id(),
            "organization_id": (
                organization_id
                or self.engine.context.organization_id()
            ),
            "user_id": str(user_id or "").strip(),
            "type": self.normalize_type(
                credential_type
            ),
            "status": self.normalize_status(
                status
            ),
            "version": 1,
            "created_at": now,
            "updated_at": now,
            "last_authenticated_at": None,
            "failed_attempts": 0,
            "locked_until": None,
            "metadata": dict(metadata or {}),
        }

        result = self.validate_record(record)

        if not result["valid"]:
            raise ValueError(
                "; ".join(result["errors"])
            )

        return record

    def validate_record(self, record):
        errors = []

        if not isinstance(record, dict):
            return {
                "valid": False,
                "errors": [
                    "Credential record must be a dictionary"
                ],
            }

        missing = sorted(
            field
            for field in self.REQUIRED_FIELDS
            if record.get(field) in (
                None,
                "",
            )
        )

        if missing:
            errors.append(
                "Missing fields: "
                + ", ".join(missing)
            )

        credential_type = self.normalize_type(
            record.get("type")
        )

        if (
            credential_type
            not in self.CREDENTIAL_TYPES
        ):
            errors.append(
                "Invalid credential type"
            )

        status = self.normalize_status(
            record.get("status")
        )

        if status not in self.STATUSES:
            errors.append(
                "Invalid credential status"
            )

        version = record.get("version")

        if (
            not isinstance(version, int)
            or isinstance(version, bool)
            or version < 1
        ):
            errors.append(
                "Version must be a positive integer"
            )

        failed_attempts = record.get(
            "failed_attempts",
            0,
        )

        if (
            not isinstance(failed_attempts, int)
            or isinstance(failed_attempts, bool)
            or failed_attempts < 0
        ):
            errors.append(
                "Failed attempts must be "
                "a non-negative integer"
            )

        metadata = record.get(
            "metadata",
            {},
        )

        if not isinstance(metadata, dict):
            errors.append(
                "Metadata must be a dictionary"
            )

        exposed_secrets = sorted(
            field
            for field in self.SECRET_FIELDS
            if field in record
        )

        if exposed_secrets:
            errors.append(
                "Secret fields are not allowed "
                "in the public credential record: "
                + ", ".join(exposed_secrets)
            )

        return {
            "valid": not errors,
            "errors": errors,
        }

    def public_record(self, record):
        """
        Retourne une représentation explicitement
        limitée aux champs publics.
        """
        return {
            field: record.get(field)
            for field in sorted(self.PUBLIC_FIELDS)
            if field in record
        }

    def is_active(self, record):
        return (
            self.normalize_status(
                record.get("status")
            )
            == "active"
        )

    def can_authenticate(self, record):
        result = self.validate_record(record)

        if not result["valid"]:
            return False

        return self.is_active(record)

    def validate(self):
        return {
            "valid": True,
            "credential_types": sorted(
                self.CREDENTIAL_TYPES
            ),
            "statuses": sorted(
                self.STATUSES
            ),
            "database": self.DATABASE_NAME,
            "errors": [],
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
        }
