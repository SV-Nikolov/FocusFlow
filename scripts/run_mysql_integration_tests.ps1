param(
    [string]$MysqlTestUrl = "mysql+mysqlconnector://focusflow:focusflowpass@127.0.0.1:3307/focusflow_test"
)

$env:MYSQL_TEST_URL = $MysqlTestUrl
python -m pytest tests/integration -q
