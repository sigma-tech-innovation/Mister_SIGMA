class EventManager:
    def __init__(self, engine):
        self.engine = engine
        self._events = {}

    def on(self, name, callback):
        self._events.setdefault(name, []).append(callback)

    def emit(self, name, *args, **kwargs):
        for cb in self._events.get(name, []):
            cb(*args, **kwargs)

    def events(self):
        return sorted(self._events.keys())
