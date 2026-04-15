-- =================================================================== --
-- Phase 5: SQL Queries, Views & Stored Procedures                     --
-- Student Records Management System                                   --
-- Member C                                                            --
-- =================================================================== --

\c student_records_db;

---==================================================================---
-- SECTION 1: CORE SELECT QUERIES                                     --
---==================================================================---

-- Query 1: All students enrolled in a specific course
-- Usage: Replace the $1 placeholder with a course_id value
SELECT
    s.student_id,
    s.first_name,
    s.last_name,
    s.email,
    c.course_code,
    c.course_name,
    e.enrollment_date
FROM students s
JOIN enrollments e ON s.student_id = e.student_id
JOIN courses c     ON e.course_id  = c.course_id
WHERE c.course_id = 1  -- replace with target course_id
ORDER BY s.last_name, s.first_name;


-- Query 2: All grades for a specific student across all courses
SELECT
    s.first_name,
    s.last_name,
    c.course_code,
    c.course_name,
    g.assessment_name,
    g.assignment_score,
    g.exam_score,
    g.final_grade
FROM students s
JOIN enrollments e ON s.student_id   = e.student_id
JOIN courses c     ON e.course_id    = c.course_id
JOIN grades g      ON e.enrollment_id = g.enrollment_id
WHERE s.student_id = 1  -- replace with target student_id
ORDER BY c.course_code, g.assessment_name;


-- Query 3: Attendance rate per student (all courses)
SELECT
    s.student_id,
    s.first_name,
    s.last_name,
    COUNT(a.attendance_id)                                          AS total_sessions,
    SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END)          AS present_count,
    SUM(CASE WHEN a.status = 'late'    THEN 1 ELSE 0 END)          AS late_count,
    SUM(CASE WHEN a.status = 'absent'  THEN 1 ELSE 0 END)          AS absent_count,
    ROUND(
        SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END)
        * 100.0 / NULLIF(COUNT(a.attendance_id), 0), 2
    )                                                               AS attendance_rate_pct
FROM students s
JOIN enrollments e  ON s.student_id   = e.student_id
JOIN attendance a   ON e.enrollment_id = a.enrollment_id
GROUP BY s.student_id, s.first_name, s.last_name
ORDER BY attendance_rate_pct DESC;


-- Query 4: Full student report — grades + attendance combined
SELECT
    s.student_id,
    s.first_name || ' ' || s.last_name         AS full_name,
    c.course_code,
    c.course_name,
    g.assessment_name,
    g.assignment_score,
    g.exam_score,
    g.final_grade,
    COUNT(a.attendance_id)                      AS total_sessions,
    ROUND(
        SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END)
        * 100.0 / NULLIF(COUNT(a.attendance_id), 0), 2
    )                                           AS attendance_rate_pct
FROM students s
JOIN enrollments e  ON s.student_id    = e.student_id
JOIN courses c      ON e.course_id     = c.course_id
LEFT JOIN grades g  ON e.enrollment_id = g.enrollment_id
LEFT JOIN attendance a ON e.enrollment_id = a.enrollment_id
GROUP BY
    s.student_id, full_name, c.course_code, c.course_name,
    g.assessment_name, g.assignment_score, g.exam_score, g.final_grade
ORDER BY s.last_name, c.course_code;


-- Query 5: Average grade and attendance per course
SELECT
    c.course_id,
    c.course_code,
    c.course_name,
    c.lecturer,
    COUNT(DISTINCT e.student_id)                AS enrolled_students,
    ROUND(AVG(g.final_grade), 2)                AS avg_final_grade,
    ROUND(
        SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END)
        * 100.0 / NULLIF(COUNT(a.attendance_id), 0), 2
    )                                           AS avg_attendance_pct
FROM courses c
LEFT JOIN enrollments e  ON c.course_id     = e.course_id
LEFT JOIN grades g       ON e.enrollment_id = g.enrollment_id
LEFT JOIN attendance a   ON e.enrollment_id = a.enrollment_id
GROUP BY c.course_id, c.course_code, c.course_name, c.lecturer
ORDER BY c.course_code;


---==================================================================---
-- SECTION 2: VIEWS                                                   --
---==================================================================---

