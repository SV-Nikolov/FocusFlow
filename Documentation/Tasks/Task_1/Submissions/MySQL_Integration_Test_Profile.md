# MySQL Integration Test Profile

This profile provides a repeatable local setup to run SQLAlchemy/MySQL integration tests.

## 1. Start MySQL test container

From project root:

```powershell
docker compose -f docker-compose.mysql-test.yml up -d
```

## 2. Set connection URL for tests

In PowerShell:

```powershell
$env:MYSQL_TEST_URL="mysql+mysqlconnector://focusflow:focusflowpass@127.0.0.1:3307/focusflow_test"
```

## 3. Run integration tests

```powershell
python -m pytest tests/integration -q
```

## 4. Run full suite

```powershell
python -m pytest -q
```

## 5. Stop container

```powershell
docker compose -f docker-compose.mysql-test.yml down -v
```

## Notes

- Integration tests are intentionally skipped when `MYSQL_TEST_URL` is not defined.
- The schema is recreated in test setup to keep test runs deterministic.
