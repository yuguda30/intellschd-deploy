import pyodbc

# Replace these with your actual values
SERVER   = "sql-svc-scheduler.database.windows.net"
DATABASE = "dbScheduler"
USERNAME = "azureadm"      # e.g. sqladmin
PASSWORD = "Arewa11223"   # the one you reset

conn_str = (
    "Driver={ODBC Driver 17 for SQL Server};"
    f"Server=tcp:{SERVER},1433;"
    f"Database={DATABASE};"
    f"Uid={USERNAME};"
    f"Pwd={PASSWORD};"
    "Encrypt=yes;"
    "Connection Timeout=30;"
)
try:
    with pyodbc.connect(conn_str) as conn:
        print("✅ Connected!")
except Exception as e:
    print("❌", e)
