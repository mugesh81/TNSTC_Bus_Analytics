-- ============================================================
--  TNSTC Bus Route Analytics — MySQL Setup Script
--  Run this entire file in MySQL Workbench
--  It will: create database → create 7 tables → load CSV data
-- ============================================================


-- ── STEP 1: Create and select the database ──────────────────
CREATE DATABASE IF NOT EXISTS tnstc_analytics;
USE tnstc_analytics;


-- ── STEP 2: Drop tables if they already exist ───────────────
-- (This lets you re-run the script cleanly if needed)
DROP TABLE IF EXISTS fuel_expenses;
DROP TABLE IF EXISTS passenger_load;
DROP TABLE IF EXISTS trips;
DROP TABLE IF EXISTS route_stops;
DROP TABLE IF EXISTS buses;
DROP TABLE IF EXISTS stops;
DROP TABLE IF EXISTS routes;


-- ── STEP 3: Create all 7 tables ─────────────────────────────

-- Table 1: routes
-- Stores the 20 TNSTC bus routes with distance
CREATE TABLE routes (
    route_id    INT PRIMARY KEY,
    route_name  VARCHAR(100) NOT NULL,
    start_stop  VARCHAR(100) NOT NULL,
    end_stop    VARCHAR(100) NOT NULL,
    distance_km INT          NOT NULL
);

-- Table 2: stops
-- Stores 30 bus stops with GPS coordinates
CREATE TABLE stops (
    stop_id   INT PRIMARY KEY,
    stop_name VARCHAR(100)   NOT NULL,
    latitude  DECIMAL(9, 6)  NOT NULL,
    longitude DECIMAL(9, 6)  NOT NULL
);

-- Table 3: route_stops
-- Links routes to stops (which stops are on which route)
CREATE TABLE route_stops (
    id         INT PRIMARY KEY,
    route_id   INT NOT NULL,
    stop_id    INT NOT NULL,
    stop_order INT NOT NULL,
    FOREIGN KEY (route_id) REFERENCES routes(route_id),
    FOREIGN KEY (stop_id)  REFERENCES stops(stop_id)
);

-- Table 4: buses
-- Stores 60 buses with their type and assigned route
CREATE TABLE buses (
    bus_id    INT PRIMARY KEY,
    bus_type  VARCHAR(50)  NOT NULL,
    capacity  INT          NOT NULL,
    route_id  INT          NOT NULL,
    FOREIGN KEY (route_id) REFERENCES routes(route_id)
);

-- Table 5: trips
-- Stores 500 trips with scheduled vs actual times and delay
CREATE TABLE trips (
    trip_id        INT PRIMARY KEY,
    route_id       INT          NOT NULL,
    scheduled_time DATETIME     NOT NULL,
    actual_time    DATETIME     NOT NULL,
    delay_minutes  INT          NOT NULL,
    FOREIGN KEY (route_id) REFERENCES routes(route_id)
);

-- Table 6: passenger_load
-- Stores passenger count at each stop for each trip
CREATE TABLE passenger_load (
    load_id         INT PRIMARY KEY,
    trip_id         INT NOT NULL,
    stop_id         INT NOT NULL,
    passenger_count INT NOT NULL,
    FOREIGN KEY (trip_id) REFERENCES trips(trip_id),
    FOREIGN KEY (stop_id) REFERENCES stops(stop_id)
);

-- Table 7: fuel_expenses
-- Stores daily fuel cost per route for 90 days
CREATE TABLE fuel_expenses (
    expense_id INT PRIMARY KEY,
    route_id   INT            NOT NULL,
    fuel_cost  DECIMAL(10, 2) NOT NULL,
    date       DATE           NOT NULL,
    FOREIGN KEY (route_id) REFERENCES routes(route_id)
);

-- Confirm all tables were created
SHOW TABLES;


-- ── STEP 4: Allow MySQL to load local CSV files ──────────────
-- Run this once to enable local file loading
SET GLOBAL local_infile = 1;


-- ── STEP 5: Load data from clean CSV files ───────────────────
-- IMPORTANT: Change the path below to match YOUR computer
-- Example: If your project is on Desktop, the path is:
-- C:/Users/HP/Desktop/tnstc_project/tnstc_data_clean/

-- NOTE: Use FORWARD SLASHES / not backslashes \ in the path

LOAD DATA LOCAL INFILE 'C:/Users/HP/Desktop/tnstc_project/tnstc_data_clean/routes.csv'
INTO TABLE routes
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(route_id, route_name, start_stop, end_stop, distance_km);

LOAD DATA LOCAL INFILE 'C:/Users/HP/Desktop/tnstc_project/tnstc_data_clean/stops.csv'
INTO TABLE stops
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(stop_id, stop_name, latitude, longitude);

LOAD DATA LOCAL INFILE 'C:/Users/HP/Desktop/tnstc_project/tnstc_data_clean/route_stops.csv'
INTO TABLE route_stops
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(id, route_id, stop_id, stop_order);

LOAD DATA LOCAL INFILE 'C:/Users/HP/Desktop/tnstc_project/tnstc_data_clean/buses.csv'
INTO TABLE buses
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(bus_id, bus_type, capacity, route_id);

LOAD DATA LOCAL INFILE 'C:/Users/HP/Desktop/tnstc_project/tnstc_data_clean/trips.csv'
INTO TABLE trips
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(trip_id, route_id, scheduled_time, actual_time, delay_minutes);

LOAD DATA LOCAL INFILE 'C:/Users/HP/Desktop/tnstc_project/tnstc_data_clean/passenger_load.csv'
INTO TABLE passenger_load
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(load_id, trip_id, stop_id, passenger_count);

LOAD DATA LOCAL INFILE 'C:/Users/HP/Desktop/tnstc_project/tnstc_data_clean/fuel_expenses.csv'
INTO TABLE fuel_expenses
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(expense_id, route_id, fuel_cost, date);


-- ── STEP 6: Verify all data loaded correctly ─────────────────
SELECT 'routes'         AS table_name, COUNT(*) AS row_count FROM routes
UNION ALL
SELECT 'stops',          COUNT(*) FROM stops
UNION ALL
SELECT 'route_stops',    COUNT(*) FROM route_stops
UNION ALL
SELECT 'buses',          COUNT(*) FROM buses
UNION ALL
SELECT 'trips',          COUNT(*) FROM trips
UNION ALL
SELECT 'passenger_load', COUNT(*) FROM passenger_load
UNION ALL
SELECT 'fuel_expenses',  COUNT(*) FROM fuel_expenses;
