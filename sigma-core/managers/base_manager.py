class BaseManager:

    def __init__(self, engine):
        self.engine = engine

    @property
    def root(self):
        return self.engine.root

    @property
    def database(self):
        return self.engine.database

    @property
    def projects(self):
        return self.engine.projects_dir
