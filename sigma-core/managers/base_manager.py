class BaseManager:
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
    def service(self):
        return self.engine.service

    @property
    def event(self):
        return self.engine.event

    @property
    def task(self):
        return self.engine.task

    @property
    def plugin(self):
        return self.engine.plugin

    @property
    def registry(self):
        return self.engine.registry

    @property
    def database(self):
        return self.engine.database
