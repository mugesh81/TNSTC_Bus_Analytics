import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

MYSQL_PASSWORD = "root123"   # replace with your password

os.makedirs("charts", exist_ok=True)

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password=MYSQL_PASSWORD,
    database="tnstc_analytics"
)

sns.set_theme(style="whitegrid")


# -- Chart 1: Top 10 delayed routes --
query1 = """
    SELECT r.route_name, ROUND(AVG(t.delay_minutes), 2) AS avg_delay
    FROM trips t
    JOIN routes r ON t.route_id = r.route_id
    GROUP BY r.route_name
    ORDER BY avg_delay DESC
    LIMIT 10
"""
df1 = pd.read_sql(query1, conn)

plt.figure(figsize=(12, 6))
bars = sns.barplot(data=df1, x="avg_delay", y="route_name", palette="Reds_r")
plt.title("Top 10 Most Delayed Routes", fontsize=14, fontweight="bold")
plt.xlabel("Average Delay (minutes)")
plt.ylabel("")
plt.tight_layout()
plt.savefig("charts/delayed_routes.png", dpi=150)
plt.close()
print("saved: charts/delayed_routes.png")


# -- Chart 2: Peak hour passenger load --
query2 = """
    SELECT HOUR(t.scheduled_time) AS hour_of_day,
           ROUND(AVG(p.passenger_count), 1) AS avg_passengers
    FROM trips t
    JOIN passenger_load p ON t.trip_id = p.trip_id
    GROUP BY HOUR(t.scheduled_time)
    ORDER BY hour_of_day
"""
df2 = pd.read_sql(query2, conn)

plt.figure(figsize=(12, 5))
sns.lineplot(data=df2, x="hour_of_day", y="avg_passengers", marker="o", color="steelblue", linewidth=2)
plt.fill_between(df2["hour_of_day"], df2["avg_passengers"], alpha=0.15, color="steelblue")
plt.xticks(range(0, 24))
plt.title("Average Passenger Load by Hour of Day", fontsize=14, fontweight="bold")
plt.xlabel("Hour of Day (24h)")
plt.ylabel("Avg Passengers")
plt.tight_layout()
plt.savefig("charts/peak_hours.png", dpi=150)
plt.close()
print("saved: charts/peak_hours.png")


# -- Chart 3: Route performance status --
query3 = """
    SELECT r.route_name,
           ROUND(AVG(t.delay_minutes), 1) AS avg_delay,
           ROUND(AVG(p.passenger_count), 1) AS avg_passengers,
           CASE
               WHEN AVG(t.delay_minutes) < 10 AND AVG(p.passenger_count) > 25 THEN 'Good'
               WHEN AVG(t.delay_minutes) > 20 OR AVG(p.passenger_count) < 20 THEN 'Poor'
               ELSE 'Average'
           END AS performance_status
    FROM trips t
    JOIN routes r ON t.route_id = r.route_id
    JOIN passenger_load p ON p.trip_id = t.trip_id
    GROUP BY r.route_name
"""
df3 = pd.read_sql(query3, conn)

status_counts = df3["performance_status"].value_counts()
colors = {"Good": "#2ecc71", "Average": "#f39c12", "Poor": "#e74c3c"}
pie_colors = [colors[s] for s in status_counts.index]

plt.figure(figsize=(7, 7))
plt.pie(status_counts, labels=status_counts.index, autopct="%1.1f%%",
        colors=pie_colors, startangle=140, textprops={"fontsize": 13})
plt.title("Route Performance Distribution", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig("charts/performance_distribution.png", dpi=150)
plt.close()
print("saved: charts/performance_distribution.png")


# -- Chart 4: Occupancy % by route (bottom 10) --
query4 = """
    SELECT r.route_name,
           ROUND((AVG(p.passenger_count) / b.capacity) * 100, 1) AS occupancy_pct
    FROM passenger_load p
    JOIN trips t ON p.trip_id = t.trip_id
    JOIN routes r ON t.route_id = r.route_id
    JOIN buses b ON b.route_id = r.route_id
    GROUP BY r.route_name, b.capacity
    ORDER BY occupancy_pct ASC
    LIMIT 10
"""
df4 = pd.read_sql(query4, conn)

plt.figure(figsize=(12, 6))
sns.barplot(data=df4, x="occupancy_pct", y="route_name", palette="Blues")
plt.axvline(x=50, color="red", linestyle="--", linewidth=1.2, label="50% threshold")
plt.title("Most Underutilized Routes by Occupancy %", fontsize=14, fontweight="bold")
plt.xlabel("Occupancy (%)")
plt.ylabel("")
plt.legend()
plt.tight_layout()
plt.savefig("charts/underutilized_routes.png", dpi=150)
plt.close()
print("saved: charts/underutilized_routes.png")


# -- Chart 5: District hub coverage --
query5 = """
    SELECT start_stop AS district_hub,
           COUNT(route_id) AS routes_originating,
           SUM(distance_km) AS total_km_covered
    FROM routes
    GROUP BY start_stop
    ORDER BY routes_originating DESC
"""
df5 = pd.read_sql(query5, conn)

fig, ax1 = plt.subplots(figsize=(12, 6))
x = range(len(df5))
bars = ax1.bar(x, df5["routes_originating"], color="steelblue", alpha=0.8, label="Routes")
ax1.set_ylabel("Number of Routes", color="steelblue")
ax1.set_xticks(x)
ax1.set_xticklabels(df5["district_hub"], rotation=30, ha="right")

ax2 = ax1.twinx()
ax2.plot(x, df5["total_km_covered"], color="darkorange", marker="o",
         linewidth=2, label="Total KM")
ax2.set_ylabel("Total KM Covered", color="darkorange")

plt.title("District Hub — Routes and Coverage", fontsize=14, fontweight="bold")
fig.tight_layout()
plt.savefig("charts/district_coverage.png", dpi=150)
plt.close()
print("saved: charts/district_coverage.png")


conn.close()
print("\nall charts saved in: charts/")
