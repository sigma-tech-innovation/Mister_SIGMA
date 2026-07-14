class ServiceManager:
    def __init__(self, engine):
        self.engine = engine
        self._services = {}

    def register(self, name, service):
        self._services[name] = service

    def get(self, name):
        return self._services.get(name)

    def list(self):
        return sorted(self._services.keys())
