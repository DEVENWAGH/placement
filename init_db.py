import os
import mysql.connector
from datetime import date

DB_NAME = "placement"
DB_USER = "root"
DB_PASS = "root"
DB_HOST = "127.0.0.1"

# First connect without specifying a database to create it if needed
conn = mysql.connector.connect(
    user=DB_USER,
    password=DB_PASS,
    host=DB_HOST
)

cur = conn.cursor()

# Create database if it doesn't exist
cur.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
cur.execute(f"USE {DB_NAME}")

# Drop tables in proper order to respect foreign key constraints
# First, drop tables that have foreign keys pointing to other tables
cur.execute("DROP TABLE IF EXISTS interviews;")
cur.execute("DROP TABLE IF EXISTS feedback;")
cur.execute("DROP TABLE IF EXISTS applications;")
cur.execute("DROP TABLE IF EXISTS fulltime;")
cur.execute("DROP TABLE IF EXISTS internship;")
cur.execute("DROP TABLE IF EXISTS stats;") # This will be replaced by applications with a 'hired' status
cur.execute("DROP TABLE IF EXISTS applied;") # This will be replaced by applications table
cur.execute("DROP TABLE IF EXISTS Job;")
cur.execute("DROP TABLE IF EXISTS UG;")
cur.execute("DROP TABLE IF EXISTS PG;")
cur.execute("DROP TABLE IF EXISTS Student;")
cur.execute("DROP TABLE IF EXISTS users;")

# Now create tables in the appropriate order
cur.execute("""
CREATE TABLE users (
    username VARCHAR(50) PRIMARY KEY,
    password VARCHAR(255),
    email VARCHAR(100),
    role ENUM('student', 'recruiter', 'faculty', 'admin') NOT NULL,
    fullname VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);""")

# Create Student table
cur.execute("""
CREATE TABLE Student (
    regNo VARCHAR(10) PRIMARY KEY,
    firstName VARCHAR(150),
    lastName VARCHAR(50),
    birthDate DATE,
    email VARCHAR(100),
    phone VARCHAR(15),
    address VARCHAR(200),
    gender CHAR(1),
    type VARCHAR(5), # UG or PG
    branch VARCHAR(100),
    semester INT,
    cgpa FLOAT,
    fa VARCHAR(100),  # Faculty Advisor
    date_added DATE,
    FOREIGN KEY (regNo) REFERENCES users(username)
);""")

# Create UG table
cur.execute("""
CREATE TABLE UG (
    regNo VARCHAR(10) PRIMARY KEY,
    branch VARCHAR(100),
    semester INT,
    date_added DATE,
    FOREIGN KEY (regNo) REFERENCES Student(regNo)
);""")

# Create PG table
cur.execute("""
CREATE TABLE PG (
    regNo VARCHAR(10) PRIMARY KEY,
    branch VARCHAR(100),
    semester INT,
    date_added DATE,
    FOREIGN KEY (regNo) REFERENCES Student(regNo)
);""")

# Create Job table
cur.execute("""
CREATE TABLE Job (
    job_Id VARCHAR(50) PRIMARY KEY,
    company VARCHAR(50),
    position VARCHAR(40),
    eligibility VARCHAR(1000),
    cgpa FLOAT,
    loc VARCHAR(50),
    type VARCHAR(20),
    recruiter_id VARCHAR(50),
    posted_date DATE,
    description TEXT,
    requirements TEXT,
    FOREIGN KEY (recruiter_id) REFERENCES users(username)
);""")

# Create fulltime table
cur.execute("""
CREATE TABLE fulltime (
    job_Id VARCHAR(50) PRIMARY KEY,
    bond VARCHAR(20),
    package INT,
    FOREIGN KEY (job_Id) REFERENCES Job(job_Id) ON DELETE CASCADE
);""")

