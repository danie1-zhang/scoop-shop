# Backend tests

The suite uses PostgreSQL because Scoop Shop relies on PostgreSQL-specific
upserts and row locks. It refuses to run unless `TEST_DATABASE_URL` points to a
database whose name ends in `_test`.

Run every test:

```bash
uv run pytest
```

Run only the full happy-path smoke test:

```bash
uv run pytest tests/test_smoke.py -v
```

At the start of a test session, the suite rebuilds the `public` schema in the
test database and applies all Alembic migrations. Before each test, it truncates
only the application tables in that test database.
