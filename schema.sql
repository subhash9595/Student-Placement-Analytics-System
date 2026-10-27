-- Optional: manual MySQL setup (the app can also create tables via `flask --app app init-db`)
CREATE DATABASE IF NOT EXISTS placement_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE placement_db;

CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    roll_no VARCHAR(30) NOT NULL UNIQUE,
    name VARCHAR(120) NOT NULL,
    email VARCHAR(120),
    department VARCHAR(50) NOT NULL,
    cgpa FLOAT NOT NULL,
    backlogs INT NOT NULL DEFAULT 0,
    aptitude_score FLOAT,
    skills TEXT,
    certifications TEXT,
    internships INT NOT NULL DEFAULT 0,
    internship_details TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_students_department (department)
);

CREATE TABLE IF NOT EXISTS placements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'eligible',
    company VARCHAR(120),
    job_role VARCHAR(120),
    package_lpa FLOAT,
    recruitment_year INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_placements_student FOREIGN KEY (student_id)
        REFERENCES students(id) ON DELETE CASCADE,
    INDEX idx_placements_status (status),
    INDEX idx_placements_company (company),
    INDEX idx_placements_year (recruitment_year)
);