# Create internship table
cur.execute("""
CREATE TABLE internship (
    job_Id VARCHAR(50) PRIMARY KEY,
    duration VARCHAR(20),
    ppo VARCHAR(20),
    salary INT,
    FOREIGN KEY (job_Id) REFERENCES Job(job_Id) ON DELETE CASCADE
);""")

# Create applications table - single table for tracking all applications
cur.execute("""
CREATE TABLE applications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(10),
    job_id VARCHAR(50),
    status ENUM('applied', 'shortlisted', 'interviewed', 'selected', 'accepted', 'rejected') DEFAULT 'applied',
    applied_date DATE,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES Student(regNo) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES Job(job_Id) ON DELETE CASCADE
);""")

# Create Interviews table
cur.execute("""
CREATE TABLE interviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    application_id INT,
    schedule_time DATETIME,
    meeting_link VARCHAR(255),
    notes TEXT,
    FOREIGN KEY (application_id) REFERENCES applications(id) ON DELETE CASCADE
);""")

# Create Feedback table
cur.execute("""
CREATE TABLE feedback (
    id INT AUTO_INCREMENT PRIMARY KEY,
    faculty_id VARCHAR(50),
    student_id VARCHAR(10),
    message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (faculty_id) REFERENCES users(username) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES Student(regNo) ON DELETE CASCADE
);""")

# Create applied table for backward compatibility
cur.execute("""
CREATE TABLE IF NOT EXISTS applied (
    regno VARCHAR(10) PRIMARY KEY,
    companies TEXT
);
""")

# Optional: Insert initial data for testing

# Admin user
import datetime
from werkzeug.security import generate_password_hash

today = datetime.date.today()

# Admin user
admin_password = generate_password_hash('admin123')
cur.execute("""
INSERT INTO users (username, password, email, role, fullname)
VALUES (%s, %s, %s, %s, %s)
""", ('11', admin_password, 'admin@example.com', 'admin', 'Admin User'))

# Faculty user
faculty_password = generate_password_hash('faculty123')
cur.execute("""
INSERT INTO users (username, password, email, role, fullname)
VALUES (%s, %s, %s, %s, %s)
""", ('F001', faculty_password, 'faculty@example.com', 'faculty', 'Faculty Member'))

# Recruiter user
recruiter_password = generate_password_hash('recruiter123')
cur.execute("""
INSERT INTO users (username, password, email, role, fullname)
VALUES (%s, %s, %s, %s, %s)
""", ('R001', recruiter_password, 'recruiter@example.com', 'recruiter', 'Recruiter Company'))

# Example job posting (Fulltime)
cur.execute("""
INSERT INTO Job (job_Id, company, position, eligibility, cgpa, loc, type, recruiter_id, posted_date, description, requirements)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
""", ('JOB001', 'Tech Solutions', 'Software Engineer', 'Bachelor of Technology, Computer Science Engineering', 7.0, 
       'Bangalore', 'Fulltime', 'R001', today, 
       'We are looking for a software engineer to join our team.', 'Good knowledge of programming languages and algorithms'))

cur.execute("""
INSERT INTO fulltime (job_Id, bond, package)
VALUES (%s, %s, %s)
""", ('JOB001', '2', 800000))

# Example job posting (Internship)
cur.execute("""
INSERT INTO Job (job_Id, company, position, eligibility, cgpa, loc, type, recruiter_id, posted_date, description, requirements)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
""", ('JOB002', 'DataCorp', 'Data Analyst Intern', 'Bachelor of Technology, Computer Science Engineering', 6.5,
       'Remote', 'internship', 'R001', today,
       '6-month internship for aspiring data analysts.', 'Python, SQL, basic statistics'))

cur.execute("""
INSERT INTO internship (job_Id, duration, ppo, salary)
VALUES (%s, %s, %s, %s)
""", ('JOB002', '6', 'yes', 25000))

conn.commit()
cur.close()
conn.close()

print("Database initialized successfully!")
