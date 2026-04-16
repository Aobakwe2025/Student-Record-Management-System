from etl.extract import extract_csv
from etl.transform import (
	transform_students,
	transform_courses,
	transform_enrollments,
	transform_grades,
	transform_attendance
)
from etl.load import load_table
from etl.logger import logger

def run():
	logger.info('=' * 55)
	logger.info('  ETL PIPELINE STARTING')
	logger.info('=' * 55)

	# ── EXTRACT ────────────────────────────────────────────────────
	logger.info('--- EXTRACT PHASE ---')
	raw_students    = extract_csv('data/raw/students.csv')
	raw_courses     = extract_csv('data/raw/courses.csv')
	raw_enrollments = extract_csv('data/raw/enrollments.csv')
	raw_grades      = extract_csv('data/raw/grades.csv')
	raw_attendance  = extract_csv('data/raw/attendance.csv')

	# ── TRANSFORM ──────────────────────────────────────────────────
	logger.info('--- TRANSFORM PHASE ---')
	students    = transform_students(raw_students)
	courses     = transform_courses(raw_courses)
	enrollments = transform_enrollments(raw_enrollments)
	grades      = transform_grades(raw_grades)
	attendance  = transform_attendance(raw_attendance)

	# ── LOAD ───────────────────────────────────────────────────────
	# Order matters: load parents before children (FK dependencies)
	logger.info('--- LOAD PHASE ---')

	load_table(
		students, 'students',
		['student_id', 'first_name', 'last_name', 'email',
		 'date_of_birth', 'major', 'enrollment_year'],
		'student_id'
	)

	load_table(
		courses, 'courses',
		['course_id', 'course_name', 'credits', 'department'],
		'course_id'
	)

	load_table(
		enrollments, 'enrollments',
		['enrollment_id', 'student_id', 'course_id', 'enrollment_date'],
		'enrollment_id'
	)

	load_table(
		grades, 'grades',
		['grade_id', 'enrollment_id', 'assignment_score',
		 'exam_score', 'final_grade'],
		'grade_id'
	)

	load_table(
		attendance, 'attendance',
		['attendance_id', 'enrollment_id', 'class_date', 'status'],
		'attendance_id'
	)

	logger.info('=' * 55)
	logger.info('  ETL PIPELINE COMPLETE')
	logger.info('=' * 55)

if __name__ == '__main__':
	run()