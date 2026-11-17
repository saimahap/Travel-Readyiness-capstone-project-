-- AI-Based Pre-Travel Readiness Prediction System
-- MySQL Database Schema

CREATE DATABASE IF NOT EXISTS travel_readiness_db;
USE travel_readiness_db;

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    phone VARCHAR(25),
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Travel Assessments Table
CREATE TABLE IF NOT EXISTS travel_assessments (
    assessment_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    destination_country VARCHAR(100) NOT NULL,
    travel_date DATE NOT NULL,
    return_date DATE NOT NULL,
    travel_purpose VARCHAR(50) NOT NULL DEFAULT 'Tourism',
    passport_status VARCHAR(20) NOT NULL,
    passport_expiry_date DATE NOT NULL,
    visa_status VARCHAR(30) NOT NULL,
    return_ticket VARCHAR(10) NOT NULL,
    hotel_booking VARCHAR(10) NOT NULL,
    travel_insurance VARCHAR(10) NOT NULL,
    vaccination_status VARCHAR(10) NOT NULL,
    prediction_result VARCHAR(30) NOT NULL,
    readiness_score INT NOT NULL DEFAULT 0,
    missing_requirements TEXT,
    assessment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- 3. Travel Reports Table
CREATE TABLE IF NOT EXISTS travel_reports (
    report_id INT AUTO_INCREMENT PRIMARY KEY,
    assessment_id INT NOT NULL,
    user_id INT NOT NULL,
    report_path VARCHAR(255) NOT NULL,
    generated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (assessment_id) REFERENCES travel_assessments(assessment_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX idx_user_email ON users(email);
CREATE INDEX idx_assessment_user ON travel_assessments(user_id);
CREATE INDEX idx_assessment_date ON travel_assessments(assessment_date);

