# ============================================================
#  TNSTC Bus Route Analytics — Data Cleaning Script
#  This script reads all 7 CSV files, checks for problems,
#  fixes them, and saves CLEAN versions ready for MySQL
# ============================================================

import pandas as pd
import os

# ── Where to read from and save to ───────────────────────────
INPUT_FOLDER  = "tnstc_data"           # raw CSVs from simulate_data.py
OUTPUT_FOLDER = "tnstc_data_clean"     # cleaned CSVs go here

os.makedirs(OUTPUT_FOLDER, exist_ok=True)
print("📁 Created folder: tnstc_data_clean")
print("=" * 55)


# ============================================================
# HELPER FUNCTION — prints a summary of any DataFrame
# ============================================================
def check_dataframe(df, name):
    print(f"\n🔍 Checking: {name}")
    print(f"   Rows: {len(df)}  |  Columns: {list(df.columns)}")

    # Check for null/missing values
    nulls = df.isnull().sum()
    if nulls.sum() == 0:
        print("   ✅ No missing values found")
    else:
        print(f"   ⚠️  Missing values found:")
        print(nulls[nulls > 0])

    # Check for duplicate rows
    dupes = df.duplicated().sum()
    if dupes == 0:
        print("   ✅ No duplicate rows found")
    else:
        print(f"   ⚠️  {dupes} duplicate rows found — will be removed")

    return nulls, dupes


# ============================================================
# TABLE 1 — routes
# ============================================================
routes = pd.read_csv(f"{INPUT_FOLDER}/routes.csv")
check_dataframe(routes, "routes.csv")

# Clean steps:
routes = routes.drop_duplicates()                          # remove duplicate rows
routes["route_name"] = routes["route_name"].str.strip()   # remove extra spaces
routes["start_stop"] = routes["start_stop"].str.strip()
routes["end_stop"]   = routes["end_stop"].str.strip()
routes["distance_km"] = pd.to_numeric(routes["distance_km"], errors="coerce")  # make sure it's a number
routes = routes.dropna()                                   # drop any row that has NaN after coerce

routes.to_csv(f"{OUTPUT_FOLDER}/routes.csv", index=False)
print(f"   💾 Saved clean routes.csv — {len(routes)} rows")


# ============================================================
# TABLE 2 — stops
# ============================================================
stops = pd.read_csv(f"{INPUT_FOLDER}/stops.csv")
check_dataframe(stops, "stops.csv")

stops = stops.drop_duplicates()
stops["stop_name"] = stops["stop_name"].str.strip()

# Latitude must be between 8 and 14 (Tamil Nadu range)
before = len(stops)
stops = stops[(stops["latitude"] >= 8.0) & (stops["latitude"] <= 14.0)]
stops = stops[(stops["longitude"] >= 76.0) & (stops["longitude"] <= 80.5)]
after = len(stops)
if before != after:
    print(f"   ⚠️  Removed {before - after} stops with invalid coordinates")
else:
    print("   ✅ All coordinates are in valid Tamil Nadu range")

stops.to_csv(f"{OUTPUT_FOLDER}/stops.csv", index=False)
print(f"   💾 Saved clean stops.csv — {len(stops)} rows")


# ============================================================
# TABLE 3 — route_stops
# ============================================================
route_stops = pd.read_csv(f"{INPUT_FOLDER}/route_stops.csv")
check_dataframe(route_stops, "route_stops.csv")

route_stops = route_stops.drop_duplicates()

# stop_order must be a positive number
route_stops["stop_order"] = pd.to_numeric(route_stops["stop_order"], errors="coerce")
route_stops = route_stops.dropna()
route_stops = route_stops[route_stops["stop_order"] > 0]

route_stops.to_csv(f"{OUTPUT_FOLDER}/route_stops.csv", index=False)
print(f"   💾 Saved clean route_stops.csv — {len(route_stops)} rows")


# ============================================================
# TABLE 4 — buses
# ============================================================
buses = pd.read_csv(f"{INPUT_FOLDER}/buses.csv")
check_dataframe(buses, "buses.csv")

buses = buses.drop_duplicates()
buses["bus_type"] = buses["bus_type"].str.strip()

# Capacity must be between 10 and 100 (realistic bus range)
before = len(buses)
buses = buses[(buses["capacity"] >= 10) & (buses["capacity"] <= 100)]
after = len(buses)
if before != after:
    print(f"   ⚠️  Removed {before - after} buses with unrealistic capacity")
else:
    print("   ✅ All bus capacities are in valid range")

# Standardise bus_type names (fix any case issues)
valid_types = ["Ordinary", "Express", "Deluxe", "AC Sleeper", "Mini Bus"]
buses["bus_type"] = buses["bus_type"].apply(
    lambda x: x if x in valid_types else "Ordinary"
)

