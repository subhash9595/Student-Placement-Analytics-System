"""Generate a realistic synthetic dataset: python sample_data/generate_sample_data.py"""
import csv
import random
from pathlib import Path

random.seed(42)
DEPTS = {"CSE": 45, "IT": 30, "ECE": 30, "EEE": 20, "MECH": 20, "CIVIL": 15}
SKILLS = {
    "CSE": ["Python", "Java", "SQL", "C++", "JavaScript", "React", "Git", "Machine Learning", "AWS"],
    "IT": ["Python", "Java", "SQL", "JavaScript", "HTML", "CSS", "Git", "Node.js", "MySQL"],
    "ECE": ["C", "Python", "Embedded Systems", "VLSI", "MATLAB", "IoT", "SQL"],
    "EEE": ["MATLAB", "PLC", "Python", "AutoCAD", "Embedded Systems", "Excel"],
    "MECH": ["AutoCAD", "SolidWorks", "MATLAB", "Excel", "Python"],
    "CIVIL": ["AutoCAD", "STAAD Pro", "Excel", "Revit", "Python"],
}
CERTS = ["AWS Cloud Practitioner", "NPTEL Python", "Oracle Java SE", "Google Data Analytics",
         "Azure Fundamentals", "Cisco CCNA", "NPTEL Embedded Systems"]
COMPANIES = {
    "CSE": [("TCS", "Systems Engineer", 3.6, 4.5), ("Infosys", "Systems Engineer", 3.6, 5), ("Wipro", "Project Engineer", 3.5, 4.5),
            ("Accenture", "Associate Software Engineer", 4.5, 6.5), ("Amazon", "SDE-1", 14, 32),
            ("Deloitte", "Analyst", 6, 9), ("Zoho", "Member Technical Staff", 6, 10)],
    "IT": [("TCS", "Systems Engineer", 3.6, 4.5), ("Infosys", "Systems Engineer", 3.6, 5), ("Cognizant", "Programmer Analyst", 4, 5.5),
           ("Capgemini", "Analyst", 4, 5), ("Accenture", "Associate Software Engineer", 4.5, 6.5), ("Zoho", "Member Technical Staff", 6, 10)],
    "ECE": [("Qualcomm", "Hardware Engineer", 10, 18), ("TCS", "Systems Engineer", 3.6, 4.5),
            ("Tech Mahindra", "Network Engineer", 3.5, 5), ("Bosch", "Embedded Engineer", 5, 8)],
    "EEE": [("Siemens", "Graduate Engineer Trainee", 5, 7.5), ("L&T", "Engineer Trainee", 4, 6), ("Schneider Electric", "Associate Engineer", 5, 8)],
    "MECH": [("Tata Motors", "Graduate Engineer Trainee", 4.5, 7), ("Mahindra", "Engineer Trainee", 4, 6.5), ("L&T", "Engineer Trainee", 4, 6)],
    "CIVIL": [("L&T", "Site Engineer", 4, 6), ("Shapoorji Pallonji", "Engineer Trainee", 3.8, 5.5), ("Tata Projects", "Site Engineer", 4, 6)],
}
FIRST = ["Aarav", "Vivaan", "Aditya", "Sai", "Arjun", "Karthik", "Rohit", "Ravi", "Vikram", "Suresh", "Ananya", "Diya", "Priya",
         "Sneha", "Lakshmi", "Divya", "Harini", "Meera", "Pooja", "Kavya", "Nikhil", "Teja", "Charan", "Manoj", "Bhavana"]
LAST = ["Reddy", "Sharma", "Kumar", "Naidu", "Rao", "Varma", "Patel", "Iyer", "Singh", "Chowdary", "Prasad", "Gupta"]

rows, n = [], 0
for dept, count in DEPTS.items():
    for _ in range(count):
        n += 1
        cgpa = round(min(9.9, max(5.0, random.gauss(7.4, 1.0))), 2)
        backlogs = 0 if random.random() < 0.8 else random.randint(1, 4)
        aptitude = round(min(98, max(25, random.gauss(cgpa * 8 - 2, 12))), 1)
        pool = SKILLS[dept]
        skills = random.sample(pool, k=min(len(pool), random.randint(1, 6)))
        certs = random.sample(CERTS, k=random.choice([0, 0, 1, 1, 2]))
        interns = random.choices([0, 1, 2], weights=[45, 40, 15])[0]
        year = random.choice([2022, 2023, 2024, 2025])
        score = (cgpa - 6) * 0.9 + (aptitude - 50) / 25 + len(skills) * 0.35 + interns * 0.7 \
            + len(certs) * 0.3 - backlogs * 0.9 + random.gauss(0, 0.8)
        status, company, role, pkg = "unplaced", "", "", ""
        if score > 3.2:
            status = "selected"
            pool_c = COMPANIES[dept]
            top = score > 5.2
            comp, role, lo, hi = random.choice(pool_c[-3:] if top else pool_c)
            company, pkg = comp, round(random.uniform(lo, hi), 2)
        elif score > 2.4:
            status = "shortlisted"
            company = random.choice(COMPANIES[dept])[0]
            role = ""
        elif cgpa >= 6.0 and backlogs == 0:
            status = "eligible"
        name = f"{random.choice(FIRST)} {random.choice(LAST)}"
        rows.append({
            "roll_no": f"{dept}{year - 4}{n:03d}", "name": name,
            "email": f"{name.lower().replace(' ', '.')}{n}@college.edu", "department": dept,
            "cgpa": cgpa, "backlogs": backlogs, "aptitude_score": aptitude,
            "skills": ", ".join(skills), "certifications": ", ".join(certs), "internships": interns,
            "internship_details": "Summer internship" if interns else "",
            "status": status, "company": company, "job_role": role, "package_lpa": pkg,
            "recruitment_year": year})

out = Path(__file__).with_name("placement_sample.csv")
with out.open("w", newline="", encoding="utf-8") as fh:
    writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
print(f"Wrote {len(rows)} rows to {out}")
