# Student Placement Data Analysis System

A Flask web application (SQLite by default; MySQL is optional) that stores student placement data and turns it into analytics:
placement rates, company and salary trends, skill demand, academic correlations, and
rule-based preparation advice for students who are not yet placed.

## Features
Student and placement CRUD, interactive dashboard (Chart.js), department/year/company analysis,
skills and skill-combination analysis, CGPA-vs-outcome correlation, preparation insights,
filtered CSV export, validated CSV import, and Matplotlib charts rendered on the server.

## Project structure
```
placement-analytics/
├── app.py                 # Flask app factory + CLI commands (init-db, seed)
├── config.py              # Settings (.env) and configurable PREP_RULES
├── constants.py           # Placement status values
├── extensions.py          # SQLAlchemy instance
├── models.py              # Student and Placement tables
├── routes/                # dashboard, students, placements, analytics, insights, data_io
├── services/              # data loading, analytics (pandas/NumPy), charts, import, export, validation
├── templates/             # Jinja2 + Bootstrap pages
├── static/                # CSS and Chart.js helpers
├── sql/schema.sql         # Optional manual MySQL setup
├── sample_data/           # 160-row sample CSV + generator script
└── tests/                 # pytest unit tests for analytics and validation
```

## Run it (Windows / VS Code, SQLite default)
1. Open this folder in VS Code (the folder containing `app.py`).
2. In the terminal, create and activate a virtual environment:
   ```
   python -m venv .venv
   .venv\\Scripts\\Activate.ps1
   ```
3. Install dependencies:
   ```
   python -m pip install -r requirements.txt
   ```
4. The included `.env` uses `DATABASE_URL=sqlite:///dev.db`, so MySQL is not required.
5. Create tables and load sample data:
   ```
   flask --app app init-db
   flask --app app seed
   ```
6. Start the app:
   ```
   flask --app app run --debug
   ```
7. Open http://127.0.0.1:5000 in your browser.

To use MySQL instead, change `DATABASE_URL` in `.env` to your MySQL connection string.

## Tests
`pytest -q`

## CSV format
Required columns: `roll_no, name, department, cgpa`. Optional: `email, backlogs, aptitude_score, skills,
certifications, internships, internship_details, status, company, job_role, package_lpa, recruitment_year`.
One row per student; `status` is one of eligible, shortlisted, selected, unplaced.

## How outcomes are counted
A student is **placed** if they have at least one `selected` record. Their dashboard status is the best of
their records (selected > shortlisted > eligible > unplaced); a student with no records counts as unplaced.

## Notes
The app has no login, so run it on a trusted network or add authentication before sharing it.
