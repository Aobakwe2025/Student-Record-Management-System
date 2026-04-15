import re
import pandas as pd
from etl.logger import logger

def transform_students(df):
	logger.info('Transforming students...')
	before = len(df)

	# Remove duplicates
	df = df.drop_duplicates(subset=['student_id'])
	df = df.drop_duplicates(subset=['email'])

	# Drop rows missing required fields
	df = df.dropna(subset=['student_id', 'first_name', 'last_name', 'email'])

	# Validate email format
	email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w{2,}$'
	valid_email = df['email'].apply(
		lambda e: bool(re.match(email_pattern, str(e)))
	)
	df = df[valid_email]

	# Standardise formatting
	df['first_name'] = df['first_name'].str.strip().str.title()
	df['last_name']  = df['last_name'].str.strip().str.title()
	df['email']      = df['email'].str.strip().str.lower()

	logger.info(f'  Students: {before} → {len(df)} rows (dropped {before - len(df)})')
	return df

def transform_courses(df):
	logger.info('Transforming courses...')
	before = len(df)

	df = df.drop_duplicates(subset=['course_id'])
	df = df.dropna(subset=['course_id', 'course_name'])
	df['course_name'] = df['course_name'].str.strip().str.title()
	df['department']  = df['department'].str.strip().str.upper()

	logger.info(f'  Courses: {before} → {len(df)} rows (dropped {before - len(df)})')
	return df

def transform_enrollments(df):
	logger.info('Transforming enrollments...')
	before = len(df)

	df = df.drop_duplicates(subset=['enrollment_id'])
	df = df.dropna(subset=['enrollment_id', 'student_id', 'course_id'])
	df['enrollment_date'] = pd.to_datetime(df['enrollment_date']).dt.date

	logger.info(f'  Enrollments: {before} → {len(df)} rows (dropped {before - len(df)})')
	return df

def transform_grades(df):
	logger.info('Transforming grades...')
	before = len(df)

	df = df.drop_duplicates(subset=['grade_id'])
	df = df.dropna(subset=['enrollment_id', 'assignment_score', 'exam_score'])

	# Enforce valid score range 0–100
	for col in ['assignment_score', 'exam_score', 'final_grade']:
		df = df[(df[col] >= 0) & (df[col] <= 100)]

	# Calculate GPA points (4.0 scale) from final grade
	def to_gpa(score):
		if score >= 90: return 4.0
		elif score >= 80: return 3.0
		elif score >= 70: return 2.0
		elif score >= 60: return 1.0
		else: return 0.0

	df['gpa_points'] = df['final_grade'].apply(to_gpa)

	logger.info(f'  Grades: {before} → {len(df)} rows (dropped {before - len(df)})')
	return df

def transform_attendance(df):
	logger.info('Transforming attendance...')
	before = len(df)

	df = df.drop_duplicates(subset=['attendance_id'])
	df = df.dropna(subset=['enrollment_id', 'class_date', 'status'])
	df['class_date'] = pd.to_datetime(df['class_date']).dt.date
	df['status']     = df['status'].str.strip().str.title()

	valid_statuses = ['Present', 'Absent', 'Late']
	df = df[df['status'].isin(valid_statuses)]

	logger.info(f'  Attendance: {before} → {len(df)} rows (dropped {before - len(df)})')
	return df