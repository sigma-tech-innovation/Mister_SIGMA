class IdentityManager:
    """
    Interface officielle des identités Sigma.

    Identités globales :
    - organization_id
    - user_id
    - workspace_id

    Identités locales :
    - installation_id
    - machine_id
    - node_id

    ContextManager reste la source unifiée.
    """

    def __init__(self, engine):
        self.engine = engine

    def info(self):
        return self.engine.context.identity()

    def validate(self):
        identity = self.info()

        missing = [
            key
            for key, value in identity.items()
            if not value
        ]

        return {
            "valid": not missing,
            "missing": missing,
            "identity": identity,
        }

    def organization_id(self):
        return self.info()["organization_id"]

    def user_id(self):
        return self.info()["user_id"]

    def workspace_id(self):
        return self.info()["workspace_id"]

    def installation_id(self):
        return self.info()["installation_id"]

    def machine_id(self):
        return self.info()["machine_id"]

    def node_id(self):
        return self.info()["node_id"]
