# ============================================================
#  TNSTC Bus Route Analytics — MySQL Database Loader (Fixed)
#  Fixed: numpy.int64 conversion error
# ============================================================
 
import mysql.connector
import pandas as pd
import numpy as np
import os
 
# ============================================================
#  ⚠️  CHANGE THIS — put your MySQL root password here
# ============================================================
MYSQL_PASSWORD = "root123"   # ← replace this
 
 
# ── File path to your clean CSVs ─────────────────────────────
CLEAN_DATA_PATH = "tnstc_data_clean"
 
 
# ============================================================
# STEP 1 — Connect to MySQL
# ============================================================
print("🔌 Connecting to MySQL...")
try:
    conn = mysql.connector.connect(
        host     = "localhost",
        user     = "root",
        password = MYSQL_PASSWORD
    )
    cursor = conn.cursor()
    print("✅ Connected to MySQL successfully!")
except mysql.connector.Error as e:
    print(f"❌ Connection failed: {e}")
    print("   → Check your password in the script (MYSQL_PASSWORD variable)")
    exit()
 
 
# ============================================================
# STEP 2 — Create the database
# ============================================================
print("\n📦 Creating database...")
cursor.execute("CREATE DATABASE IF NOT EXISTS tnstc_analytics")
cursor.execute("USE tnstc_analytics")
print("✅ Database 'tnstc_analytics' ready!")
 
 
# ============================================================
# STEP 3 — Create all 7 tables
# ============================================================
print("\n🏗️  Creating tables...")
 
drop_order = [
    "fuel_expenses", "passenger_load", "trips",
    "route_stops", "buses", "stops", "routes"
]
for table in drop_order:
    cursor.execute(f"DROP TABLE IF EXISTS {table}")
 
create_statements = {
 
    "routes": """
        CREATE TABLE routes (
            route_id    INT PRIMARY KEY,
            route_name  VARCHAR(100) NOT NULL,
            start_stop  VARCHAR(100) NOT NULL,
            end_stop    VARCHAR(100) NOT NULL,
            distance_km INT          NOT NULL
        )
    """,
 
    "stops": """
        CREATE TABLE stops (
            stop_id   INT PRIMARY KEY,
            stop_name VARCHAR(100)  NOT NULL,
            latitude  DECIMAL(9,6)  NOT NULL,
            longitude DECIMAL(9,6)  NOT NULL
        )
    """,
 
    "route_stops": """
        CREATE TABLE route_stops (
            id         INT PRIMARY KEY,
            route_id   INT NOT NULL,
            stop_id    INT NOT NULL,
            stop_order INT NOT NULL,
            FOREIGN KEY (route_id) REFERENCES routes(route_id),
            FOREIGN KEY (stop_id)  REFERENCES stops(stop_id)
        )
    """,
 
    "buses": """
        CREATE TABLE buses (
            bus_id   INT PRIMARY KEY,
            bus_type VARCHAR(50) NOT NULL,
            capacity INT         NOT NULL,
            route_id INT         NOT NULL,
            FOREIGN KEY (route_id) REFERENCES routes(route_id)
        )
    """,
 
    "trips": """
        CREATE TABLE trips (
            trip_id        INT PRIMARY KEY,
            route_id       INT      NOT NULL,
            scheduled_time DATETIME NOT NULL,
            actual_time    DATETIME NOT NULL,
            delay_minutes  INT      NOT NULL,
            FOREIGN KEY (route_id) REFERENCES routes(route_id)
        )
    """,
 
    "passenger_load": """
        CREATE TABLE passenger_load (
            load_id         INT PRIMARY KEY,
            trip_id         INT NOT NULL,
            stop_id         INT NOT NULL,
            passenger_count INT NOT NULL,
            FOREIGN KEY (trip_id) REFERENCES trips(trip_id),
            FOREIGN KEY (stop_id) REFERENCES stops(stop_id)
        )
    """,
 
    "fuel_expenses": """
        CREATE TABLE fuel_expenses (
            expense_id INT            PRIMARY KEY,
            route_id   INT            NOT NULL,
            fuel_cost  DECIMAL(10,2)  NOT NULL,
            date       DATE           NOT NULL,
            FOREIGN KEY (route_id) REFERENCES routes(route_id)
        )
    """
}
 
for table_name, sql in create_statements.items():
    cursor.execute(sql)
    print(f"   ✅ Created table: {table_name}")
 
 
# ============================================================
# STEP 4 — Insert data from CSV files
# ============================================================
print("\n📥 Loading data from CSV files...")
 
 
def convert_value(v):
    """Convert numpy types to plain Python types for MySQL."""
    if v is None:
        return None
    if isinstance(v, float) and np.isnan(v):
        return None
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        f = float(v)
        return int(f) if f.is_integer() else f
    if isinstance(v, (np.bool_,)):
        return bool(v)
    return v
 
 
def load_csv_to_table(csv_filename, table_name, columns):
    filepath = os.path.join(CLEAN_DATA_PATH, csv_filename)
    df = pd.read_csv(filepath)
 
    rows = []
    for _, row in df[columns].iterrows():
        clean_row = tuple(convert_value(row[col]) for col in columns)
        rows.append(clean_row)
 
    placeholders = ", ".join(["%s"] * len(columns))
    sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
 
    cursor.executemany(sql, rows)
    conn.commit()
    print(f"   ✅ {table_name:<22} → {len(rows):>5} rows inserted")
 
 
load_csv_to_table(
    "routes.csv", "routes",
    ["route_id", "route_name", "start_stop", "end_stop", "distance_km"]
)
load_csv_to_table(
    "stops.csv", "stops",
    ["stop_id", "stop_name", "latitude", "longitude"]
)
load_csv_to_table(
    "route_stops.csv", "route_stops",
    ["id", "route_id", "stop_id", "stop_order"]
)
load_csv_to_table(
    "buses.csv", "buses",
    ["bus_id", "bus_type", "capacity", "route_id"]
)
load_csv_to_table(
    "trips.csv", "trips",
    ["trip_id", "route_id", "scheduled_time", "actual_time", "delay_minutes"]
)
load_csv_to_table(
    "passenger_load.csv", "passenger_load",
    ["load_id", "trip_id", "stop_id", "passenger_count"]
)
load_csv_to_table(
    "fuel_expenses.csv", "fuel_expenses",
    ["expense_id", "route_id", "fuel_cost", "date"]
)
 
 
# ============================================================
# STEP 5 — Verify row counts
# ============================================================
print("\n🔍 Verifying row counts in MySQL...")
print("-" * 42)
 
tables = ["routes", "stops", "route_stops", "buses",
          "trips", "passenger_load", "fuel_expenses"]
 
total = 0
for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    total += count
    print(f"   {table:<24} → {count:>5} rows ✅")
 
print("-" * 42)
print(f"   {'TOTAL':<24} → {total:>5} rows")
 
cursor.close()
conn.close()
 
print()
print("=" * 50)
print("  DATABASE SETUP COMPLETE!")
print("=" * 50)
print("  Database : tnstc_analytics")
print("  Tables   : 7")
print(f"  Rows     : {total:,}")
print()
print("  ✅ Refresh Schemas in MySQL Workbench")
print("     to see tnstc_analytics appear!")
print("  👉 Next: SQL Analysis queries (Week 3)")
print("=" * 50)