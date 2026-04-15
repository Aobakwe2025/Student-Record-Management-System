import csv
import os
import random
from datetime import date, timedelta
from faker import Faker

fake = Faker()
random.seed(42)

MAJORS = [
    'Computer Science', 'Information Technology', 'Mathematics',
    'Physics', 'Business Administration', 'Electrical Engineering'
]

# ── Students ───────────────────────────────────────────────────────────────────
students = []
for i in range(1, 301):
    dob = fake.date_of_birth(minimum_age=17, maximum_age=25)
    students.append({
        'student_id': f'STU{i:04d}',
        'first_name': fake.first_name(),
        'last_name': fake.last_name(),
        'email': fake.unique.email(),
        'date_of_birth': dob,
        'major': random.choice(MAJORS),
        'enrollment_year': random.randint(2020, 2024)
    })

# ── Courses ────────────────────────────────────────────────────────────────────
course_names = [
    'Introduction to Programming', 'Database Systems', 'Data Structures',
    'Algorithms', 'Web Development', 'Machine Learning', 'Linear Algebra',
    'Statistics', 'Operating Systems', 'Computer Networks',
    'Software Engineering', 'Cybersecurity', 'Cloud Computing',
    'Mobile Development', 'Artificial Intelligence', 'Calculus I',
    'Calculus II', 'Discrete Mathematics', 'Computer Architecture',
    'Digital Logic', 'Project Management', 'Business Analytics',
    'Data Mining', 'Computer Graphics', 'Human-Computer Interaction'
]
courses = []
for i, name in enumerate(course_names, 1):
    courses.append({
        'course_id': f'CRS{i:03d}',
        'course_name': name,
        'credits': random.choice([2, 3, 4]),
        'department': random.choice(['CS', 'IT', 'MATH', 'ENG', 'BUS'])
    })

# ── Enrollments ────────────────────────────────────────────────────────────────
enrollments = []
enroll_id = 1
enrolled_pairs = set()
for student in students:
    num_courses = random.randint(3, 6)
    chosen = random.sample(courses, num_courses)
    for course in chosen:
        pair = (student['student_id'], course['course_id'])
        if pair not in enrolled_pairs:
            enrolled_pairs.add(pair)
            enrollments.append({
                'enrollment_id': f'ENR{enroll_id:05d}',
                'student_id': student['student_id'],
                'course_id': course['course_id'],
                'enrollment_date': fake.date_between(
                    start_date=date(2023, 1, 1),
                    end_date=date(2024, 9, 1)
                )
            })
            enroll_id += 1

# ── Grades ─────────────────────────────────────────────────────────────────────
grades = []
for i, enr in enumerate(enrollments, 1):
    assignment = round(random.uniform(40, 100), 2)
    exam       = round(random.uniform(40, 100), 2)
    final      = round(assignment * 0.4 + exam * 0.6, 2)
    grades.append({
        'grade_id': f'GRD{i:05d}',
        'enrollment_id': enr['enrollment_id'],
        'assignment_score': assignment,
        'exam_score': exam,
        'final_grade': final
    })

# ── Attendance ─────────────────────────────────────────────────────────────────
attendance = []
att_id = 1
for enr in enrollments:
    for week in range(1, 13):
        class_date = date(2024, 1, 15) + timedelta(weeks=week)
        status = random.choices(
            ['Present', 'Absent', 'Late'],
            weights=[75, 15, 10]
        )[0]
        attendance.append({
            'attendance_id': f'ATT{att_id:06d}',
            'enrollment_id': enr['enrollment_id'],
            'class_date': class_date,
            'status': status
        })
        att_id += 1

# ── Save to CSV ────────────────────────────────────────────────────────────────
def save_csv(data, filename):
    os.makedirs('data/raw', exist_ok=True)
    filepath = f'data/raw/{filename}'
    with open(filepath, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    print(f'Saved {len(data):,} rows → {filepath}')

save_csv(students,    'students.csv')
save_csv(courses,     'courses.csv')
save_csv(enrollments, 'enrollments.csv')
save_csv(grades,      'grades.csv')
save_csv(attendance,  'attendance.csv')

print('\nData generation complete.')