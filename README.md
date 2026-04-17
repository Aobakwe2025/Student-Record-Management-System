# 🎓 Student Management System

A full-stack student data management platform built with PostgreSQL, Python, and a CLI interface. The system handles student records, course enrollments, grade tracking, and attendance — with a complete ETL pipeline for data ingestion and a SQL-powered reporting layer.

Database Deployment Link: https://dashboard.render.com/d/dpg-d7gghpdckfvc73e5srlg-a
---

## 👥 Team

| Member | Role |
|---|---|
| **Khayalethu Shezi** | Database Design & Infrastructure (Phases 1, 2, 7, 8) |
| **Nomdumiso Mtshilibe** | ETL Pipeline & Sample Data (Phases 3, 4) |
| **Aobakwe Modillane** | SQL, Python CLI & Documentation (Phases 5, 6, 8-docs) |

---

## 📋 Project Overview

### Phase Breakdown

**Phase 1 & 2 — Database Design** *(Khayalethu)*
- Entity-Relationship Diagram (ERD) normalised to 3NF
- PostgreSQL/MySQL schema with constraints and indexes
- User permissions and role-based access

**Phase 3 & 4 — ETL Pipeline** *(Nomdumiso)*
- Synthetic data generation using Faker (100–500 students, 20–30 courses, enrollments, grades, attendance)
- Python ETL pipeline: extract from CSV/Excel/JSON → transform → load
- Handles nulls, email validation, GPA calculation, attendance checks
- Batch inserts, error logging, duplicate detection, and rollback support

**Phase 5 & 6 — SQL & CLI** *(Aobakwe)*
- SQL queries, stored procedures, and views
- Python CLI: add students, enroll in courses, record grades, mark attendance, export reports

**Phase 7 & 8 — Testing, Deployment & Docs** *(Khayalethu + Aobakwe)*
- Validation and test cases
- Deployment to Render or Railway
- ERD writeup, architecture overview, user guide, and PowerPoint slides

---

## 🗂️ Repository Structure

```
student-management-system/
├── db/
│   ├── schema.sql          # Table definitions, constraints, indexes
│   ├── permissions.sql     # User roles and access control
│   └── erd/                # ERD diagrams and writeup
├── etl/
│   ├── generate_data.py    # Faker-based sample data generation
│   ├── extract.py          # CSV/Excel/JSON extraction
│   ├── transform.py        # Cleaning, validation, GPA calc
│   └── load.py             # Batch inserts with error handling
├── sql/
│   ├── queries.sql         # Analytical queries
│   ├── procedures.sql      # Stored procedures
│   └── views.sql           # Reporting views
├── cli/
│   └── main.py             # Python CLI entry point
├── tests/
│   └── test_cases.sql      # Validation and test queries
├── docs/
│   ├── architecture.md     # System architecture overview
│   ├── user_guide.md       # End-user instructions
│   └── slides/             # PowerPoint presentation
├── data/
│   └── sample/             # Generated CSV/Excel/JSON files
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup Instructions

### Prerequisites

- Python 3.9+
- PostgreSQL 14+ (or MySQL 8+)
- pip

### 1. Clone the Repository

```bash
git clone https://github.com/<your-org>/student-management-system.git
cd student-management-system
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up the Database

Connect to your PostgreSQL instance and run the schema:

```bash
psql -U <your_user> -d <your_database> -f db/schema.sql
psql -U <your_user> -d <your_database> -f db/permissions.sql
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=student_db
DB_USER=your_user
DB_PASSWORD=your_password
```

### 5. Generate Sample Data

```bash
python etl/generate_data.py
```

This creates CSV/JSON files in `data/sample/` with students, courses, enrollments, grades, and attendance.

### 6. Run the ETL Pipeline

```bash
python etl/extract.py
python etl/transform.py
python etl/load.py
```

### 7. Launch the CLI

```bash
python cli/main.py
```

---

## 💻 CLI Usage

```
Commands:
  add-student         Add a new student record
  enroll              Enroll a student in a course
  record-grade        Record a grade for an enrollment
  mark-attendance     Mark attendance for a student
  export-report       Export a report (CSV/Excel)
  --help              Show help for any command
```

Example:

```bash
python cli/main.py add-student --name "Jane Doe" --email "jane@example.com"
python cli/main.py enroll --student-id 42 --course-id 7
python cli/main.py export-report --type attendance --format csv
```

---

## 🗄️ Database Schema (Summary)

| Table | Description |
|---|---|
| `students` | Student profiles (name, email, DOB, etc.) |
| `courses` | Course catalogue (code, name, credits) |
| `enrollments` | Student–course relationships |
| `grades` | Grade records per enrollment |
| `attendance` | Per-session attendance records |

See `db/schema.sql` for full definitions and `docs/architecture.md` for the ERD writeup.

---

## 🧪 Running Tests

```bash
psql -U <your_user> -d <your_database> -f tests/test_cases.sql
```

---

## 🚀 Deployment

The application is configured for deployment on **Render** or **Railway**.

1. Push the repo to GitHub.
2. Connect your Render/Railway project to the repo.
3. Add environment variables in the platform dashboard.
4. Run database migrations via the shell using the schema files.

---

## 🤝 Contributing

All three members share responsibility for:
- Maintaining the GitHub repository
- Code reviews on each other's pull requests
- Integration testing once all components are connected
- Final submission packaging

**Branching convention:** `feature/<member-initials>/<short-description>`  
Example: `feature/ks/db-schema`, `feature/nm/etl-pipeline`, `feature/am/cli`

> ⚠️ **Critical dependency:** The database schema (`db/schema.sql`) must be committed first — ideally by day 2–3 — before ETL loading and SQL work can proceed.

---

## 📄 License

This project was developed as part of a group academic assignment. All rights reserved by the authors.
