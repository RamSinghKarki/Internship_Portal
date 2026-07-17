-- ============================================================
-- Internship Portal - Database Setup (matches the ER diagram)
-- Run once in MySQL:  mysql -u root -p < database.sql
--
-- Tables: roles, users, students, companies, supervisors,
--         internships, applications, progress_logs
-- ============================================================

DROP DATABASE IF EXISTS internship_db;
CREATE DATABASE internship_db;
USE internship_db;

-- 1. Roles (defines what kind of user someone is)
CREATE TABLE roles (
    id        INT AUTO_INCREMENT PRIMARY KEY,
    role_name VARCHAR(20) NOT NULL UNIQUE   -- admin / student / company / supervisor
);

-- 2. Users (central table - everyone who can login)
CREATE TABLE users (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    role_id    INT NOT NULL,
    name       VARCHAR(100) NOT NULL,
    email      VARCHAR(100) NOT NULL UNIQUE,
    password   VARCHAR(255) NOT NULL,       -- stored as a hash, never plain text
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(id)
);

-- 3. Students (extra details of a student user)
CREATE TABLE students (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT NOT NULL UNIQUE,
    roll_number VARCHAR(50),
    department  VARCHAR(100),
    semester    INT,
    skills      VARCHAR(255),
    document_url VARCHAR(255),               -- uploaded document (ID card / citizenship)
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 4. Companies (extra details of a company user)
CREATE TABLE companies (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT NOT NULL UNIQUE,
    industry    VARCHAR(100),
    location    VARCHAR(100),
    description TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 5. Supervisors (works for a company, guides students)
CREATE TABLE supervisors (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT NOT NULL UNIQUE,
    company_id  INT NOT NULL,
    designation VARCHAR(100),
    department  VARCHAR(100),
    FOREIGN KEY (user_id)    REFERENCES users(id)     ON DELETE CASCADE,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- 6. Internships (posted by companies)
CREATE TABLE internships (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    company_id      INT NOT NULL,
    title           VARCHAR(200) NOT NULL,
    description     TEXT,
    required_skills VARCHAR(255),
    duration_weeks  INT,
    stipend         VARCHAR(50),
    vacancies       INT,
    status          VARCHAR(20) DEFAULT 'open',   -- open / closed
    posted_date     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- 7. Applications (a student applies to an internship)
CREATE TABLE applications (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    student_id    INT NOT NULL,
    internship_id INT NOT NULL,
    cover_letter  TEXT,
    status        VARCHAR(20) DEFAULT 'applied',  -- applied / selected / rejected
    applied_date  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (student_id, internship_id),           -- cannot apply twice
    FOREIGN KEY (student_id)    REFERENCES students(id)    ON DELETE CASCADE,
    FOREIGN KEY (internship_id) REFERENCES internships(id) ON DELETE CASCADE
);

-- 8. Progress logs (weekly work reports of a selected student,
--    checked by a supervisor who adds feedback and marks)
CREATE TABLE progress_logs (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    application_id INT NOT NULL,
    supervisor_id  INT,                           -- filled when a supervisor gives feedback
    week_number    INT,
    description    TEXT,                          -- work done by the student
    feedback       TEXT,                          -- written by the supervisor
    marks          INT,
    submitted_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (application_id) REFERENCES applications(id) ON DELETE CASCADE,
    FOREIGN KEY (supervisor_id)  REFERENCES supervisors(id)  ON DELETE SET NULL
);

-- 9. Notifications (in-app messages for a user, shown at the bell icon)
CREATE TABLE notifications (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    user_id    INT NOT NULL,
    message    VARCHAR(255) NOT NULL,
    link       VARCHAR(255),
    is_read    BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 10. Audit logs (who did what and when - for the admin)
CREATE TABLE audit_logs (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    user_id    INT,                            -- NULL for failed logins
    action     VARCHAR(50) NOT NULL,           -- e.g. login, register, apply
    details    VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- ---------- starting data ----------
INSERT INTO roles (role_name) VALUES ('admin'), ('student'), ('company'), ('supervisor');

-- Default admin account  (email: admin@portal.com  password: admin123)
INSERT INTO users (role_id, name, email, password) VALUES
(1, 'Admin', 'admin@portal.com',
 'pbkdf2:sha256:1000000$q9kKTkMrQZLUSLQp$50cdcb29c2a20385dc20c63bc2735817ce17372aa4c138e4fbd44c8e6d79d698');
