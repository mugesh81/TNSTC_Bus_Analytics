-- ============================================================
-- TNSTC Bus Route Analytics
-- SQL Analysis Queries
-- Database: tnstc_analytics
-- ============================================================


-- Top 10 most delayed routes
SELECT r.route_name,
       ROUND(AVG(t.delay_minutes), 2) AS avg_delay,
       MAX(t.delay_minutes) AS max_delay,
       COUNT(t.trip_id) AS total_trips
FROM trips t
JOIN routes r ON t.route_id = r.route_id
GROUP BY r.route_name
ORDER BY avg_delay DESC
LIMIT 10;


-- Underutilized routes by occupancy percentage
SELECT r.route_name,
       ROUND(AVG(p.passenger_count), 1) AS avg_passengers,
       b.capacity,
       ROUND((AVG(p.passenger_count) / b.capacity) * 100, 1) AS occupancy_pct
FROM passenger_load p
JOIN trips t ON p.trip_id = t.trip_id
JOIN routes r ON t.route_id = r.route_id
JOIN buses b ON b.route_id = r.route_id
GROUP BY r.route_name, b.capacity
ORDER BY occupancy_pct ASC
LIMIT 10;


-- Peak hour passenger surge
SELECT HOUR(t.scheduled_time) AS hour_of_day,
       ROUND(AVG(p.passenger_count), 1) AS avg_passengers,
       COUNT(t.trip_id) AS total_trips
FROM trips t
JOIN passenger_load p ON t.trip_id = p.trip_id
GROUP BY HOUR(t.scheduled_time)
ORDER BY avg_passengers DESC
LIMIT 10;


-- Fuel cost vs estimated passenger revenue per route
SELECT r.route_name,
       ROUND(SUM(f.fuel_cost), 2) AS total_fuel_cost,
       SUM(p.passenger_count) AS total_passengers,
       ROUND(SUM(p.passenger_count) * 15, 2) AS estimated_revenue,
       ROUND((SUM(p.passenger_count) * 15) - SUM(f.fuel_cost), 2) AS net_profit
FROM fuel_expenses f
JOIN routes r ON f.route_id = r.route_id
JOIN trips t ON t.route_id = r.route_id
JOIN passenger_load p ON p.trip_id = t.trip_id
GROUP BY r.route_name
ORDER BY net_profit DESC;


-- Route performance classification by delay and occupancy
SELECT r.route_name,
       ROUND(AVG(t.delay_minutes), 1) AS avg_delay,
       ROUND(AVG(p.passenger_count), 1) AS avg_passengers,
       r.distance_km,
       CASE
           WHEN AVG(t.delay_minutes) < 10 AND AVG(p.passenger_count) > 25 THEN 'Good'
           WHEN AVG(t.delay_minutes) > 20 OR AVG(p.passenger_count) < 20 THEN 'Poor'
           ELSE 'Average'
       END AS performance_status
FROM trips t
JOIN routes r ON t.route_id = r.route_id
JOIN passenger_load p ON p.trip_id = t.trip_id
GROUP BY r.route_name, r.distance_km
ORDER BY performance_status, avg_delay ASC;


-- District-wise route coverage
SELECT start_stop AS district_hub,
       COUNT(route_id) AS routes_originating,
       ROUND(AVG(distance_km), 1) AS avg_route_distance,
       SUM(distance_km) AS total_km_covered
FROM routes
GROUP BY start_stop
ORDER BY routes_originating DESC;
