class PluginManager:
    def __init__(self, engine):
        self.engine = engine
        self._plugins = {}

    def register(self, name, plugin):
        self._plugins[name] = plugin

    def get(self, name):
        return self._plugins.get(name)

    def list(self):
        return sorted(self._plugins.keys())
