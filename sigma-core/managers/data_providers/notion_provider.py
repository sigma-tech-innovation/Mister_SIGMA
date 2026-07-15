import json
import urllib.error
import urllib.request


class NotionProvider:
    """
    Connecteur Notion optionnel.

    Le transport HTTP peut être injecté pour les tests.
    Aucun appel réseau n'est effectué à l'initialisation.
    """

    provider_key = "notion"
    api_base_url = "https://api.notion.com/v1"
    api_version = "2022-06-28"

    def __init__(
        self,
        token="",
        database_id="",
        transport=None,
    ):
        self.token = str(token or "").strip()
        self.database_id = str(
            database_id or ""
        ).strip()
        self.transport = (
            transport or self._http_request
        )

    def configuration(self):
        return {
            "token_configured": bool(self.token),
            "database_id": self.database_id,
            "api_base_url": self.api_base_url,
            "api_version": self.api_version,
        }

    def validate(self):
        errors = []

        if not self.token:
            errors.append(
                "Notion token is missing"
            )

        if not self.database_id:
            errors.append(
                "Notion database ID is missing"
            )

        return {
            "valid": not errors,
            "provider": self.provider_key,
            "errors": errors,
        }

    def headers(self):
        return {
            "Authorization": (
                f"Bearer {self.token}"
            ),
            "Notion-Version": self.api_version,
            "Content-Type": "application/json",
        }

    def _http_request(
        self,
        method,
        path,
        payload=None,
    ):
        url = (
            self.api_base_url
            + "/"
            + path.lstrip("/")
        )

        body = None

        if payload is not None:
            body = json.dumps(payload).encode(
                "utf-8"
            )

        request = urllib.request.Request(
            url=url,
            data=body,
            headers=self.headers(),
            method=method,
        )

        try:
            with urllib.request.urlopen(
                request,
                timeout=30,
            ) as response:
                content = response.read().decode(
                    "utf-8"
                )

        except urllib.error.HTTPError as error:
            detail = error.read().decode(
                "utf-8",
                errors="replace",
            )

            raise RuntimeError(
                "Notion API request failed: "
                f"{error.code} {detail}"
            ) from error

        if not content:
            return {}

        return json.loads(content)

    def request(
        self,
        method,
        path,
        payload=None,
    ):
        validation = self.validate()

        if not validation["valid"]:
            raise RuntimeError(
                "; ".join(validation["errors"])
            )

        return self.transport(
            method,
            path,
            payload,
        )

    def list_resources(self):
        return [
            self.database_id
        ] if self.database_id else []

    def pull(self, resource=None):
        database_id = (
            resource or self.database_id
        )

        return self.request(
            "POST",
            f"databases/{database_id}/query",
            {},
        )

    def push(
        self,
        resource,
        records,
    ):
        database_id = (
            resource or self.database_id
        )

        results = []

        for record in records:
            payload = {
                "parent": {
                    "database_id": database_id,
                },
                "properties": record,
            }

            results.append(
                self.request(
                    "POST",
                    "pages",
                    payload,
                )
            )

        return results

    def snapshot(self):
        return {
            "provider": self.provider_key,
            "configuration": (
                self.configuration()
            ),
            "validation": self.validate(),
            "resources": self.list_resources(),
        }
