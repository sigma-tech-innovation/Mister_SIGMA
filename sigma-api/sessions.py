"""
Contrat applicatif transport-agnostique des sessions Sigma.

Cette étape expose uniquement des opérations de consultation.
Aucun token, JWT ou secret n'est créé ou retourné.
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
    return engine_module.engine.session


def serialize_session(session):
    if session is None:
        return None

    if hasattr(session, "as_dict"):
        return session.as_dict()

    if isinstance(session, dict):
        return dict(session)

    raise TypeError(
        "Unsupported session representation"
    )


def status():
    return success(
        manager().snapshot()
    )


def validate():
    result = manager().validate()

    return success(
        result,
        status=(
            200
            if result.get("valid")
            else 503
        ),
    )


def list_sessions(
    *,
    user_id=None,
    organization_id=None,
    workspace_id=None,
    credential_id=None,
    device_id=None,
    state=None,
):
    if any(
        value is not None
        for value in (
            user_id,
            organization_id,
            workspace_id,
            credential_id,
            device_id,
            state,
        )
    ):
        records = manager().find(
            user_id=user_id,
            organization_id=organization_id,
            workspace_id=workspace_id,
            credential_id=credential_id,
            device_id=device_id,
            state=state,
        )
    else:
        records = manager().list()

    return success([
        serialize_session(record)
        for record in records
    ])


def get_session(session_id):
    selected_id = str(
        session_id or ""
    ).strip()

    if not selected_id:
        return failure(
            "SIGMA_SESSION_INVALID_REQUEST",
            "Session ID is required",
            status=400,
        )

    session = manager().get(
        selected_id
    )

    if session is None:
        return failure(
            "SIGMA_SESSION_NOT_FOUND",
            "Session not found",
            status=404,
            details={
                "session_id": selected_id,
            },
        )

    return success(
        serialize_session(session)
    )
