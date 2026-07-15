from dataclasses import asdict, dataclass
from enum import Enum


class NodeError(Exception):
    code = "SIGMA_NODE_ERROR"
    retryable = False

    def __init__(self, message, *, details=None):
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


class NodeNotFoundError(NodeError):
    code = "SIGMA_NODE_NOT_FOUND"


class NodeAlreadyExistsError(NodeError):
    code = "SIGMA_NODE_ALREADY_EXISTS"


class InvalidNodeError(NodeError):
    code = "SIGMA_NODE_INVALID"


class NodeState(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"


class NodeRole(str, Enum):
    CORE = "core"
    EDGE = "edge"
    WORKER = "worker"
    GATEWAY = "gateway"


@dataclass(frozen=True)
class NodeEvent:
    node_id: str
    occurred_at: str
    details: dict
    event_type: str

    def as_dict(self):
        return asdict(self)


@dataclass(frozen=True)
class NodeRegistered(NodeEvent):
    event_type: str = "node.registered"


@dataclass(frozen=True)
class NodeDisconnected(NodeEvent):
    event_type: str = "node.disconnected"


class NodeNetworkManager:

    STATES = {
        state.value
        for state in NodeState
    }

    ROLES = {
        role.value
        for role in NodeRole
    }

    EVENT_TYPES = {
        "node.registered",
        "node.disconnected",
    }

    def __init__(self, engine):
        self.engine = engine

    def validate(self):
        return {
            "valid": True,
            "states": sorted(self.STATES),
            "roles": sorted(self.ROLES),
            "event_types": sorted(self.EVENT_TYPES),
            "errors": [],
        }

    def snapshot(self):
        return {
            "validation": self.validate(),
        }
