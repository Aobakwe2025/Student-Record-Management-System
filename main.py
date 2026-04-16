import argparse
import csv
import sys
from datetime import date, datetime

try:
    import psycopg2
    from psycopg2 import sql
except ImportError:
    print("Error: psycopg2 is not installed. Run:  pip install psycopg2-binary")
    sys.exit(1)


# =============================================================================
# DATABASE CONNECTION
# =============================================================================

DB_CONFIG = {
    "host":     "localhost",
    "port":     5432,
    "dbname":   "student_records_db",
    "user":     "app_user",
    "password": "MyAPPUserPassword",
}


def get_connection():
    """Return a psycopg2 connection. Exits with a clear message on failure."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.OperationalError as e:
        print(f"[ERROR] Could not connect to the database:\n  {e}")
        print("\nCheck that PostgreSQL is running and that DB_CONFIG is correct.")
        sys.exit(1)


# =============================================================================
# HELPERS
# =============================================================================

def prompt(label, required=True, value_type=str, choices=None):
    """
    Interactively prompt the user for a value.
    - required: re-prompts until a non-empty value is entered.
    - value_type: cast the input (e.g. int, float).
    - choices: tuple of valid string values; re-prompts if not matched.
    """
    while True:
        raw = input(f"  {label}: ").strip()
        if not raw:
            if required:
                print(f"    [!] This field is required.")
                continue
            else:
                return None
        if choices and raw not in choices:
            print(f"    [!] Must be one of: {', '.join(choices)}")
            continue
        try:
            return value_type(raw)
        except (ValueError, TypeError):
            print(f"    [!] Expected {value_type.__name__}, got: {raw!r}")


def confirm(question):
    """Ask a yes/no question. Returns True for 'y'."""
    ans = input(f"  {question} [y/n]: ").strip().lower()
    return ans == "y"


def print_table(rows, headers):
    """Print a list of tuples as a plain-text table."""
    if not rows:
        print("  (no results)")
        return
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))
    sep = "+-" + "-+-".join("-" * w for w in col_widths) + "-+"
    fmt = "| " + " | ".join(f"{{:<{w}}}" for w in col_widths) + " |"
    print(sep)
    print(fmt.format(*headers))
    print(sep)
    for row in rows:
        print(fmt.format(*[str(c) if c is not None else "" for c in row]))
    print(sep)


# =============================================================================
# COMMAND: add-student
# =============================================================================

def cmd_add_student(_args):
    """Interactively add a new student to the students table."""
    print("\n=== Add New Student ===")
    first_name = prompt("First name")
    last_name  = prompt("Last name")
    email      = prompt("Email")
    dob_raw    = prompt("Date of birth (YYYY-MM-DD)", required=False)
    major      = prompt("Major", required=False)

    dob = None
    if dob_raw:
        try:
            dob = datetime.strptime(dob_raw, "%Y-%m-%d").date()
        except ValueError:
            print("[ERROR] Invalid date format. Expected YYYY-MM-DD.")
            return

    print(f"\n  Name:  {first_name} {last_name}")
    print(f"  Email: {email}")
    print(f"  DOB:   {dob or 'not provided'}")
    print(f"  Major: {major or 'not provided'}")

    if not confirm("Save this student?"):
        print("  Cancelled.")
        return

    query = """
        INSERT INTO students (first_name, last_name, email, date_of_birth, major)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING student_id;
    """
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(query, (first_name, last_name, email, dob, major))
                student_id = cur.fetchone()[0]
        print(f"\n[OK] Student added with ID: {student_id}")
    except psycopg2.errors.UniqueViolation:
        print(f"[ERROR] A student with email '{email}' already exists.")
    except psycopg2.Error as e:
        print(f"[ERROR] Database error:\n  {e}")
    finally:
        conn.close()


# =============================================================================
# COMMAND: enroll
# =============================================================================

def cmd_enroll(_args):
    """Enroll a student into a course by calling the enroll_student procedure."""
    print("\n=== Enroll Student in Course ===")
    student_id = prompt("Student ID", value_type=int)
    course_id  = prompt("Course ID",  value_type=int)

    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.callproc("enroll_student", [student_id, course_id])
        print(f"\n[OK] Enrollment processed for student {student_id} / course {course_id}.")
    except psycopg2.Error as e:
        # Strip the SQLSTATE prefix for a cleaner message
        print(f"[ERROR] {e.pgerror.strip() if e.pgerror else e}")
    finally:
        conn.close()


# =============================================================================
# COMMAND: record-grade
# =============================================================================

def cmd_record_grade(_args):
    """Record or update a grade entry for an enrollment."""
    print("\n=== Record Grade ===")
    enrollment_id    = prompt("Enrollment ID",    value_type=int)
    assessment_name  = prompt("Assessment name  (e.g. 'Midterm', 'Assignment 1')")
    assignment_score = prompt("Assignment score (0–100, leave blank to skip)", required=False, value_type=float)
    exam_score       = prompt("Exam score       (0–100, leave blank to skip)", required=False, value_type=float)
    final_grade      = prompt("Final grade      (0–100, leave blank to skip)", required=False, value_type=float)

    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.callproc(
                    "record_grade",
                    [enrollment_id, assessment_name, assignment_score, exam_score, final_grade],
                )
        print(f"\n[OK] Grade recorded for enrollment {enrollment_id} / assessment '{assessment_name}'.")
    except psycopg2.Error as e:
        print(f"[ERROR] {e.pgerror.strip() if e.pgerror else e}")
    finally:
        conn.close()


# =============================================================================
# COMMAND: mark-attendance
# =============================================================================

def cmd_mark_attendance(_args):
    """Mark a student's attendance for a session."""
    print("\n=== Mark Attendance ===")
    enrollment_id = prompt("Enrollment ID", value_type=int)
    date_raw      = prompt("Session date (YYYY-MM-DD)", required=False) or str(date.today())
    status        = prompt("Status", choices=("present", "absent", "late"))

    try:
        session_date = datetime.strptime(date_raw, "%Y-%m-%d").date()
    except ValueError:
        print("[ERROR] Invalid date format. Expected YYYY-MM-DD.")
        return

    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.callproc("mark_attendance", [enrollment_id, session_date, status])
        print(f"\n[OK] Attendance marked: enrollment {enrollment_id}, {session_date}, '{status}'.")
    except psycopg2.Error as e:
        print(f"[ERROR] {e.pgerror.strip() if e.pgerror else e}")
    finally:
        conn.close()


