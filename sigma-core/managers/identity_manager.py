class IdentityManager:
    def __init__(self, engine):
        self.engine = engine

    def info(self):
        return self.engine.config.ensure_identity()

    def machine_id(self):
        return self.info()["machine_id"]

    def user_id(self):
        return self.info()["user_id"]

    def node_id(self):
        return self.info()["node_id"]
