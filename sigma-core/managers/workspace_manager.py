import shutil


class WorkspaceManager:
    def __init__(self, engine):
        self.engine = engine

    def root(self):
        return self.engine.root

    def path(self, *parts):
        return self.engine.root.joinpath(*parts)

    def exists(self, *parts):
        return self.path(*parts).exists()

    def list(self, *parts):
        target = self.path(*parts)

        if not target.exists() or not target.is_dir():
            return []

        return sorted(target.iterdir(), key=lambda item: item.name)

    def count(self, *parts):
        return len(self.list(*parts))

    def create(self, *parts, content=None, directory=False):
        target = self.path(*parts)

        if target.exists():
            return None

        if directory:
            target.mkdir(parents=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content or "", encoding="utf-8")

        return target

    def update(self, *parts, content):
        target = self.path(*parts)

        if not target.exists() or target.is_dir():
            return None

        target.write_text(content, encoding="utf-8")
        return target

    def delete(self, *parts):
        target = self.path(*parts)

        if not target.exists():
            return False

        if target.is_dir():
            shutil.rmtree(target)
        else:
            target.unlink()

        return True
