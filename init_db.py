import os
import mysql.connector
from datetime import date

DB_NAME = "placement"
DB_USER = "root"
DB_PASS = "12345678"
DB_HOST = "localhost"

conn = mysql.connector.connect(
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASS,
    host=DB_HOST
)

cur = conn.cursor()

# Drop and create users table
cur.execute("DROP TABLE IF EXISTS users;")
cur.execute("""
CREATE TABLE users (
    username VARCHAR(50) PRIMARY KEY,
    password VARCHAR(255),
    email VARCHAR(50),
    role ENUM('student', 'recruiter', 'faculty') NOT NULL,
    fullname VARCHAR(100)
);""")

# Drop and create Student table
cur.execute("DROP TABLE IF EXISTS Student;")
cur.execute("""
CREATE TABLE Student (
    regNo VARCHAR(10) PRIMARY KEY,
    firstName VARCHAR(150),
    lastName VARCHAR(50),
    dob DATE,
    email VARCHAR(40),
    phoneNo BIGINT,
    address VARCHAR(200),
    gender CHAR(1),
    type VARCHAR(5),
    cgpa FLOAT,
    fa VARCHAR(100),
    date_added DATE
);""")

# Drop and create UG table
cur.execute("DROP TABLE IF EXISTS UG;")
cur.execute("""
CREATE TABLE UG (
    regNo VARCHAR(10) PRIMARY KEY,
    branch VARCHAR(100),
    semester INT,
    date_added DATE
);""")

# Drop and create PG table
cur.execute("DROP TABLE IF EXISTS PG;")
cur.execute("""
CREATE TABLE PG (
    regNo VARCHAR(10) PRIMARY KEY,
    branch VARCHAR(100),
    semester INT,
    date_added DATE
);""")

# Drop and create Job table
cur.execute("DROP TABLE IF EXISTS Job;")
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
    FOREIGN KEY (recruiter_id) REFERENCES users(username)
);""")

# Drop and create fulltime table
cur.execute("DROP TABLE IF EXISTS fulltime;")
cur.execute("""
CREATE TABLE fulltime (
    job_Id VARCHAR(50) PRIMARY KEY,
    bond VARCHAR(20),
    package INT
);""")

# Drop and create internship table
cur.execute("DROP TABLE IF EXISTS internship;")
cur.execute("""
CREATE TABLE internship (
    job_Id VARCHAR(50) PRIMARY KEY,
    duration VARCHAR(20),
    ppo VARCHAR(20),
    salary INT
);""")

# Drop and create stats table
cur.execute("DROP TABLE IF EXISTS stats;")
cur.execute("""
CREATE TABLE stats (
    regno VARCHAR(100) PRIMARY KEY,
    job_id VARCHAR(50)
);""")

# Drop and create applied table
cur.execute("DROP TABLE IF EXISTS applied;")
cur.execute("""
CREATE TABLE applied (
    regno VARCHAR(100) PRIMARY KEY,
    companies VARCHAR(500)
);""")


# New Application table
cur.execute("DROP TABLE IF EXISTS applications;")
cur.execute("""
CREATE TABLE applications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(10),
    job_id VARCHAR(50),
    status ENUM('applied', 'shortlisted', 'interviewed') DEFAULT 'applied',
    applied_date DATE,
    FOREIGN KEY (student_id) REFERENCES Student(regNo),
    FOREIGN KEY (job_id) REFERENCES Job(job_Id)
);""")

# New Interviews table
cur.execute("DROP TABLE IF EXISTS interviews;")
cur.execute("""
CREATE TABLE interviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    application_id INT,
    schedule_time DATETIME,
    meeting_link VARCHAR(255),
    FOREIGN KEY (application_id) REFERENCES applications(id)
);""")

# New Feedback table
cur.execute("DROP TABLE IF EXISTS feedback;")
cur.execute("""
CREATE TABLE feedback (
    id INT AUTO_INCREMENT PRIMARY KEY,
    faculty_id VARCHAR(50),
    student_id VARCHAR(10),
    message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (faculty_id) REFERENCES users(username),
    FOREIGN KEY (student_id) REFERENCES Student(regNo)
);""")

conn.commit()

# Example insert to Student/UG/PG
# today = date.today()

# cur.execute("""
# INSERT INTO Student (regNo, firstName, lastName, dob, email, phoneNo, address, gender, type, cgpa, fa, date_added)
# VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
# """, ("S001", "John", "Doe", "2000-01-01", "john@example.com", 9876543210, "123 Main St", "M", "UG", 8.5, "Dr. Smith", today))

# cur.execute("""
# INSERT INTO UG (regNo, branch, semester, date_added)
# VALUES (%s, %s, %s, %s)
# """, ("S001", "Computer Science", 6, today))

conn.commit()
cur.close()
conn.close()
