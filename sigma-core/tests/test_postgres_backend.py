import importlib.util
import unittest
from unittest.mock import patch


def load(name, path):
    spec = importlib.util.spec_from_file_location(
        name,
        path
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


postgres_module = load(
    "postgres_backend",
    "sigma-core/managers/database_backends/"
    "postgres_backend.py"
)


class PostgreSQLBackendTests(unittest.TestCase):

    def test_backend_exists(self):
        backend = (
            postgres_module.PostgreSQLBackend()
        )

        self.assertIsNotNone(backend)

    @patch.object(
        postgres_module.importlib,
        "import_module",
        side_effect=ImportError
    )
    def test_driver_unavailable(
        self,
        import_mock
    ):
        backend = (
            postgres_module.PostgreSQLBackend()
        )

        self.assertFalse(
            backend.driver_available()
        )
        import_mock.assert_called_once_with(
            "psycopg"
        )

    @patch.object(
        postgres_module.importlib,
        "import_module",
        side_effect=ImportError
    )
    def test_connect_requires_driver(
        self,
        import_mock
    ):
        backend = (
            postgres_module.PostgreSQLBackend(
                database_url=(
                    "postgresql://localhost/sigma"
                )
            )
        )

        with self.assertRaisesRegex(
            RuntimeError,
            "requires psycopg"
        ):
            backend.connect()

        import_mock.assert_called_once_with(
            "psycopg"
        )

    def test_custom_connect_factory(self):
        calls = []

        def factory(url):
            calls.append(url)
            return object()

        backend = (
            postgres_module.PostgreSQLBackend(
                database_url="postgresql://sigma",
                connect_factory=factory,
            )
        )

        connection = backend.connect()

        self.assertIsNotNone(connection)
        self.assertEqual(
            calls,
            ["postgresql://sigma"],
        )
        self.assertTrue(
            backend.driver_available()
        )


if __name__ == "__main__":
    unittest.main()
