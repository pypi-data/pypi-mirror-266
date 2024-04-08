import os
import unittest
from unittest.mock import patch
from sqlalchemy.engine import Engine
from aq_utilities.engine.psql import get_engine, reset_engine


class TestRemoteConfig(unittest.TestCase):
    @patch.dict(
        os.environ, {
            "PGUSER": "pgadmin",
            "PGPASSWORD": "test_password",
            "PGHOST": "test_host",
            "PGDATABASE": "test_db",
            "PGPORT": "5432"
        })
    def test_get_engine(self):
        # test to ensure we get an engine
        engine = get_engine()
        self.assertIsInstance(engine, Engine)
        # test that we can reset the engine
        result = reset_engine()
        self.assertIsNone(result)
        # test that the new get engine uses environment variables
        engine = get_engine()
        self.assertEqual(engine.url.username, "pgadmin")
        self.assertEqual(engine.dialect.name, "postgresql")
        self.assertFalse(engine.echo)
        # test that we can also pass params to get_engine
        _ = reset_engine()
        engine = get_engine(
            "foo_test_user",
            "foo_test_password",
            "foo_test_host",
            "foo_test_db",
        )
        self.assertEqual(engine.url.username, "foo_test_user")
        self.assertEqual(engine.url.password, "foo_test_password")
        self.assertEqual(engine.url.host, "foo_test_host")
        self.assertEqual(engine.url.database, "foo_test_db")
        self.assertEqual(engine.dialect.name, "postgresql")
        self.assertFalse(engine.echo)

if __name__ == "__main__":
    unittest.main()