-- View 1: student_report
-- A full read-only report of each student's grades and attendance
-- per course. Used by the CLI export command.
CREATE OR REPLACE VIEW student_report AS
SELECT
    s.student_id,
    s.first_name,
    s.last_name,
    s.email,
    s.major,
    c.course_code,
    c.course_name,
    c.lecturer,
    e.enrollment_date,
    g.assessment_name,
    g.assignment_score,
    g.exam_score,
    g.final_grade,
    COUNT(a.attendance_id)                                          AS total_sessions,
    SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END)          AS sessions_present,
    SUM(CASE WHEN a.status = 'late'    THEN 1 ELSE 0 END)          AS sessions_late,
    SUM(CASE WHEN a.status = 'absent'  THEN 1 ELSE 0 END)          AS sessions_absent,
    ROUND(
        SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END)
        * 100.0 / NULLIF(COUNT(a.attendance_id), 0), 2
    )                                                               AS attendance_rate_pct
FROM students s
JOIN enrollments e      ON s.student_id    = e.student_id
JOIN courses c          ON e.course_id     = c.course_id
LEFT JOIN grades g      ON e.enrollment_id = g.enrollment_id
LEFT JOIN attendance a  ON e.enrollment_id = a.enrollment_id
GROUP BY
    s.student_id, s.first_name, s.last_name, s.email, s.major,
    c.course_code, c.course_name, c.lecturer, e.enrollment_date,
    g.assessment_name, g.assignment_score, g.exam_score, g.final_grade;


-- View 2: course_summary
-- Aggregated stats per course: enrollment count, average grade,
-- average attendance. Useful for lecturer/admin dashboards.
CREATE OR REPLACE VIEW course_summary AS
SELECT
    c.course_id,
    c.course_code,
    c.course_name,
    c.credits,
    c.lecturer,
    COUNT(DISTINCT e.student_id)                                    AS enrolled_students,
    ROUND(AVG(g.assignment_score), 2)                               AS avg_assignment_score,
    ROUND(AVG(g.exam_score), 2)                                     AS avg_exam_score,
    ROUND(AVG(g.final_grade), 2)                                    AS avg_final_grade,
    ROUND(
        SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END)
        * 100.0 / NULLIF(COUNT(a.attendance_id), 0), 2
    )                                                               AS avg_attendance_pct
FROM courses c
LEFT JOIN enrollments e  ON c.course_id     = e.course_id
LEFT JOIN grades g       ON e.enrollment_id = g.enrollment_id
LEFT JOIN attendance a   ON e.enrollment_id = a.enrollment_id
GROUP BY c.course_id, c.course_code, c.course_name, c.credits, c.lecturer
ORDER BY c.course_code;


---==================================================================---
-- SECTION 3: STORED PROCEDURES                                       --
---==================================================================---

