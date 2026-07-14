class BaseCommand:
    def __init__(self, engine):
        self.engine = engine

    @property
    def config(self):
        return self.engine.config

    @property
    def workspace(self):
        return self.engine.workspace

    @property
    def logger(self):
        return self.engine.logger

    @property
    def registry(self):
        return self.engine.registry

    @property
    def database(self):
        return self.engine.database

    def run(self, *args, **kwargs):
        raise NotImplementedError("Command must implement run()")
