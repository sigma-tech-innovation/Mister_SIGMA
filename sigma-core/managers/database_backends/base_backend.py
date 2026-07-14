class DatabaseBackend:

    def load(self, name):
        raise NotImplementedError

    def save(self, name, data):
        raise NotImplementedError

    def exists(self, name):
        raise NotImplementedError

    def delete(self, name):
        raise NotImplementedError

    def list(self):
        raise NotImplementedError
