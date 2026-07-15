from dataclasses import asdict, dataclass
from enum import Enum


class DeviceError(Exception):
    """
    Erreur stable du domaine Device.
    """

    code = "SIGMA_DEVICE_ERROR"
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


class DeviceNotFoundError(DeviceError):
    code = "SIGMA_DEVICE_NOT_FOUND"


class DeviceAlreadyExistsError(DeviceError):
    code = "SIGMA_DEVICE_ALREADY_EXISTS"


class DeviceDisabledError(DeviceError):
    code = "SIGMA_DEVICE_DISABLED"


class DeviceRevokedError(DeviceError):
    code = "SIGMA_DEVICE_REVOKED"


class InvalidDeviceError(DeviceError):
    code = "SIGMA_DEVICE_INVALID"


class DeviceState(str, Enum):
    REGISTERED = "registered"
    TRUSTED = "trusted"
    DISABLED = "disabled"
    REVOKED = "revoked"


class DeviceType(str, Enum):
    PHONE = "phone"
    TABLET = "tablet"
    COMPUTER = "computer"
    SERVER = "server"
    VPS = "vps"
    RASPBERRY_PI = "raspberry_pi"
    IOT = "iot"
    GATEWAY = "gateway"
    RADIO = "radio"
    VIRTUAL = "virtual"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class DeviceEvent:
    device_id: str
    user_id: str
    organization_id: str
    occurred_at: str
    details: dict
    event_type: str

    def as_dict(self):
        return asdict(self)


@dataclass(frozen=True)
class DeviceRegistered(DeviceEvent):
    event_type: str = "device.registered"


@dataclass(frozen=True)
class DeviceTrusted(DeviceEvent):
    event_type: str = "device.trusted"


@dataclass(frozen=True)
class DeviceDisabled(DeviceEvent):
    event_type: str = "device.disabled"


@dataclass(frozen=True)
class DeviceRevoked(DeviceEvent):
    event_type: str = "device.revoked"




from datetime import datetime
from dataclasses import field


@dataclass(frozen=True)
class DeviceTrustPolicy:
    trusted: bool = False
    require_attestation: bool = False
    allow_remote_access: bool = True

    def validate(self):
        return {
            "valid": True,
            "errors": [],
        }


@dataclass(frozen=True)
class Device:
    id: str
    organization_id: str
    workspace_id: str
    user_id: str
    state: str
    device_type: str
    platform: str
    hostname: str
    created_at: str
    updated_at: str
    metadata: dict = field(default_factory=dict)
    version: int = 1

    def as_dict(self):
        return asdict(self)



class DeviceRepository:

    def __init__(self):
        self._devices = {}

    def create(self, device):
        if device.id in self._devices:
            return None

        self._devices[device.id] = device
        return device

    def get(self, device_id):
        return self._devices.get(device_id)

    def exists(self, device_id):
        return device_id in self._devices

    def delete(self, device_id):
        return self._devices.pop(
            device_id,
            None,
        )

    def list(self):
        return list(
            self._devices.values()
        )

    def count(self):
        return len(
            self._devices
        )

    def find(
        self,
        *,
        user_id=None,
        organization_id=None,
        workspace_id=None,
        device_type=None,
        state=None,
    ):
        devices = self.list()

        filters = {
            "user_id": user_id,
            "organization_id": organization_id,
            "workspace_id": workspace_id,
            "device_type": device_type,
            "state": state,
        }

        for field, expected in filters.items():
            if expected is None:
                continue

            selected = str(expected).strip().lower()

            devices = [
                device
                for device in devices
                if str(
                    getattr(device, field, "")
                    or ""
                ).strip().lower() == selected
            ]

        return devices

    def replace(self, device):
        if device.id not in self._devices:
            return None

        self._devices[device.id] = device
        return device


