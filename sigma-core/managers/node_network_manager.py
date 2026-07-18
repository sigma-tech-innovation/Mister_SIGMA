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


@dataclass(frozen=True)
class NodeEndpoint:
    node_id: str
    protocol: str
    host: str
    port: int
    priority: int
    security: dict = field(default_factory=dict)
    status: str = "declared"

    def as_dict(self):
        return asdict(self)



@dataclass(frozen=True)
class NodeCapability:
    name: str
    version: str
    state: str = "declared"
    metadata: dict = field(default_factory=dict)

    def as_dict(self):
        return asdict(self)



@dataclass(frozen=True)
class NodeLink:
    source_node: str
    destination_node: str
    logical_cost: int
    latency: int
    priority: int
    status: str = "declared"
    metadata: dict = field(default_factory=dict)

    def as_dict(self):
        return asdict(self)



@dataclass(frozen=True)
class Zone:
    name: str
    kind: str
    metadata: dict = field(default_factory=dict)

    def as_dict(self):
        return asdict(self)



@dataclass(frozen=True)
class Region:
    name: str
    metadata: dict = field(default_factory=dict)

    def as_dict(self):
        return asdict(self)



@dataclass(frozen=True)
class TopologySnapshot:
    nodes: list = field(default_factory=list)
    links: list = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

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


    def new_endpoint(
        self,
        *,
        node_id,
        protocol,
        host,
        port,
        priority,
        security,
        status,
    ):
        node_id = str(node_id).strip()
        protocol = str(protocol).strip().lower()
        host = str(host).strip()
        status = str(status).strip().lower()

        if not node_id:
            raise InvalidNodeError("Invalid node_id")

        if not protocol:
            raise InvalidNodeError("Invalid protocol")

        if not host:
            raise InvalidNodeError("Invalid host")

        if not status:
            raise InvalidNodeError("Invalid status")

        if type(port) is not int or not (1 <= port <= 65535):
            raise InvalidNodeError("Invalid port")

        if type(priority) is not int or priority < 0:
            raise InvalidNodeError("Invalid priority")

        if not isinstance(security, dict):
            raise InvalidNodeError("Invalid security")

        return NodeEndpoint(
            node_id=node_id,
            protocol=protocol,
            host=host,
            port=port,
            priority=priority,
            security=dict(security),
            status=status,
        )


    def new_capability(
        self,
        name,
        version,
        state="declared",
        metadata=None,
    ):
        if metadata is None:
            metadata = {}

        return NodeCapability(
            name=name,
            version=version,
            state=state,
            metadata=dict(metadata),
        )



    def new_link(
        self,
        source_node,
        destination_node,
        logical_cost,
        latency,
        priority,
        status="declared",
        metadata=None,
    ):
        if metadata is None:
            metadata = {}

        return NodeLink(
            source_node=source_node,
            destination_node=destination_node,
            logical_cost=logical_cost,
            latency=latency,
            priority=priority,
            status=status,
            metadata=dict(metadata),
        )



    def new_zone(
        self,
        name,
        kind,
        metadata=None,
    ):
        if metadata is None:
            metadata = {}

        return Zone(
            name=name,
            kind=kind,
            metadata=dict(metadata),
        )



    def new_region(
        self,
        name,
        metadata=None,
    ):
        if metadata is None:
            metadata = {}

        return Region(
            name=name,
            metadata=dict(metadata),
        )



    def new_topology_snapshot(
        self,
        nodes=None,
        links=None,
        metadata=None,
    ):
        if nodes is None:
            nodes = []

        if links is None:
            links = []

        if metadata is None:
            metadata = {}

        return TopologySnapshot(
            nodes=list(nodes),
            links=list(links),
            metadata=dict(metadata),
        )



    def find_by_zone(
        self,
        zone_name,
    ):
        return []



    def find_by_region(
        self,
        region_name,
    ):
        return []



    def find_by_capability(
        self,
        capability_name,
    ):
        return []



    def find_by_endpoint(
        self,
        endpoint_name,
    ):
        return []



    def find_incoming_links(
        self,
        node_id,
    ):
        return []



    def find_outgoing_links(
        self,
        node_id,
    ):
        return []



    def validate_duplicate_node_ids(
        self,
    ):
        raise NotImplementedError



    def validate_duplicate_endpoint_ids(
        self,
    ):
        raise NotImplementedError



    def validate_duplicate_link_ids(
        self,
    ):
        raise NotImplementedError



    def validate_duplicate_zone_ids(
        self,
    ):
        raise NotImplementedError


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



    def register(self, node):
        created = self.repository.create(node)

        if created is None:
            raise NodeAlreadyExistsError(
                "Node already exists",
                details={"node_id": node.id},
            )

        return created

    def disconnect(self, node_id):
        node = self.get(node_id)

        if node is None:
            raise NodeNotFoundError(
                "Node not found",
                details={"node_id": node_id},
            )

        updated = Node(
            id=node.id,
            role=node.role,
            state=NodeState.OFFLINE.value,
            hostname=node.hostname,
            address=node.address,
            created_at=node.created_at,
            updated_at=self.now(),
            metadata=dict(node.metadata),
            version=node.version + 1,
        )

        self.repository.replace(updated)
        return updated

    def maintenance(self, node_id):
        node = self.get(node_id)

        if node is None:
            raise NodeNotFoundError(
                "Node not found",
                details={"node_id": node_id},
            )

        updated = Node(
            id=node.id,
            role=node.role,
            state=NodeState.MAINTENANCE.value,
            hostname=node.hostname,
            address=node.address,
            created_at=node.created_at,
            updated_at=self.now(),
            metadata=dict(node.metadata),
            version=node.version + 1,
        )

        self.repository.replace(updated)
        return updated

    def reconnect(self, node_id):
        node = self.get(node_id)

        if node is None:
            raise NodeNotFoundError(
                "Node not found",
                details={"node_id": node_id},
            )

        updated = Node(
            id=node.id,
            role=node.role,
            state=NodeState.ONLINE.value,
            hostname=node.hostname,
            address=node.address,
            created_at=node.created_at,
            updated_at=self.now(),
            metadata=dict(node.metadata),
            version=node.version + 1,
        )

        self.repository.replace(updated)
        return updated
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
