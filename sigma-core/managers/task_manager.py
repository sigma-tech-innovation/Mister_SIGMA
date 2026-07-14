class TaskManager:
    def __init__(self, engine):
        self.engine = engine
        self._tasks = {}

    def add(self, name, value):
        self._tasks[name] = value

    def get(self, name):
        return self._tasks.get(name)

    def list(self):
        return sorted(self._tasks.keys())
