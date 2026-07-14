import importlib.util
import unittest
from types import SimpleNamespace


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


event = load(
    "event",
    "sigma-core/managers/event_manager.py"
)


class EventManagerTests(unittest.TestCase):

    def setUp(self):
        self.engine = SimpleNamespace()
        self.m = event.EventManager(self.engine)

    def test_manager_exists(self):
        self.assertIsNotNone(self.m)

    def test_on_and_events(self):
        self.m.on("started", lambda: None)
        self.m.on("stopped", lambda: None)

        self.assertEqual(
            self.m.events(),
            ["started", "stopped"]
        )

    def test_emit(self):
        received = []

        def callback(value, status=None):
            received.append((value, status))

        self.m.on("updated", callback)
        self.m.emit("updated", 42, status="ok")

        self.assertEqual(
            received,
            [(42, "ok")]
        )

    def test_multiple_callbacks(self):
        received = []

        self.m.on(
            "sync",
            lambda value: received.append(("first", value))
        )
        self.m.on(
            "sync",
            lambda value: received.append(("second", value))
        )

        self.m.emit("sync", "done")

        self.assertEqual(
            received,
            [
                ("first", "done"),
                ("second", "done")
            ]
        )

    def test_emit_unknown_event(self):
        self.m.emit("missing", 1, status="ignored")

        self.assertEqual(
            self.m.events(),
            []
        )


if __name__ == "__main__":
    unittest.main()
