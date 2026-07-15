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
