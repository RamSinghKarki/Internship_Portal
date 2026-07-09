-- ============================================================
-- Internship Portal - Database Setup
-- Run this file once in MySQL:  mysql -u root -p < database.sql
-- ============================================================

CREATE DATABASE IF NOT EXISTS internship_db;
USE internship_db;

-- 1. Users table (students, companies and admin all live here)
CREATE TABLE users (
    id       INT AUTO_INCREMENT PRIMARY KEY,
    name     VARCHAR(100) NOT NULL,
    email    VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role     VARCHAR(20)  NOT NULL      -- 'student', 'company' or 'admin'
);

-- 2. Internships table (posted by companies)
CREATE TABLE internships (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    company_id  INT NOT NULL,           -- which company posted it
    title       VARCHAR(200) NOT NULL,
    description TEXT,
    skills      VARCHAR(255),
    deadline    DATE,
    FOREIGN KEY (company_id) REFERENCES users(id)
);

-- 3. Applications table (students apply to internships)
CREATE TABLE applications (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    student_id    INT NOT NULL,
    internship_id INT NOT NULL,
    status        VARCHAR(20) DEFAULT 'applied',   -- applied / selected / rejected
    FOREIGN KEY (student_id)    REFERENCES users(id),
    FOREIGN KEY (internship_id) REFERENCES internships(id)
);

-- Default admin account  (email: admin@portal.com  password: admin123)
INSERT INTO users (name, email, password, role) VALUES
('Admin', 'admin@portal.com',
 'pbkdf2:sha256:1000000$q9kKTkMrQZLUSLQp$50cdcb29c2a20385dc20c63bc2735817ce17372aa4c138e4fbd44c8e6d79d698',
 'admin');
