-- Student Records Management Ssystem --

-- Create the database --
CREATE DATABASE student_records_db;

-- Connect to database --
\c student_records_db;

---==================================================================---
-- TABLE DEFINITIONS --
-- Creation order: students, courses, enrollments, grades, attendance
---==================================================================---

-- Students 
-- Root entity. No foreign key dependencies
CREATE TABLE IF NOT EXISTS students (
    student_id      SERIAL          PRIMARY KEY,
    first_name      VARCHAR(100)    NOT NULL,
    last_name       VARCHAR(100)    NOT NULL,
    email           VARCHAR(150)    NOT NULL UNIQUE,
    date_of_birth   DATE,
    major           VARCHAR(100)
);

-- Courses
-- Root entity. No foreign key dependencies
CREATE TABLE IF NOT EXISTS courses (
    course_id       SERIAL          PRIMARY KEY,
    course_code     VARCHAR(20)     NOT NULL UNIQUE,
    course_name     VARCHAR(150)    NOT NULL,
    credits         INT             NOT NULL CHECK (credits BETWEEN 1 AND 30),
    lecturer        VARCHAR(100)
);

-- Enrollments
-- 'UNIQUE' prevents a student from enrolling in the same course twice
-- Resolves the M:N relationship
CREATE TABLE IF NOT EXISTS enrollments (
    enrollment_id   SERIAL          PRIMARY KEY,
    student_id      INT             NOT NULL
                                    REFERENCES students(student_id)
                                    ON DELETE CASCADE,
    course_id       INT             NOT NULL
                                    REFERENCES courses(course_id)
                                    ON DELETE CASCADE,
    enrollment_date DATE            NOT NULL DEFAULT CURRENT_DATE,
    UNIQUE(student_id, course_id)
);

-- Grades
-- Allows multiple assessment records per enrollment.
CREATE TABLE EIF NOT EXISTS grades (
    grade_id            SERIAL          PRIMARY KEY,
    enrollment_id       INT             NOT NULL
                                        REFERENCES enrollments(enrollment_id)
                                        ON DELETE CASCADE,
    assessment_name     VARCHAR(100)    NOT NULL,
    assignment_score    DECIMAL(5,2)    CHECK (assignment_score BETWEEN 0 AND 100),
    exam_score          DECIMAL(5,2)    CHECK (exam_score BETWEEN 0 AND 100),
    final_grade         DECIMAL(5,2)    CHECK (final_grade BETWEEN 0 AND 100)
);

-- Attendance
-- One record per student, per class via enrollment
-- 'Status' is constrained to exactly 3 valid values which are case sensitive.
CREATE TABLE IF NOT EXISTS attendance (
    attendance_id       SERIAL          PRIMARY KEY,
    enrollment_id       INT             NOT NULL
                                        REFERENCES enrollments(enrollment_id)
                                        ON REFERENCES CASCADE,
    session_date        DATE            NOT NULL,
    status              VARCHAR(20)     NOT NULL
                                        CHECK (status IN('present', 'absent', 'late'))
);

---==================================================================---
-- INDEXES --
---==================================================================---

-- Foreign Key Indexes
CREATE INDEX idx_enrollments_student_id     ON enrollments(student_id);
CREATE INDEX idx_enrollments_course_id      ON enrollments(course_id);
CREATE INDEX idx_grades_enrollments_id      ON grades(enrollment_id);
CREATE INDEX idx_attendance_enrollment_id   ON attendance(enrollment_id);

-- Query-pattern Indexes
CREATE INDEX idx_attendance_session_date    ON attendance(session_date);
CREATE INDEX idx_grades_final_grade         ON grades(final_grade);

-- Composite index: attendance rate queries
CREATE INDEX idx_attendance_enrollment_date ON attendance(enrollment_id, session_date);

---==================================================================---
-- ROLES & PERMISSIONS --
---==================================================================---

-- Create roles
CREATE ROLE db_admin        LOGIN PASSWORD 'Password';
CREATE ROLE etl_user        LOGIN PASSWORD 'MyETLPassword';
CREATE ROLE read_only       LOGIN PASSWORD 'MyREADOnlyPassword';
CREATE ROLE app_user        LOGIN PASSWORD 'MyAPPUserPassword';

-- db_admin: full control permissions
GRANT ALL PRIVILEGES ON DATABASE student_records_db TO db_admin;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO  db_admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO db_admin;

-- etl_user: load & update data (ETL pipeline)
GRANT INSERT, UPDATE, SELECT ON ALL TABLES IN SCHEMA public TO etl_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO etl_user;

-- read_only: SELECT only (SQL development)
GRANT SELECT ON ALL TABLES IN SCHEMA public TO read_only;

-- app_user: full CRUD 
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_user;

-- Default Privileges - Applies to all tables created after this script
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT INSERT, UPDATE, SELECT ON TABLES TO etl_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT USAGE, SELECT ON SEQUENCES TO etl_user;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT ON TABLES TO read_only;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT USAGE, SELECT ON SEQUENCES TO app_user;

---==================================================================---
-- VERIFICATION QUERIES
---==================================================================---

-- Lists all tables
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;

-- Lists all indexes
SELECT indexname, tablename, indexdef
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;

-- Lists all roles
SELECT rolname,rolcanlogin
FROM pg_roles
WHERE rolname IN ('db_admin', 'etl_user', 'read_only', 'app_user');

-- Lists all constraints
SELECT conname, contype, coonrelid::regclass AS table_name
FROM pg_constraint
WHERE conrelid::regclass::text IN (
    'students', 'courses', 'enrollments', 'grades', 'attendance'
)
ORDER BY table_name, contype;
