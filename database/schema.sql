-- Smart Women Safety Alert System
-- Normalized MySQL Database Schema Script
-- Supports MySQL 8.0+

CREATE DATABASE IF NOT EXISTS women_safety_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE women_safety_db;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    phone VARCHAR(20) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    emergency_pin VARCHAR(10) DEFAULT '1234',
    blood_group VARCHAR(10) DEFAULT 'O+',
    medical_notes TEXT,
    address TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    role VARCHAR(20) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_email (email),
    INDEX idx_user_phone (phone)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS admin_users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    badge_number VARCHAR(50),
    department VARCHAR(100) DEFAULT 'Emergency Response & Safety Cell',
    is_superadmin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS emergency_contacts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    relationship VARCHAR(50) NOT NULL,
    is_primary BOOLEAN DEFAULT FALSE,
    email VARCHAR(120),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_contact_user (user_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS emergency_alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    alert_type VARCHAR(50) DEFAULT 'SOS_BUTTON',
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    accuracy_meters DECIMAL(6, 2) DEFAULT 10.0,
    address_description TEXT,
    google_maps_url TEXT NOT NULL,
    status VARCHAR(30) DEFAULT 'ACTIVE',
    silent_mode BOOLEAN DEFAULT FALSE,
    battery_level INT DEFAULT 100,
    network_status VARCHAR(20) DEFAULT 'ONLINE',
    tracking_token VARCHAR(64) UNIQUE,
    resolution_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_alert_status (status),
    INDEX idx_alert_user (user_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS location_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    alert_id INT NULL,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    speed DECIMAL(5, 2) DEFAULT 0.0,
    heading DECIMAL(5, 2) DEFAULT 0.0,
    battery_level INT DEFAULT 100,
    is_offline_sync BOOLEAN DEFAULT FALSE,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (alert_id) REFERENCES emergency_alerts(id) ON DELETE SET NULL,
    INDEX idx_loc_user_time (user_id, recorded_at)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS incident_reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    reported_by_user_id INT NULL,
    title VARCHAR(150) NOT NULL,
    category VARCHAR(60) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    location_name VARCHAR(200) NOT NULL,
    description TEXT,
    is_anonymous BOOLEAN DEFAULT FALSE,
    is_verified BOOLEAN DEFAULT TRUE,
    reported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (reported_by_user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_incident_coords (latitude, longitude),
    INDEX idx_incident_severity (severity)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS risk_predictions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    time_of_day_hour INT NOT NULL,
    calculated_risk_score DECIMAL(5, 2) NOT NULL,
    risk_category VARCHAR(20) NOT NULL,
    reason_warning TEXT NOT NULL,
    recommended_action TEXT NOT NULL,
    predicted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS safe_zones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    zone_name VARCHAR(100) NOT NULL,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    radius_meters INT DEFAULT 200,
    notify_on_exit BOOLEAN DEFAULT TRUE,
    notify_on_entry BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    alert_id INT NULL,
    recipient_phone VARCHAR(20) NOT NULL,
    recipient_name VARCHAR(100) NOT NULL,
    message_body TEXT NOT NULL,
    channel VARCHAR(20) DEFAULT 'SMS',
    delivery_status VARCHAR(20) DEFAULT 'SENT',
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (alert_id) REFERENCES emergency_alerts(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS incident_evidence (
    id INT AUTO_INCREMENT PRIMARY KEY,
    alert_id INT NOT NULL,
    user_id INT NOT NULL,
    file_type VARCHAR(20) DEFAULT 'AUDIO',
    file_path VARCHAR(255) NOT NULL,
    file_size_bytes INT NOT NULL,
    duration_seconds INT DEFAULT 0,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (alert_id) REFERENCES emergency_alerts(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;
