"""
Contrat applicatif transport-agnostique des devices Sigma.

Cette étape expose uniquement des opérations de consultation.
Aucun secret matériel, certificat ou token n'est créé.
"""

import importlib.util
from pathlib import Path

ROOT = Path.cwd()

spec = importlib.util.spec_from_file_location(
    "engine",
    ROOT / "sigma-core/engine.py",
)

engine_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine_module)


def success(data, *, status=200):
    return {
        "ok": True,
        "status": status,
        "data": data,
        "error": None,
    }


def failure(
    code,
    message,
    *,
    status=400,
    details=None,
):
    return {
        "ok": False,
        "status": status,
        "data": None,
        "error": {
            "code": str(code),
            "message": str(message),
            "retryable": False,
            "details": dict(details or {}),
        },
    }


def manager():
    return engine_module.engine.device


def serialize_device(device):
    if device is None:
        return None

    if hasattr(device, "as_dict"):
        return device.as_dict()

    if isinstance(device, dict):
        return dict(device)

    raise TypeError(
        "Unsupported device representation"
    )


def status():
    return success(
        manager().snapshot()
    )


def validate():
    result = manager().validate()

    return success(
        result,
        status=200 if result.get("valid") else 503,
    )


def list_devices(
    *,
    user_id=None,
    organization_id=None,
    workspace_id=None,
    device_type=None,
    state=None,
):
    if any(
        value is not None
        for value in (
            user_id,
            organization_id,
            workspace_id,
            device_type,
            state,
        )
    ):
        records = manager().find(
            user_id=user_id,
            organization_id=organization_id,
            workspace_id=workspace_id,
            device_type=device_type,
            state=state,
        )
    else:
        records = manager().list()

    return success(
        [
            serialize_device(device)
            for device in records
        ]
    )


def get_device(device_id):
    selected = str(
        device_id or ""
    ).strip()

    if not selected:
        return failure(
            "SIGMA_DEVICE_INVALID_REQUEST",
            "Device ID is required",
            status=400,
        )

    device = manager().get(selected)

    if device is None:
        return failure(
            "SIGMA_DEVICE_NOT_FOUND",
            "Device not found",
            status=404,
            details={
                "device_id": selected,
            },
        )

    return success(
        serialize_device(device)
    )
