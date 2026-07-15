import base64
import hashlib
import hmac
import secrets
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
    SECRET_DATABASE_NAME = "credential_secrets"

    PASSWORD_ALGORITHM = "pbkdf2_sha256"
    PASSWORD_DIGEST = "sha256"
    PASSWORD_ITERATIONS = 600_000
    PASSWORD_SALT_BYTES = 16
    PASSWORD_KEY_BYTES = 32

    PASSWORD_MIN_LENGTH = 12
    PASSWORD_MAX_LENGTH = 1024
    MAX_FAILED_ATTEMPTS = 5

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

    def records(self):
        return self.engine.database.load(
            self.DATABASE_NAME
        )

    def save_records(self, records):
        return self.engine.database.save(
            self.DATABASE_NAME,
            records
        )

    def secret_records(self):
        return self.engine.database.load(
            self.SECRET_DATABASE_NAME
        )

    def save_secret_records(self, records):
        return self.engine.database.save(
            self.SECRET_DATABASE_NAME,
            records
        )

    def list(self):
        return [
            self.public_record(record)
            for record in self.records()
        ]

    def count(self):
        return len(self.records())

    def next_id(self):
        return f"CRED-{uuid.uuid4()}"

    def normalize_type(self, value):
        return str(value or "").strip().lower()

    def normalize_status(self, value):
        return str(value or "").strip().lower()

    def password_policy(self):
        return {
            "min_length": self.PASSWORD_MIN_LENGTH,
            "max_length": self.PASSWORD_MAX_LENGTH,
            "algorithm": self.PASSWORD_ALGORITHM,
            "digest": self.PASSWORD_DIGEST,
            "iterations": self.PASSWORD_ITERATIONS,
            "salt_bytes": self.PASSWORD_SALT_BYTES,
            "key_bytes": self.PASSWORD_KEY_BYTES,
            "max_failed_attempts": (
                self.MAX_FAILED_ATTEMPTS
            ),
        }

    def validate_password(self, password):
        errors = []

        if not isinstance(password, str):
            errors.append(
                "Password must be a string"
            )
            return {
                "valid": False,
                "errors": errors,
            }

        length = len(password)

        if length < self.PASSWORD_MIN_LENGTH:
            errors.append(
                "Password is too short"
            )

        if length > self.PASSWORD_MAX_LENGTH:
            errors.append(
                "Password is too long"
            )

        return {
            "valid": not errors,
            "errors": errors,
        }

    def encode_bytes(self, value):
        return base64.urlsafe_b64encode(
            value
        ).decode("ascii")

    def decode_bytes(self, value):
        try:
            return base64.urlsafe_b64decode(
                str(value).encode("ascii")
            )
        except (
            ValueError,
            TypeError,
        ) as error:
            raise ValueError(
                "Invalid encoded credential value"
            ) from error

    def derive_password_key(
        self,
        password,
        *,
        salt,
        iterations=None,
    ):
        selected_iterations = int(
            iterations
            or self.PASSWORD_ITERATIONS
        )

        if selected_iterations < 1:
            raise ValueError(
                "Password iterations must be positive"
            )

        return hashlib.pbkdf2_hmac(
            self.PASSWORD_DIGEST,
            password.encode("utf-8"),
            salt,
            selected_iterations,
            dklen=self.PASSWORD_KEY_BYTES,
        )

    def hash_password(
        self,
        password,
        *,
        salt=None,
        iterations=None,
    ):
        validation = self.validate_password(
            password
        )

        if not validation["valid"]:
            raise ValueError(
                "; ".join(validation["errors"])
            )

        selected_salt = (
            salt
            if salt is not None
            else secrets.token_bytes(
                self.PASSWORD_SALT_BYTES
            )
        )

        if not isinstance(
            selected_salt,
            bytes,
        ):
            raise TypeError(
                "Password salt must be bytes"
            )

        selected_iterations = int(
            iterations
            or self.PASSWORD_ITERATIONS
        )

        derived_key = self.derive_password_key(
            password,
            salt=selected_salt,
            iterations=selected_iterations,
        )

        return {
            "algorithm": self.PASSWORD_ALGORITHM,
            "digest": self.PASSWORD_DIGEST,
            "iterations": selected_iterations,
            "salt": self.encode_bytes(
                selected_salt
            ),
            "hash": self.encode_bytes(
                derived_key
            ),
        }

    def verify_password_hash(
        self,
        password,
        secret_record,
    ):
        if not isinstance(password, str):
            return False

        if not isinstance(secret_record, dict):
            return False

        if (
            secret_record.get("algorithm")
            != self.PASSWORD_ALGORITHM
        ):
            return False

        if (
            secret_record.get("digest")
            != self.PASSWORD_DIGEST
        ):
            return False

        try:
            salt = self.decode_bytes(
                secret_record.get("salt", "")
            )
            expected = self.decode_bytes(
                secret_record.get("hash", "")
            )
            iterations = int(
                secret_record.get(
                    "iterations",
                    0,
                )
            )

            if iterations < 1:
                return False

            actual = self.derive_password_key(
                password,
                salt=salt,
                iterations=iterations,
            )

        except (
            ValueError,
            TypeError,
        ):
            return False

        return hmac.compare_digest(
            actual,
            expected,
        )

    def get_secret(self, credential_id):
        selected_id = str(
            credential_id or ""
        ).strip()

        for record in self.secret_records():
            if (
                record.get("credential_id")
                == selected_id
            ):
                return dict(record)

        return None

    def save_secret(
        self,
        credential_id,
        secret_record,
    ):
        selected_id = str(
            credential_id or ""
        ).strip()

        if not selected_id:
            raise ValueError(
                "Credential ID is required"
            )

        records = self.secret_records()
        stored = {
            "credential_id": selected_id,
            **dict(secret_record),
        }

        for index, record in enumerate(records):
            if (
                record.get("credential_id")
                == selected_id
            ):
                records[index] = stored
                self.save_secret_records(
                    records
                )
                return dict(stored)

        records.append(stored)
        self.save_secret_records(records)

        return dict(stored)

    def delete_secret(self, credential_id):
        selected_id = str(
            credential_id or ""
        ).strip()

        records = self.secret_records()
        filtered = [
            record
            for record in records
            if (
                record.get("credential_id")
                != selected_id
            )
        ]

        if len(filtered) == len(records):
            return False

        self.save_secret_records(filtered)
        return True

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

    def get(self, credential_id):
        selected_id = str(
            credential_id or ""
        ).strip()

        for record in self.records():
            if record.get("id") == selected_id:
                return self.public_record(record)

        return None

    def get_by_user(
        self,
        user_id,
        *,
        credential_type=None,
    ):
        selected_user_id = str(
            user_id or ""
        ).strip()

        selected_type = (
            self.normalize_type(
                credential_type
            )
            if credential_type is not None
            else None
        )

        return [
            self.public_record(record)
            for record in self.records()
            if (
                record.get("user_id")
                == selected_user_id
            )
            and (
                selected_type is None
                or self.normalize_type(
                    record.get("type")
                ) == selected_type
            )
        ]

    def exists(self, credential_id):
        return self.get(
            credential_id
        ) is not None

    def create(self, data):
        source = dict(data or {})

        record = self.new_record(
            user_id=source.get("user_id"),
            credential_type=source.get(
                "type",
                "password",
            ),
            organization_id=source.get(
                "organization_id"
            ),
            status=source.get(
                "status",
                "active",
            ),
            metadata=source.get(
                "metadata",
                {},
            ),
        )

        if source.get("id"):
            record["id"] = str(
                source["id"]
            ).strip()

        validation = self.validate_record(
            record
        )

        if not validation["valid"]:
            raise ValueError(
                "; ".join(validation["errors"])
            )

        if self.exists(record["id"]):
            return None

        duplicate = self.get_by_user(
            record["user_id"],
            credential_type=record["type"],
        )

        if duplicate:
            return None

        records = self.records()
        records.append(record)
        self.save_records(records)

        emitter = getattr(
            self.engine,
            "event",
            None,
        )

        if emitter is not None:
            emitter.emit(
                "authentication.credential_created",
                self.public_record(record),
            )

        return self.public_record(record)

    def update(
        self,
        credential_id,
        **fields,
    ):
        forbidden = sorted(
            field
            for field in fields
            if field in self.SECRET_FIELDS
        )

        if forbidden:
            raise ValueError(
                "Secret fields are not allowed: "
                + ", ".join(forbidden)
            )

        immutable = {
            "id",
            "organization_id",
            "user_id",
            "type",
            "created_at",
        }

        attempted_immutable = sorted(
            field
            for field in fields
            if field in immutable
        )

        if attempted_immutable:
            raise ValueError(
                "Immutable fields cannot be updated: "
                + ", ".join(attempted_immutable)
            )

        records = self.records()

        for record in records:
            if record.get("id") != credential_id:
                continue

            record.update(fields)
            record["version"] = (
                record.get("version", 0) + 1
            )
            record["updated_at"] = (
                self.engine.now()
            )

            validation = self.validate_record(
                record
            )

            if not validation["valid"]:
                raise ValueError(
                    "; ".join(validation["errors"])
                )

            self.save_records(records)

            emitter = getattr(
                self.engine,
                "event",
                None,
            )

            if emitter is not None:
                emitter.emit(
                    "authentication.credential_updated",
                    self.public_record(record),
                )

            return self.public_record(record)

        return None

    def set_password(
        self,
        credential_id,
        password,
    ):
        credential = self.get(
            credential_id
        )

        if credential is None:
            raise KeyError(
                f"Unknown credential: {credential_id}"
            )

        if credential.get("type") != "password":
            raise ValueError(
                "Credential type does not support passwords"
            )

        secret_record = self.hash_password(
            password
        )

        self.save_secret(
            credential_id,
            secret_record,
        )

        updated = self.update(
            credential_id,
            status="active",
            failed_attempts=0,
            locked_until=None,
            metadata={
                **credential.get(
                    "metadata",
                    {},
                ),
                "password_configured": True,
            },
        )

        emitter = getattr(
            self.engine,
            "event",
            None,
        )

        if emitter is not None:
            emitter.emit(
                "authentication.password_set",
                self.public_record(updated),
            )

        return updated

    def verify_password(
        self,
        credential_id,
        password,
    ):
        credential = self.get(
            credential_id
        )

        if credential is None:
            return False

        if not self.can_authenticate(
            credential
        ):
            return False

        secret_record = self.get_secret(
            credential_id
        )

        if secret_record is None:
            return False

        verified = self.verify_password_hash(
            password,
            secret_record,
        )

        if verified:
            self.update(
                credential_id,
                failed_attempts=0,
                last_authenticated_at=(
                    self.engine.now()
                ),
            )

            return True

        attempts = (
            credential.get(
                "failed_attempts",
                0,
            )
            + 1
        )

        fields = {
            "failed_attempts": attempts,
        }

        if (
            attempts
            >= self.MAX_FAILED_ATTEMPTS
        ):
            fields["status"] = "locked"

        self.update(
            credential_id,
            **fields,
        )

        return False

    def change_password(
        self,
        credential_id,
        current_password,
        new_password,
    ):
        if not self.verify_password(
            credential_id,
            current_password,
        ):
            raise InvalidCredentialError(
                "Invalid current password",
                details={
                    "credential_id": (
                        credential_id
                    ),
                },
            )

        return self.set_password(
            credential_id,
            new_password,
        )

    def revoke(self, credential_id):
        credential = self.update(
            credential_id,
            status="revoked",
        )

        if credential is None:
            return None

        self.delete_secret(
            credential_id
        )

        return credential

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
        errors = []

        for index, record in enumerate(
            self.records()
        ):
            result = self.validate_record(
                record
            )

            for error in result["errors"]:
                errors.append(
                    f"Record {index}: {error}"
                )

        return {
            "valid": not errors,
            "count": self.count(),
            "credential_types": sorted(
                self.CREDENTIAL_TYPES
            ),
            "statuses": sorted(
                self.STATUSES
            ),
            "database": self.DATABASE_NAME,
            "secret_database": (
                self.SECRET_DATABASE_NAME
            ),
            "password_policy": (
                self.password_policy()
            ),
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
        }
