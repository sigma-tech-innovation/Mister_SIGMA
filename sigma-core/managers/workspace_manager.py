class WorkspaceManager:
    def __init__(self, engine):
        self.engine = engine

    def root(self):
        return self.engine.root

    def path(self, *parts):
        return self.engine.root.joinpath(*parts)

    def exists(self, *parts):
        return self.path(*parts).exists()
