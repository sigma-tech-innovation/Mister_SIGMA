from dataclasses import asdict, dataclass
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

    def normalize_state(self, value):
        if isinstance(value, SessionState):
            return value.value

        return str(value or "").strip().lower()

    def state_exists(self, value):
        return (
            self.normalize_state(value)
            in self.STATES
        )

    def validate(self):
        return {
            "valid": True,
            "states": sorted(self.STATES),
            "event_types": sorted(
                self.EVENT_TYPES
            ),
            "errors": [],
        }

    def snapshot(self):
        return {
            "validation": self.validate(),
        }
