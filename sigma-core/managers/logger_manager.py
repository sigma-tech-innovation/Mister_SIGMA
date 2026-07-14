class LoggerManager:
    def __init__(self, engine):
        self.engine = engine

    def info(self, message):
        print(f"[INFO] {message}")

    def warning(self, message):
        print(f"[WARNING] {message}")

    def error(self, message):
        print(f"[ERROR] {message}")