buses.to_csv(f"{OUTPUT_FOLDER}/buses.csv", index=False)
print(f"   💾 Saved clean buses.csv — {len(buses)} rows")


# ============================================================
# TABLE 5 — trips
# ============================================================
trips = pd.read_csv(f"{INPUT_FOLDER}/trips.csv")
check_dataframe(trips, "trips.csv")

trips = trips.drop_duplicates()

# Convert time columns to proper datetime format
trips["scheduled_time"] = pd.to_datetime(trips["scheduled_time"], errors="coerce")
trips["actual_time"]    = pd.to_datetime(trips["actual_time"],    errors="coerce")

# Drop rows where time conversion failed
before = len(trips)
trips = trips.dropna(subset=["scheduled_time", "actual_time"])
after = len(trips)
if before != after:
    print(f"   ⚠️  Removed {before - after} trips with invalid time format")

# delay_minutes must be between 0 and 120
trips["delay_minutes"] = pd.to_numeric(trips["delay_minutes"], errors="coerce")
trips = trips[(trips["delay_minutes"] >= 0) & (trips["delay_minutes"] <= 120)]

# Recalculate delay_minutes from actual - scheduled (double check)
trips["delay_check"] = (
    trips["actual_time"] - trips["scheduled_time"]
).dt.total_seconds() / 60
trips["delay_minutes"] = trips["delay_check"].round(0).astype(int)
trips = trips.drop(columns=["delay_check"])

# Format times back to string for MySQL
trips["scheduled_time"] = trips["scheduled_time"].dt.strftime("%Y-%m-%d %H:%M:%S")
trips["actual_time"]    = trips["actual_time"].dt.strftime("%Y-%m-%d %H:%M:%S")

trips.to_csv(f"{OUTPUT_FOLDER}/trips.csv", index=False)
print(f"   💾 Saved clean trips.csv — {len(trips)} rows")


# ============================================================
# TABLE 6 — passenger_load
# ============================================================
passenger = pd.read_csv(f"{INPUT_FOLDER}/passenger_load.csv")
check_dataframe(passenger, "passenger_load.csv")

passenger = passenger.drop_duplicates()

# passenger_count must be between 1 and 100
passenger["passenger_count"] = pd.to_numeric(passenger["passenger_count"], errors="coerce")
before = len(passenger)
passenger = passenger[(passenger["passenger_count"] >= 1) & (passenger["passenger_count"] <= 100)]
passenger = passenger.dropna()
after = len(passenger)
if before != after:
    print(f"   ⚠️  Removed {before - after} rows with invalid passenger counts")
else:
    print("   ✅ All passenger counts are in valid range")

passenger.to_csv(f"{OUTPUT_FOLDER}/passenger_load.csv", index=False)
print(f"   💾 Saved clean passenger_load.csv — {len(passenger)} rows")


# ============================================================
# TABLE 7 — fuel_expenses
# ============================================================
fuel = pd.read_csv(f"{INPUT_FOLDER}/fuel_expenses.csv")
check_dataframe(fuel, "fuel_expenses.csv")

fuel = fuel.drop_duplicates()

# fuel_cost must be a positive number
fuel["fuel_cost"] = pd.to_numeric(fuel["fuel_cost"], errors="coerce")
before = len(fuel)
fuel = fuel[fuel["fuel_cost"] > 0]
fuel = fuel.dropna()
after = len(fuel)
if before != after:
    print(f"   ⚠️  Removed {before - after} rows with invalid fuel cost")
else:
    print("   ✅ All fuel costs are positive")

# Make sure date column is in correct format YYYY-MM-DD
fuel["date"] = pd.to_datetime(fuel["date"], errors="coerce").dt.strftime("%Y-%m-%d")
fuel = fuel.dropna(subset=["date"])

fuel.to_csv(f"{OUTPUT_FOLDER}/fuel_expenses.csv", index=False)
print(f"   💾 Saved clean fuel_expenses.csv — {len(fuel)} rows")


# ============================================================
# FINAL SUMMARY
# ============================================================
print()
print("=" * 55)
print("  DATA CLEANING COMPLETE!")
print("=" * 55)

files = ["routes", "stops", "route_stops", "buses", "trips", "passenger_load", "fuel_expenses"]
total_rows = 0
for f in files:
    df = pd.read_csv(f"{OUTPUT_FOLDER}/{f}.csv")
    total_rows += len(df)
    print(f"  {f+'.csv':<25} → {len(df):>5} rows  ✅")

print(f"\n  Total rows across all tables: {total_rows:,}")
print(f"  Clean files saved in: {OUTPUT_FOLDER}/")
print("=" * 55)
print()
print("  ✅ Your data is now clean and ready for MySQL!")
print("  👉 Next step: Load these CSVs into MySQL database")