class DeviceManager:
    """
    Contrats initiaux du domaine Device Sigma.

    Cette étape ne contient encore :

    - aucune persistance ;
    - aucune association automatique aux sessions ;
    - aucun secret matériel ;
    - aucun certificat ;
    - aucune communication réseau ;
    - aucune gestion distante.
    """

    STATES = {
        state.value
        for state in DeviceState
    }

    TYPES = {
        device_type.value
        for device_type in DeviceType
    }

    EVENT_TYPES = {
        "device.registered",
        "device.trusted",
        "device.disabled",
        "device.revoked",
    }

    def __init__(self, engine):
        self.engine = engine
        self.repository = (
            DeviceRepository()
        )

    def now(self):
        if hasattr(self.engine, "now"):
            return self.engine.now()
        return datetime.utcnow().isoformat()

    def default_policy(self):
        return DeviceTrustPolicy()

    def new_device(
        self,
        *,
        device_id,
        organization_id,
        workspace_id,
        user_id,
        device_type,
        platform="unknown",
        hostname="unknown",
        metadata=None,
        state=DeviceState.REGISTERED.value,
    ):
        now = self.now()

        return Device(
            id=device_id,
            organization_id=organization_id,
            workspace_id=workspace_id,
            user_id=user_id,
            state=self.normalize_state(state),
            device_type=self.normalize_type(device_type),
            platform=str(platform),
            hostname=str(hostname),
            created_at=now,
            updated_at=now,
            metadata=dict(metadata or {}),
        )

    def create_device(
        self,
        device,
    ):
        return self.repository.create(
            device
        )

    def get(self, device_id):
        return self.repository.get(
            str(device_id or "").strip()
        )

    def exists(self, device_id):
        return self.repository.exists(
            str(device_id or "").strip()
        )

    def list(self):
        return self.repository.list()

    def count(self):
        return self.repository.count()

    def delete(self, device_id):
        return self.repository.delete(
            str(device_id or "").strip()
        )

    def find(
        self,
        *,
        user_id=None,
        organization_id=None,
        workspace_id=None,
        device_type=None,
        state=None,
    ):
        return self.repository.find(
            user_id=user_id,
            organization_id=organization_id,
            workspace_id=workspace_id,
            device_type=(
                self.normalize_type(device_type)
                if device_type is not None
                else None
            ),
            state=(
                self.normalize_state(state)
                if state is not None
                else None
            ),
        )

    def emit_event(
        self,
        event_class,
        device,
        *,
        details=None,
    ):
        event = event_class(
            device_id=device.id,
            user_id=device.user_id,
            organization_id=(
                device.organization_id
            ),
            occurred_at=self.now(),
            details=dict(details or {}),
        )

        emitter = getattr(
            self.engine,
            "event",
            None,
        )

        if emitter is not None:
            emitter.emit(
                event.event_type,
                event.as_dict(),
            )

        return event

    def register(
        self,
        *,
        device_id,
        organization_id,
        workspace_id,
        user_id,
        device_type,
        platform="unknown",
        hostname="unknown",
        metadata=None,
    ):
        if self.exists(device_id):
            raise DeviceAlreadyExistsError(
                "Device already exists",
                details={
                    "device_id": device_id,
                },
            )

        device = self.new_device(
            device_id=device_id,
            organization_id=organization_id,
            workspace_id=workspace_id,
            user_id=user_id,
            device_type=device_type,
            platform=platform,
            hostname=hostname,
            metadata=metadata,
        )

        created = self.create_device(
            device
        )

        if created is None:
            raise DeviceAlreadyExistsError(
                "Device already exists",
                details={
                    "device_id": device_id,
                },
            )

        self.emit_event(
            DeviceRegistered,
            created,
            details={
                "state": created.state,
                "device_type": (
                    created.device_type
                ),
            },
        )

        return created

    def update_state(
        self,
        device,
        state,
        *,
        reason=None,
    ):
        now = self.now()

        metadata = dict(
            device.metadata
        )

        if reason is not None:
            metadata[
                "state_change_reason"
            ] = str(reason)

        updated = Device(
            **{
                **device.as_dict(),
                "state": (
                    self.normalize_state(
                        state
                    )
                ),
                "updated_at": now,
                "metadata": metadata,
                "version": (
                    device.version + 1
                ),
            }
        )

        replaced = (
            self.repository.replace(
                updated
            )
        )

        if replaced is None:
            raise DeviceNotFoundError(
                "Device not found",
                details={
                    "device_id": device.id,
                },
            )

        return replaced

    def trust(self, device_id):
        device = self.get(device_id)

        if device is None:
            raise DeviceNotFoundError(
                "Device not found",
                details={
                    "device_id": device_id,
                },
            )

        if (
            device.state
            == DeviceState.REVOKED.value
        ):
            raise DeviceRevokedError(
                "Device is revoked",
                details={
                    "device_id": device_id,
                },
            )

        if (
            device.state
            == DeviceState.DISABLED.value
        ):
            raise DeviceDisabledError(
                "Device is disabled",
                details={
                    "device_id": device_id,
                },
            )

        if (
            device.state
            == DeviceState.TRUSTED.value
        ):
            return device

        trusted = self.update_state(
            device,
            DeviceState.TRUSTED,
        )

        self.emit_event(
            DeviceTrusted,
            trusted,
            details={
                "previous_state": (
                    device.state
                ),
            },
        )

        return trusted

    def disable(
        self,
        device_id,
        *,
        reason="disabled",
    ):
        device = self.get(device_id)

        if device is None:
            raise DeviceNotFoundError(
                "Device not found",
                details={
                    "device_id": device_id,
                },
            )

        if (
            device.state
            == DeviceState.REVOKED.value
        ):
            raise DeviceRevokedError(
                "Device is revoked",
                details={
                    "device_id": device_id,
                },
            )

        if (
            device.state
            == DeviceState.DISABLED.value
        ):
            return device

        disabled = self.update_state(
            device,
            DeviceState.DISABLED,
            reason=reason,
        )

        self.emit_event(
            DeviceDisabled,
            disabled,
            details={
                "previous_state": (
                    device.state
                ),
                "reason": str(reason),
            },
        )

        return disabled

    def revoke(
        self,
        device_id,
        *,
        reason="revoked",
    ):
        device = self.get(device_id)

        if device is None:
            raise DeviceNotFoundError(
                "Device not found",
                details={
                    "device_id": device_id,
                },
            )

        if (
            device.state
            == DeviceState.REVOKED.value
        ):
            return device

        revoked = self.update_state(
            device,
            DeviceState.REVOKED,
            reason=reason,
        )

        self.emit_event(
            DeviceRevoked,
            revoked,
            details={
                "previous_state": (
                    device.state
                ),
                "reason": str(reason),
            },
        )

        return revoked

    def normalize_state(self, value):

        if isinstance(value, DeviceState):
            return value.value

        return str(value or "").strip().lower()

    def normalize_type(self, value):
        if isinstance(value, DeviceType):
            return value.value

        return str(value or "").strip().lower()

    def state_exists(self, value):
        return (
            self.normalize_state(value)
            in self.STATES
        )

    def type_exists(self, value):
        return (
            self.normalize_type(value)
            in self.TYPES
        )

    def validate(self):
        return {
            "valid": True,
            "states": sorted(self.STATES),
            "types": sorted(self.TYPES),
            "event_types": sorted(
                self.EVENT_TYPES
            ),
            "errors": [],
        }

    def snapshot(self):
        return {
            "validation": self.validate(),
        }
