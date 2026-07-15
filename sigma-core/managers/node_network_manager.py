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




from datetime import datetime
from dataclasses import field


@dataclass(frozen=True)
class NodeNetworkPolicy:
    allow_cluster_join: bool = True
    allow_remote_management: bool = True
    require_tls: bool = False

    def create_node(
        self,
        node,
    ):
        return self.repository.create(node)

    def get(self, node_id):
        return self.repository.get(
            str(node_id).strip()
        )

    def exists(self, node_id):
        return self.repository.exists(
            str(node_id).strip()
        )

    def list(self):
        return self.repository.list()

    def count(self):
        return self.repository.count()

    def delete(self, node_id):
        return self.repository.delete(
            str(node_id).strip()
        )

    def find(
        self,
        *,
        role=None,
        state=None,
        hostname=None,
    ):
        return self.repository.find(
            role=role,
            state=state,
            hostname=hostname,
        )

    def validate(self):

        return {
            "valid": True,
            "errors": [],
        }


@dataclass(frozen=True)
class Node:
    id: str
    role: str
    state: str
    hostname: str
    address: str
    created_at: str
    updated_at: str
    metadata: dict = field(default_factory=dict)
    version: int = 1

    def as_dict(self):
        return asdict(self)



class NodeRepository:

    def __init__(self):
        self._nodes = {}

    def create(self, node):
        if node.id in self._nodes:
            return None

        self._nodes[node.id] = node
        return node

    def get(self, node_id):
        return self._nodes.get(node_id)

    def exists(self, node_id):
        return node_id in self._nodes

    def replace(self, node):
        if node.id not in self._nodes:
            return None

        self._nodes[node.id] = node
        return node

    def delete(self, node_id):
        return self._nodes.pop(node_id, None)

    def list(self):
        return list(self._nodes.values())

    def count(self):
        return len(self._nodes)


    def find(
        self,
        *,
        role=None,
        state=None,
        hostname=None,
    ):
        nodes = self.list()

        filters = {
            "role": role,
            "state": state,
            "hostname": hostname,
        }

        for field, expected in filters.items():
            if expected is None:
                continue

            expected = str(expected).strip().lower()

            nodes = [
                node
                for node in nodes
                if str(getattr(node, field, "")).strip().lower() == expected
            ]

        return nodes


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
        self.repository = NodeRepository()

    def now(self):
        if hasattr(self.engine, "now"):
            return self.engine.now()
        return datetime.utcnow().isoformat()

    def default_policy(self):
        return NodeNetworkPolicy()

    def new_node(
        self,
        *,
        node_id,
        role,
        hostname="unknown",
        address="0.0.0.0",
        metadata=None,
        state=NodeState.ONLINE.value,
    ):
        now = self.now()

        return Node(
            id=node_id,
            role=str(role).strip().lower(),
            state=str(state).strip().lower(),
            hostname=str(hostname),
            address=str(address),
            created_at=now,
            updated_at=now,
            metadata=dict(metadata or {}),
        )


    def create_node(self, node):
        return self.repository.create(node)

    def get(self, node_id):
        return self.repository.get(str(node_id).strip())

    def exists(self, node_id):
        return self.repository.exists(str(node_id).strip())

    def list(self):
        return self.repository.list()

    def count(self):
        return self.repository.count()

    def delete(self, node_id):
        return self.repository.delete(str(node_id).strip())

    def find(
        self,
        *,
        role=None,
        state=None,
        hostname=None,
    ):
        return self.repository.find(
            role=role,
            state=state,
            hostname=hostname,
        )

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
