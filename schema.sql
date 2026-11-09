-- AI-Based Pre-Travel Readiness Prediction System Database Schema
-- Compatible with MySQL 5.7+ / 8.0+

CREATE DATABASE IF NOT EXISTS travel_readiness_db;
USE travel_readiness_db;

CREATE TABLE IF NOT EXISTS predictions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    passenger_name VARCHAR(100) NOT NULL DEFAULT 'Anonymous',
    destination VARCHAR(100) NOT NULL DEFAULT 'International',
    passport_validity_months INT NOT NULL,
    visa_status VARCHAR(20) NOT NULL,
    return_ticket VARCHAR(10) NOT NULL,
    hotel_booking VARCHAR(10) NOT NULL,
    travel_insurance VARCHAR(10) NOT NULL,
    vaccination_status VARCHAR(10) NOT NULL,
    readiness_prediction VARCHAR(30) NOT NULL,
    confidence_score FLOAT NOT NULL,
    missing_items TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexing for fast retrieval of travel readiness reports
CREATE INDEX idx_passenger_name ON predictions(passenger_name);
CREATE INDEX idx_created_at ON predictions(created_at);

