from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum


class SessionError(Exception):
    """
    Erreur stable du domaine Session.
    """

    code = "SIGMA_SESSION_ERROR"
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


class SessionNotFoundError(SessionError):
    code = "SIGMA_SESSION_NOT_FOUND"


class SessionExpiredError(SessionError):
    code = "SIGMA_SESSION_EXPIRED"


class SessionRevokedError(SessionError):
    code = "SIGMA_SESSION_REVOKED"


class SessionDisabledError(SessionError):
    code = "SIGMA_SESSION_DISABLED"


class InvalidSessionError(SessionError):
    code = "SIGMA_SESSION_INVALID"


class SessionState(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    DISABLED = "disabled"


@dataclass(frozen=True)
class SessionPolicy:
    absolute_ttl_seconds: int = 86400
    idle_ttl_seconds: int = 3600
    renewable: bool = True

    def validate(self):
        errors = []

        if (
            not isinstance(
                self.absolute_ttl_seconds,
                int,
            )
            or isinstance(
                self.absolute_ttl_seconds,
                bool,
            )
            or self.absolute_ttl_seconds < 1
        ):
            errors.append(
                "Absolute TTL must be a positive integer"
            )

        if (
            not isinstance(
                self.idle_ttl_seconds,
                int,
            )
            or isinstance(
                self.idle_ttl_seconds,
                bool,
            )
            or self.idle_ttl_seconds < 1
        ):
            errors.append(
                "Idle TTL must be a positive integer"
            )

        if (
            isinstance(
                self.absolute_ttl_seconds,
                int,
            )
            and isinstance(
                self.idle_ttl_seconds,
                int,
            )
            and self.idle_ttl_seconds
            > self.absolute_ttl_seconds
        ):
            errors.append(
                "Idle TTL cannot exceed absolute TTL"
            )

        return {
            "valid": not errors,
            "errors": errors,
        }

    def as_dict(self):
        return asdict(self)


@dataclass(frozen=True)
class Session:
    id: str
    organization_id: str
    workspace_id: str
    user_id: str
    credential_id: str
    state: str
    created_at: str
    updated_at: str
    expires_at: str
    idle_expires_at: str
    last_activity_at: str
    device_id: str | None = None
    revoked_at: str | None = None
    revoked_reason: str | None = None
    metadata: dict = field(
        default_factory=dict
    )
    version: int = 1

    def as_dict(self):
        return asdict(self)


@dataclass(frozen=True)
class SessionEvent:
    session_id: str
    user_id: str
    organization_id: str
    occurred_at: str
    details: dict
    event_type: str

    def as_dict(self):
        return asdict(self)


@dataclass(frozen=True)
class SessionCreated(SessionEvent):
    event_type: str = "session.created"


@dataclass(frozen=True)
class SessionRenewed(SessionEvent):
    event_type: str = "session.renewed"


@dataclass(frozen=True)
class SessionExpired(SessionEvent):
    event_type: str = "session.expired"


@dataclass(frozen=True)
class SessionRevoked(SessionEvent):
    event_type: str = "session.revoked"



class SessionRepository:

    def __init__(self):
        self._sessions = {}

    def create(self, session):
        if session.id in self._sessions:
            return None

        self._sessions[session.id] = session
        return session

    def get(self, session_id):
        return self._sessions.get(session_id)

    def exists(self, session_id):
        return session_id in self._sessions

    def delete(self, session_id):
        return self._sessions.pop(
            session_id,
            None,
        )

    def list(self):
        return list(
            self._sessions.values()
        )

    def count(self):
        return len(
            self._sessions
        )

    def find(
        self,
        *,
        user_id=None,
        organization_id=None,
        workspace_id=None,
        credential_id=None,
        device_id=None,
        state=None,
    ):
        sessions = self.list()

        filters = {
            "user_id": user_id,
            "organization_id": organization_id,
            "workspace_id": workspace_id,
            "credential_id": credential_id,
            "device_id": device_id,
            "state": state,
        }

        for field, expected in filters.items():
            if expected is None:
                continue

            selected = str(expected).strip()

            sessions = [
                session
                for session in sessions
                if str(
                    getattr(
                        session,
                        field,
                        "",
                    )
                    or ""
                ).strip() == selected
            ]

        return sessions

    def replace(self, session):
        if session.id not in self._sessions:
            return None

        self._sessions[session.id] = session
        return session


class SessionManager:
    """
    Contrats initiaux du domaine Session.

    Cette étape ne contient encore :
    - aucune persistance ;
    - aucun JWT ;
    - aucun refresh token ;
    - aucune dépendance HTTP ;
    - aucun accès PostgreSQL.
    """

    STATES = {
        state.value
        for state in SessionState
    }

    EVENT_TYPES = {
        "session.created",
        "session.renewed",
        "session.expired",
        "session.revoked",
    }

    def __init__(self, engine):
        self.engine = engine
        self.repository = (
            SessionRepository()
        )

    def create_session(self, session):
        validation = self.validate_session(
            session
        )

        if not validation["valid"]:
            raise InvalidSessionError(
                "Invalid session",
                details={
                    "errors": validation["errors"],
                },
            )

        return self.repository.create(
            session
        )

    def get(self, session_id):
        return self.repository.get(
            str(session_id or "").strip()
        )

    def exists(self, session_id):
        return self.repository.exists(
            str(session_id or "").strip()
        )

    def list(self):
        return self.repository.list()

    def count(self):
        return self.repository.count()

    def delete(self, session_id):
        return self.repository.delete(
            str(session_id or "").strip()
        )

    def find(
        self,
        *,
        user_id=None,
        organization_id=None,
        workspace_id=None,
        credential_id=None,
        device_id=None,
        state=None,
    ):
        selected_state = (
            self.normalize_state(state)
            if state is not None
            else None
        )

        return self.repository.find(
            user_id=user_id,
            organization_id=organization_id,
            workspace_id=workspace_id,
            credential_id=credential_id,
            device_id=device_id,
            state=selected_state,
        )

    def normalize_state(self, value):
        if isinstance(value, SessionState):
            return value.value

        return str(value or "").strip().lower()

    def now_utc(self):
        value = self.engine.now()

        if isinstance(value, datetime):
            current = value
        else:
            current = datetime.fromisoformat(
                str(value).replace(
                    "Z",
                    "+00:00",
                )
            )

        if current.tzinfo is None:
            current = current.replace(
                tzinfo=timezone.utc
            )

        return current.astimezone(
            timezone.utc
        )

    def format_datetime(self, value):
        return value.astimezone(
            timezone.utc
        ).isoformat()

    def parse_datetime(self, value):
        parsed = datetime.fromisoformat(
            str(value).replace(
                "Z",
                "+00:00",
            )
        )

        if parsed.tzinfo is None:
            parsed = parsed.replace(
                tzinfo=timezone.utc
            )

        return parsed.astimezone(
            timezone.utc
        )

    def default_policy(self):
        return SessionPolicy()

    def validate_policy(self, policy):
        if not isinstance(
            policy,
            SessionPolicy,
        ):
            return {
                "valid": False,
                "errors": [
                    "Session policy must be a SessionPolicy"
                ],
            }

        return policy.validate()

    def new_session(
        self,
        *,
        session_id,
        user_id,
        credential_id,
        organization_id,
        workspace_id,
        device_id=None,
        metadata=None,
        policy=None,
    ):
        selected_policy = (
            policy
            or self.default_policy()
        )

        validation = self.validate_policy(
            selected_policy
        )

        if not validation["valid"]:
            raise ValueError(
                "; ".join(
                    validation["errors"]
                )
            )

        now = self.now_utc()

        session = Session(
            id=str(
                session_id or ""
            ).strip(),
            organization_id=str(
                organization_id or ""
            ).strip(),
            workspace_id=str(
                workspace_id or ""
            ).strip(),
            user_id=str(
                user_id or ""
            ).strip(),
            credential_id=str(
                credential_id or ""
            ).strip(),
            device_id=(
                str(device_id).strip()
                if device_id is not None
                else None
            ),
            state=SessionState.ACTIVE.value,
            created_at=self.format_datetime(
                now
            ),
            updated_at=self.format_datetime(
                now
            ),
            expires_at=self.format_datetime(
                now
                + timedelta(
                    seconds=(
                        selected_policy
                        .absolute_ttl_seconds
                    )
                )
            ),
            idle_expires_at=self.format_datetime(
                now
                + timedelta(
                    seconds=(
                        selected_policy
                        .idle_ttl_seconds
                    )
                )
            ),
            last_activity_at=(
                self.format_datetime(now)
            ),
            metadata=dict(
                metadata or {}
            ),
            version=1,
        )

        result = self.validate_session(
            session
        )

        if not result["valid"]:
            raise ValueError(
                "; ".join(result["errors"])
            )

        return session

    def validate_session(self, session):
        errors = []

        if not isinstance(
            session,
            Session,
        ):
            return {
                "valid": False,
                "errors": [
                    "Session must be a Session instance"
                ],
            }

        required = {
            "id": session.id,
            "organization_id": (
                session.organization_id
            ),
            "workspace_id": (
                session.workspace_id
            ),
            "user_id": session.user_id,
            "credential_id": (
                session.credential_id
            ),
            "state": session.state,
            "created_at": (
                session.created_at
            ),
            "updated_at": (
                session.updated_at
            ),
            "expires_at": (
                session.expires_at
            ),
            "idle_expires_at": (
                session.idle_expires_at
            ),
            "last_activity_at": (
                session.last_activity_at
            ),
        }

        missing = sorted(
            key
            for key, value in required.items()
            if not value
        )

        if missing:
            errors.append(
                "Missing fields: "
                + ", ".join(missing)
            )

        if not self.state_exists(
            session.state
        ):
            errors.append(
                "Invalid session state"
            )

        if (
            not isinstance(
                session.version,
                int,
            )
            or isinstance(
                session.version,
                bool,
            )
            or session.version < 1
        ):
            errors.append(
                "Version must be a positive integer"
            )

        if not isinstance(
            session.metadata,
            dict,
        ):
            errors.append(
                "Metadata must be a dictionary"
            )

        try:
            created_at = self.parse_datetime(
                session.created_at
            )
            expires_at = self.parse_datetime(
                session.expires_at
            )
            idle_expires_at = self.parse_datetime(
                session.idle_expires_at
            )
        except ValueError:
            errors.append(
                "Invalid session datetime"
            )
        else:
            if expires_at <= created_at:
                errors.append(
                    "Absolute expiration must be after creation"
                )

            if idle_expires_at <= created_at:
                errors.append(
                    "Idle expiration must be after creation"
                )

            if idle_expires_at > expires_at:
                errors.append(
                    "Idle expiration cannot exceed absolute expiration"
                )

        return {
            "valid": not errors,
            "errors": errors,
        }


    def touch(
        self,
        session,
        *,
        at=None,
    ):
        current = (
            at
            if at is not None
            else self.now_utc()
        )

        if not hasattr(current, "tzinfo"):
            current = self.parse_datetime(current)

        policy = self.default_policy()

        updated = Session(
            **{
                **session.as_dict(),
                "updated_at": self.format_datetime(current),
                "last_activity_at": self.format_datetime(current),
                "idle_expires_at": self.format_datetime(
                    current + timedelta(
                        seconds=policy.idle_ttl_seconds
                    )
                ),
                "version": session.version + 1,
            }
        )

        self.repository.replace(updated)
        return updated

    def revoke(
        self,
        session,
        *,
        reason="revoked",
        at=None,
    ):
        current = (
            at
            if at is not None
            else self.now_utc()
        )

        if not hasattr(current, "tzinfo"):
            current = self.parse_datetime(current)

        revoked = Session(
            **{
                **session.as_dict(),
                "state": SessionState.REVOKED.value,
                "updated_at": self.format_datetime(current),
                "revoked_at": self.format_datetime(current),
                "revoked_reason": str(reason),
                "version": session.version + 1,
            }
        )

        self.repository.replace(revoked)
        return revoked

    def renew(
        self,
        session,
        *,
        policy=None,
        at=None,
    ):
        current = (
            at
            if at is not None
            else self.now_utc()
        )

        if not hasattr(current, "tzinfo"):
            current = self.parse_datetime(current)

        policy = policy or self.default_policy()

        renewed = Session(
            **{
                **session.as_dict(),
                "updated_at": self.format_datetime(current),
                "last_activity_at": self.format_datetime(current),
                "expires_at": self.format_datetime(
                    current + timedelta(
                        seconds=policy.absolute_ttl_seconds
                    )
                ),
                "idle_expires_at": self.format_datetime(
                    current + timedelta(
                        seconds=policy.idle_ttl_seconds
                    )
                ),
                "version": session.version + 1,
            }
        )

        self.repository.replace(renewed)
        return renewed

    def is_expired(
        self,
        session,
        *,
        at=None,
    ):
        current = (
            at
            if isinstance(at, datetime)
            else (
                self.parse_datetime(at)
                if at is not None
                else self.now_utc()
            )
        )

        absolute_expiration = (
            self.parse_datetime(
                session.expires_at
            )
        )
        idle_expiration = (
            self.parse_datetime(
                session.idle_expires_at
            )
        )

        return (
            current >= absolute_expiration
            or current >= idle_expiration
        )

    def state_exists(self, value):
        return (
            self.normalize_state(value)
            in self.STATES
        )

    def validate(self):
        policy = self.default_policy()
        policy_validation = (
            policy.validate()
        )

        return {
            "valid": (
                policy_validation["valid"]
            ),
            "states": sorted(self.STATES),
            "event_types": sorted(
                self.EVENT_TYPES
            ),
            "default_policy": (
                policy.as_dict()
            ),
            "errors": (
                policy_validation["errors"]
            ),
        }

    def snapshot(self):
        return {
            "validation": self.validate(),
        }
