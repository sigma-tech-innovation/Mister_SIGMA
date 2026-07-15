"""
Contrat applicatif de l'API Authentication Sigma.

Ce module ne dépend d'aucun framework HTTP. Il expose des fonctions
transport-agnostiques qui pourront être utilisées ultérieurement par
un routeur HTTP, WebSocket, RPC ou tout autre adaptateur.

Aucune fonction ne crée de session ou de token.
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
    retryable=False,
    details=None,
):
    return {
        "ok": False,
        "status": status,
        "data": None,
        "error": {
            "code": str(code),
            "message": str(message),
            "retryable": bool(retryable),
            "details": dict(details or {}),
        },
    }


def manager():
    return engine_module.engine.authentication


def sanitize_response(value):
    forbidden_fragments = {
        "password",
        "secret",
        "token",
        "hash",
        "salt",
        "api_key",
        "authorization",
    }

    if isinstance(value, dict):
        result = {}

        for key, item in value.items():
            normalized_key = str(
                key
            ).strip().lower()

            if any(
                fragment in normalized_key
                for fragment in forbidden_fragments
            ):
                continue

            result[str(key)] = sanitize_response(
                item
            )

        return result

    if isinstance(value, list):
        return [
            sanitize_response(item)
            for item in value
        ]

    if isinstance(value, tuple):
        return [
            sanitize_response(item)
            for item in value
        ]

    if isinstance(
        value,
        (
            str,
            int,
            float,
            bool,
        ),
    ) or value is None:
        return value

    return str(value)


def status():
    return success(
        sanitize_response(
            manager().snapshot()
        )
    )


def validate():
    result = sanitize_response(
        manager().validate()
    )

    return success(
        result,
        status=(
            200
            if result.get("valid")
            else 503
        ),
    )


def policy():
    return success(
        sanitize_response(
            manager().password_policy()
        )
    )


def list_credentials():
    return success(
        sanitize_response(
            manager().list()
        )
    )


def get_credential(credential_id):
    record = manager().get(
        credential_id
    )

    if record is None:
        return failure(
            "SIGMA_AUTH_CREDENTIAL_NOT_FOUND",
            "Credential not found",
            status=404,
            details={
                "credential_id": str(
                    credential_id or ""
                ),
            },
        )

    return success(
        sanitize_response(record)
    )


def list_audit(
    *,
    credential_id=None,
    user_id=None,
):
    records = manager().list_audit(
        credential_id=credential_id,
        user_id=user_id,
    )

    return success(
        sanitize_response(records)
    )


def authenticate(payload, *, context=None):
    if not isinstance(payload, dict):
        return failure(
            "SIGMA_AUTH_INVALID_REQUEST",
            "Authentication payload must be an object",
            status=400,
        )

    credential_id = str(
        payload.get(
            "credential_id",
            "",
        )
    ).strip()

    password = payload.get("password")

    if not credential_id:
        return failure(
            "SIGMA_AUTH_INVALID_REQUEST",
            "Credential ID is required",
            status=400,
        )

    if not isinstance(password, str):
        return failure(
            "SIGMA_AUTH_INVALID_REQUEST",
            "Password is required",
            status=400,
        )

    authentication = manager()

    try:
        result = authentication.authenticate(
            credential_id,
            password,
            context=context,
        )

    except Exception as error:
        if hasattr(error, "as_dict"):
            contract = error.as_dict()

            status_code = {
                "SIGMA_AUTH_INVALID_CREDENTIAL": 401,
                "SIGMA_AUTH_CREDENTIAL_DISABLED": 403,
                "SIGMA_AUTH_CREDENTIAL_LOCKED": 423,
            }.get(
                contract.get("code"),
                400,
            )

            return failure(
                contract.get(
                    "code",
                    "SIGMA_AUTHENTICATION_ERROR",
                ),
                contract.get(
                    "message",
                    "Authentication failed",
                ),
                status=status_code,
                retryable=contract.get(
                    "retryable",
                    False,
                ),
                details=sanitize_response(
                    contract.get(
                        "details",
                        {},
                    )
                ),
            )

        raise

    return success(
        sanitize_response(result),
        status=200,
    )


def create_credential(payload):
    if not isinstance(payload, dict):
        return failure(
            "SIGMA_AUTH_INVALID_REQUEST",
            "Credential payload must be an object",
            status=400,
        )

    allowed = {
        "id",
        "organization_id",
        "user_id",
        "type",
        "status",
        "metadata",
    }

    unexpected = sorted(
        key
        for key in payload
        if key not in allowed
    )

    if unexpected:
        return failure(
            "SIGMA_AUTH_INVALID_REQUEST",
            "Unsupported credential fields",
            status=400,
            details={
                "fields": unexpected,
            },
        )

    try:
        record = manager().create(
            payload
        )
    except ValueError as error:
        return failure(
            "SIGMA_AUTH_INVALID_CREDENTIAL_RECORD",
            str(error),
            status=400,
        )

    if record is None:
        return failure(
            "SIGMA_AUTH_CREDENTIAL_CONFLICT",
            "Credential already exists",
            status=409,
        )

    return success(
        sanitize_response(record),
        status=201,
    )


def revoke_credential(credential_id):
    record = manager().revoke(
        credential_id
    )

    if record is None:
        return failure(
            "SIGMA_AUTH_CREDENTIAL_NOT_FOUND",
            "Credential not found",
            status=404,
            details={
                "credential_id": str(
                    credential_id or ""
                ),
            },
        )

    return success(
        sanitize_response(record)
    )