# =============================================================================
# COMMAND: export-report
# =============================================================================

def cmd_export_report(args):
    """
    Export a CSV report from the student_report view.
    Optional filters:
        --student-id   filter to one student
        --course-code  filter to one course
    """
    print("\n=== Export Report ===")

    # Build query dynamically based on optional filters
    base_query = "SELECT * FROM student_report"
    conditions = []
    params = []

    if args.student_id:
        conditions.append("student_id = %s")
        params.append(args.student_id)
    if args.course_code:
        conditions.append("course_code = %s")
        params.append(args.course_code)

    if conditions:
        base_query += " WHERE " + " AND ".join(conditions)
    base_query += " ORDER BY last_name, course_code, assessment_name;"

    # Default filename: report_YYYYMMDD.csv
    filename = args.output or f"report_{date.today().strftime('%Y%m%d')}.csv"

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(base_query, params)
            rows = cur.fetchall()
            headers = [desc[0] for desc in cur.description]

        if not rows:
            print("  No records match the given filters.")
            return

        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)

        print(f"\n[OK] Report exported: {filename}  ({len(rows)} rows)")

        # Preview first 5 rows in the terminal
        print(f"\nPreview (first {min(5, len(rows))} rows):")
        print_table(rows[:5], headers)

    except psycopg2.Error as e:
        print(f"[ERROR] {e.pgerror.strip() if e.pgerror else e}")
    finally:
        conn.close()


# =============================================================================
# ARGUMENT PARSER
# =============================================================================

def build_parser():
    parser = argparse.ArgumentParser(
        prog="cli.py",
        description="Student Records Management System — CLI",
    )
    subparsers = parser.add_subparsers(dest="command", metavar="COMMAND")
    subparsers.required = True

    # add-student
    subparsers.add_parser(
        "add-student",
        help="Add a new student (interactive prompts)",
    ).set_defaults(func=cmd_add_student)

    # enroll
    subparsers.add_parser(
        "enroll",
        help="Enroll a student into a course (interactive prompts)",
    ).set_defaults(func=cmd_enroll)

    # record-grade
    subparsers.add_parser(
        "record-grade",
        help="Record or update a grade for an enrollment (interactive prompts)",
    ).set_defaults(func=cmd_record_grade)

    # mark-attendance
    subparsers.add_parser(
        "mark-attendance",
        help="Mark attendance for a session (interactive prompts)",
    ).set_defaults(func=cmd_mark_attendance)

    # export-report
    export_p = subparsers.add_parser(
        "export-report",
        help="Export the student report view to a CSV file",
    )
    export_p.add_argument(
        "--student-id", type=int, default=None,
        metavar="ID",
        help="Filter report to a single student by ID",
    )
    export_p.add_argument(
        "--course-code", type=str, default=None,
        metavar="CODE",
        help="Filter report to a single course by code (e.g. CS101)",
    )
    export_p.add_argument(
        "--output", type=str, default=None,
        metavar="FILE",
        help="Output filename (default: report_YYYYMMDD.csv)",
    )
    export_p.set_defaults(func=cmd_export_report)

    return parser


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)
