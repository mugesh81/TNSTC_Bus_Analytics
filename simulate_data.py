import pandas as pd
import numpy as np
import random
from faker import Faker
from datetime import timedelta

fake = Faker()
random.seed(42)
np.random.seed(42)

# -------------------------------
# ROUTES DATA
# -------------------------------
routes = [
    (1, "Chennai - Vellore", "Chennai", "Vellore", 140),
    (2, "Chennai - Pondicherry", "Chennai", "Pondicherry", 160),
    (3, "Madurai - Rameshwaram", "Madurai", "Rameshwaram", 170),
    (4, "Coimbatore - Ooty", "Coimbatore", "Ooty", 85),
    (5, "Trichy - Thanjavur", "Trichy", "Thanjavur", 60),
    (6, "Tirunelveli - Nagercoil", "Tirunelveli", "Nagercoil", 35),
    (7, "Salem - Erode", "Salem", "Erode", 55),
    (8, "Coimbatore - Pollachi", "Coimbatore", "Pollachi", 40),
    (9, "Chennai - Tirupati", "Chennai", "Tirupati", 150),
    (10, "Madurai - Kodaikanal", "Madurai", "Kodaikanal", 120)
]

routes_df = pd.DataFrame(routes, columns=[
    "route_id", "route_name", "start_stop", "end_stop", "distance_km"
])

# -------------------------------
# STOPS DATA
# -------------------------------
stops = [
    (1, "Chennai", 13.0827, 80.2707),
    (2, "Vellore", 12.9165, 79.1325),
    (3, "Pondicherry", 11.9416, 79.8083),
    (4, "Madurai", 9.9252, 78.1198),
    (5, "Rameshwaram", 9.2881, 79.3129),
    (6, "Coimbatore", 11.0168, 76.9558),
    (7, "Ooty", 11.4064, 76.6932),
    (8, "Trichy", 10.7905, 78.7047),
    (9, "Thanjavur", 10.7867, 79.1378),
    (10, "Tirunelveli", 8.7139, 77.7567)
]

stops_df = pd.DataFrame(stops, columns=[
    "stop_id", "stop_name", "latitude", "longitude"
])

# -------------------------------
# ROUTE STOPS (FIXED ✅)
# -------------------------------
route_stops = []
id_counter = 1

for route in routes:
    route_id = route[0]
    selected_stops = random.sample(range(1, 11), random.randint(3, 5))

    order = 1
    for stop_id in selected_stops:
        route_stops.append((id_counter, route_id, stop_id, order))
        id_counter += 1
        order += 1

route_stops_df = pd.DataFrame(route_stops, columns=[
    "id", "route_id", "stop_id", "stop_order"
])

# -------------------------------
# BUSES DATA
# -------------------------------
bus_types = ["Ordinary", "Express", "AC Sleeper", "Mini Bus", "Deluxe"]

buses = []
for i in range(1, 21):
    buses.append((
        i,
        random.choice(bus_types),
        random.randint(30, 55),
        random.randint(1, 10)
    ))

buses_df = pd.DataFrame(buses, columns=[
    "bus_id", "bus_type", "capacity", "route_id"
])

# -------------------------------
# TRIPS DATA
# -------------------------------
trips = []
trip_id = 1

for _ in range(500):
    route = random.choice(routes)
    route_id = route[0]
    distance_km = route[4]

    scheduled_time = fake.date_time_this_year()
    hour = scheduled_time.hour

    # Delay logic
    if distance_km > 120:
        delay = random.randint(10, 25)
    elif distance_km > 60:
        delay = random.randint(5, 15)
    else:
        delay = random.randint(0, 8)

    # Peak hour effect
    if 7 <= hour <= 9 or 17 <= hour <= 19:
        delay += random.randint(5, 10)

    actual_time = scheduled_time + timedelta(minutes=delay)

    trips.append((
        trip_id,
        route_id,
        scheduled_time,
        actual_time,
        delay
    ))

    trip_id += 1

trips_df = pd.DataFrame(trips, columns=[
    "trip_id", "route_id", "scheduled_time", "actual_time", "delay_minutes"
])

# -------------------------------
# PASSENGER LOAD
# -------------------------------
passenger_load = []
load_id = 1

for _, trip in trips_df.iterrows():
    route = routes_df[routes_df["route_id"] == trip["route_id"]].iloc[0]
    distance_km = route["distance_km"]

    hour = trip["scheduled_time"].hour

    if 7 <= hour <= 9 or 17 <= hour <= 19:
        passengers = random.randint(35, 55)
    elif 10 <= hour <= 16:
        passengers = random.randint(20, 40)
    else:
        passengers = random.randint(5, 20)

    # Weekend effect
    if trip["scheduled_time"].weekday() >= 5:
        passengers += random.randint(5, 15)

    # Distance effect
    if distance_km > 120:
        passengers -= random.randint(5, 10)

    # Noise
    passengers += random.randint(-3, 3)
    passengers = max(0, passengers)

    stop_id = random.randint(1, 10)

    passenger_load.append((
        load_id,
        trip["trip_id"],
        stop_id,
        passengers
    ))

    load_id += 1

passenger_df = pd.DataFrame(passenger_load, columns=[
    "load_id", "trip_id", "stop_id", "passenger_count"
])

# -------------------------------
# FUEL EXPENSES
# -------------------------------
fuel_data = []
expense_id = 1

for _ in range(1000):
    route = random.choice(routes)
    route_id = route[0]
    distance_km = route[4]

    fuel_cost = distance_km * random.uniform(2.5, 4.0)

    date = fake.date_this_year()

    fuel_data.append((
        expense_id,
        route_id,
        round(fuel_cost, 2),
        date
    ))

    expense_id += 1

fuel_df = pd.DataFrame(fuel_data, columns=[
    "expense_id", "route_id", "fuel_cost", "date"
])

# -------------------------------
# SAVE FILES
# -------------------------------
routes_df.to_csv("tnstc_data/routes.csv", index=False)
stops_df.to_csv("tnstc_data/stops.csv", index=False)
route_stops_df.to_csv("tnstc_data/route_stops.csv", index=False)
buses_df.to_csv("tnstc_data/buses.csv", index=False)
trips_df.to_csv("tnstc_data/trips.csv", index=False)
passenger_df.to_csv("tnstc_data/passenger_load.csv", index=False)
fuel_df.to_csv("tnstc_data/fuel_expenses.csv", index=False)

print("✅ Data generation completed successfully!")