-- Procedure 1: enroll_student
-- Safely enrolls a student into a course.
-- Raises a notice (not an error) if already enrolled.
CREATE OR REPLACE PROCEDURE enroll_student(
    p_student_id  INT,
    p_course_id   INT
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Check student exists
    IF NOT EXISTS (SELECT 1 FROM students WHERE student_id = p_student_id) THEN
        RAISE EXCEPTION 'Student with ID % does not exist.', p_student_id;
    END IF;

    -- Check course exists
    IF NOT EXISTS (SELECT 1 FROM courses WHERE course_id = p_course_id) THEN
        RAISE EXCEPTION 'Course with ID % does not exist.', p_course_id;
    END IF;

    -- Check not already enrolled
    IF EXISTS (
        SELECT 1 FROM enrollments
        WHERE student_id = p_student_id AND course_id = p_course_id
    ) THEN
        RAISE NOTICE 'Student % is already enrolled in course %.', p_student_id, p_course_id;
        RETURN;
    END IF;

    INSERT INTO enrollments (student_id, course_id)
    VALUES (p_student_id, p_course_id);

    RAISE NOTICE 'Student % successfully enrolled in course %.', p_student_id, p_course_id;
END;
$$;


-- Procedure 2: record_grade
-- Records or updates a grade entry for a given enrollment.
-- If an entry for the same assessment already exists it updates it;
-- otherwise it inserts a new row.
CREATE OR REPLACE PROCEDURE record_grade(
    p_enrollment_id     INT,
    p_assessment_name   VARCHAR(100),
    p_assignment_score  DECIMAL(5,2) DEFAULT NULL,
    p_exam_score        DECIMAL(5,2) DEFAULT NULL,
    p_final_grade       DECIMAL(5,2) DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Check enrollment exists
    IF NOT EXISTS (SELECT 1 FROM enrollments WHERE enrollment_id = p_enrollment_id) THEN
        RAISE EXCEPTION 'Enrollment ID % does not exist.', p_enrollment_id;
    END IF;

    -- Score range validation
    IF p_assignment_score IS NOT NULL AND p_assignment_score NOT BETWEEN 0 AND 100 THEN
        RAISE EXCEPTION 'assignment_score must be between 0 and 100.';
    END IF;
    IF p_exam_score IS NOT NULL AND p_exam_score NOT BETWEEN 0 AND 100 THEN
        RAISE EXCEPTION 'exam_score must be between 0 and 100.';
    END IF;
    IF p_final_grade IS NOT NULL AND p_final_grade NOT BETWEEN 0 AND 100 THEN
        RAISE EXCEPTION 'final_grade must be between 0 and 100.';
    END IF;

    -- Upsert: update if assessment exists, insert if not
    IF EXISTS (
        SELECT 1 FROM grades
        WHERE enrollment_id = p_enrollment_id
          AND assessment_name = p_assessment_name
    ) THEN
        UPDATE grades
        SET assignment_score = COALESCE(p_assignment_score, assignment_score),
            exam_score       = COALESCE(p_exam_score,       exam_score),
            final_grade      = COALESCE(p_final_grade,      final_grade)
        WHERE enrollment_id  = p_enrollment_id
          AND assessment_name = p_assessment_name;

        RAISE NOTICE 'Grade updated for enrollment % / assessment "%".', p_enrollment_id, p_assessment_name;
    ELSE
        INSERT INTO grades (enrollment_id, assessment_name, assignment_score, exam_score, final_grade)
        VALUES (p_enrollment_id, p_assessment_name, p_assignment_score, p_exam_score, p_final_grade);

        RAISE NOTICE 'Grade recorded for enrollment % / assessment "%".', p_enrollment_id, p_assessment_name;
    END IF;
END;
$$;


-- Procedure 3: mark_attendance
-- Records a single attendance entry for an enrollment on a given date.
-- Raises an error if a record for that date already exists.
CREATE OR REPLACE PROCEDURE mark_attendance(
    p_enrollment_id  INT,
    p_session_date   DATE,
    p_status         VARCHAR(20)
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Check enrollment exists
    IF NOT EXISTS (SELECT 1 FROM enrollments WHERE enrollment_id = p_enrollment_id) THEN
        RAISE EXCEPTION 'Enrollment ID % does not exist.', p_enrollment_id;
    END IF;

    -- Validate status value (mirrors the table CHECK constraint)
    IF p_status NOT IN ('present', 'absent', 'late') THEN
        RAISE EXCEPTION 'Invalid status "%". Must be present, absent, or late.', p_status;
    END IF;

    -- Prevent duplicate attendance record for same date
    IF EXISTS (
        SELECT 1 FROM attendance
        WHERE enrollment_id = p_enrollment_id
          AND session_date  = p_session_date
    ) THEN
        RAISE EXCEPTION 'Attendance already recorded for enrollment % on %.', p_enrollment_id, p_session_date;
    END IF;

    INSERT INTO attendance (enrollment_id, session_date, status)
    VALUES (p_enrollment_id, p_session_date, p_status);

    RAISE NOTICE 'Attendance marked: enrollment %, date %, status "%".', p_enrollment_id, p_session_date, p_status;
END;
$$;


---==================================================================---
-- VERIFICATION: confirm views and procedures were created            --
---==================================================================---

-- List views
SELECT table_name AS view_name
FROM information_schema.views
WHERE table_schema = 'public'
ORDER BY table_name;

-- List stored procedures
SELECT routine_name, routine_type
FROM information_schema.routines
WHERE routine_schema = 'public'
  AND routine_type = 'PROCEDURE'
ORDER BY routine_name;
