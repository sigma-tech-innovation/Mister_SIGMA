import importlib.util
import unittest


def load(name, path):
    spec = importlib.util.spec_from_file_location(
        name,
        path,
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


notion_module = load(
    "notion_provider",
    "sigma-core/managers/data_providers/"
    "notion_provider.py",
)


class FakeTransport:

    def __init__(self):
        self.calls = []

    def __call__(
        self,
        method,
        path,
        payload=None,
    ):
        self.calls.append(
            {
                "method": method,
                "path": path,
                "payload": payload,
            }
        )

        return {
            "ok": True,
            "path": path,
        }


class NotionProviderTests(unittest.TestCase):

    def create_provider(self):
        self.transport = FakeTransport()

        return notion_module.NotionProvider(
            token="secret-token",
            database_id="database-001",
            transport=self.transport,
        )

    def test_missing_configuration(self):
        provider = (
            notion_module.NotionProvider()
        )

        result = provider.validate()

        self.assertFalse(result["valid"])
        self.assertIn(
            "Notion token is missing",
            result["errors"],
        )
        self.assertIn(
            "Notion database ID is missing",
            result["errors"],
        )

    def test_valid_configuration(self):
        provider = self.create_provider()

        result = provider.validate()

        self.assertTrue(result["valid"])
        self.assertEqual(
            provider.list_resources(),
            ["database-001"],
        )

    def test_headers_do_not_expose_token_in_snapshot(self):
        provider = self.create_provider()
        snapshot = provider.snapshot()

        self.assertTrue(
            snapshot["configuration"][
                "token_configured"
            ]
        )
        self.assertNotIn(
            "secret-token",
            str(snapshot),
        )

    def test_pull(self):
        provider = self.create_provider()

        result = provider.pull()

        self.assertTrue(result["ok"])
        self.assertEqual(
            self.transport.calls[0],
            {
                "method": "POST",
                "path": (
                    "databases/database-001/query"
                ),
                "payload": {},
            },
        )

    def test_push(self):
        provider = self.create_provider()

        result = provider.push(
            "database-001",
            [
                {
                    "Name": {
                        "title": [],
                    }
                }
            ],
        )

        self.assertEqual(
            len(result),
            1,
        )
        self.assertEqual(
            self.transport.calls[0]["path"],
            "pages",
        )
        self.assertEqual(
            self.transport.calls[0]["payload"][
                "parent"
            ]["database_id"],
            "database-001",
        )

    def test_request_rejects_invalid_config(self):
        provider = (
            notion_module.NotionProvider()
        )

        with self.assertRaisesRegex(
            RuntimeError,
            "Notion token is missing",
        ):
            provider.pull()


if __name__ == "__main__":
    unittest.main()
