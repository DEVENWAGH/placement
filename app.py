from flask import Flask, request, session, redirect, url_for, render_template, flash
from flask_session import Session
from flask_mail import Mail,Message
import os
import mysql.connector
import re
import time
from werkzeug.security import generate_password_hash, check_password_hash
from common import cache
import pyautogui as pag
import smtplib
import json
import random
from datetime import datetime

app = Flask(__name__)


app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'allu526687@gmail.com'
app.config['MAIL_PASSWORD'] = 'bada sybq jymf khuv'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail=Mail(app)

app.secret_key = "randomdhjsecret"
cache.init_app(app=app, config={"CACHE_TYPE": "SimpleCache"})


Session(app)


DB_NAME = "placement"
DB_USER = "root"
DB_PASS = "root"
DB_HOST = "127.0.0.1"

try:
    conn = mysql.connector.connect(
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST
    )
    # conn.autocommit = True
except mysql.connector.Error as err:
    if err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
        # Database doesn't exist, create it
        temp_conn = mysql.connector.connect(
            user=DB_USER,
            password=DB_PASS,
            host=DB_HOST
        )
        temp_cursor = temp_conn.cursor()
        temp_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        temp_conn.commit()
        temp_cursor.close()
        temp_conn.close()
        
        # Now connect to the newly created database
        conn = mysql.connector.connect(
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            host=DB_HOST
        )
    else:
        print(f"Failed to connect to database: {err}")
        exit(1)


admin_user_created = False  # Flag to ensure the logic runs only once

@app.before_request
def create_admin_user():
    global admin_user_created
    if not admin_user_created:
        cursor = conn.cursor(dictionary=True, buffered=True)
        username = 'admin'
        password = '12345678'
        hashed_password = generate_password_hash(password)
        role = 'admin'

        # Check if admin user already exists
        cursor.execute('SELECT * FROM users WHERE username = %s AND role = %s', (username, role))
        account = cursor.fetchone()

        if not account:
            # Insert admin user into the database
            cursor.execute(
                'INSERT INTO users (username, password, email, role, fullname) VALUES (%s, %s, %s, %s, %s)',
                (username, hashed_password, 'admin@example.com', role, 'Administrator')
            )
            conn.commit()
            print("Admin user created successfully.")
        else:
            print("Admin user already exists.")

        admin_user_created = True  # Set the flag to True after execution


@app.route('/')
def index():
    """Redirect root URL to login page"""
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    cursor = conn.cursor(dictionary=True, buffered=True)

    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

        # Special case for admin login
        if username == 'admin':
            cursor.execute('SELECT * FROM users WHERE username = %s AND role = %s', (username, 'admin'))
            admin = cursor.fetchone()
            
            if admin and check_password_hash(admin['password'], password):
                session['loggedin'] = True
                session['username'] = username
                session['role'] = 'admin'
                return redirect(url_for('adminHome'))
            else:
                flash('Incorrect admin credentials')
                return render_template('login.html', hide_navbar=True)

        # Check if account exists using MySQL
        cursor.execute('SELECT * FROM users WHERE username = %s OR email = %s', (username, username))
        account = cursor.fetchone()
        
        # Print debug info to the server console
        print(f"Login attempt - User input: {username}")
        if account:
            print(f"User found: {account['username']}, Role: {account['role']}")
            password_check = check_password_hash(account['password'], password)
            print(f"Password check: {'Passed' if password_check else 'Failed'}")
        else:
            print("No matching account found")

        # If account exists in accounts table in our database
        if account and check_password_hash(account['password'], password):
            # Create session data
            session['loggedin'] = True
            session['username'] = account['username']
            session['role'] = account['role']
            
            # Redirect based on role
            if account['role'] == 'student':
                return redirect(url_for('student_dashboard'))
            elif account['role'] == 'recruiter':
                return redirect(url_for('recruiter_dashboard'))
            elif account['role'] == 'faculty':
                # Use direct URL instead of url_for to bypass potential errors
                return redirect('/faculty/dashboard')
            elif account['role'] == 'admin':
                return redirect(url_for('adminHome'))
            
            # Default redirect to home page if no specific role
            return redirect('/')
        else:
            # Provide more specific error message
            if account:
                flash('Incorrect password. Please try again.')
            else:
                flash('Account not found. Please check your username or email.')

    return render_template('login.html', hide_navbar=True)


@app.route('/register', methods=['GET', 'POST'])
def register():
    cursor = conn.cursor(dictionary=True, buffered=True)
    
    # If form is submitted
    if request.method == 'POST':
        # Get form data
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        fullname = request.form['fullname']
        role = request.form['role']
        
        # Check if username exists
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()
        
        if account:
            flash('Account already exists!')
        else:
            # Hash password
            hashed_password = generate_password_hash(password)
            
            # Insert new user
            cursor.execute(
                'INSERT INTO users (username, password, email, role, fullname, created_at) VALUES (%s, %s, %s, %s, %s, NOW())',
                (username, hashed_password, email, role, fullname)
            )
            conn.commit()
            flash('You have successfully registered! You can now login.')
            return redirect(url_for('login'))
    
    return render_template('register.html', hide_navbar=True)


@app.route('/create_profile', methods=['GET', 'POST'])
def create_profile():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    if session.get('role') != 'student':
        flash('Access denied. Student privileges required.')
        return redirect(url_for('login'))
    
    cursor = conn.cursor(dictionary=True, buffered=True)
    
    # Get user email from the users table
    cursor.execute('SELECT email FROM users WHERE username = %s', (session['username'],))
    user_data = cursor.fetchone()
    user_email = user_data['email'] if user_data else ''
    
    if request.method == 'POST':
        # Extract form data
        firstName = request.form['fname']
        lastName = request.form['lname']
        birthDate = request.form['year']
        email = user_email  # Use email from database instead of form
        phone = request.form['phone']
        address = request.form['address']
        gender = request.form['gender']
        education_type = request.form['type']
        branch = request.form['branch']
        semester = request.form['semester']
        cgpa = request.form['cgpa']
        
        try:
            # Insert directly into Student table with all fields
            cursor.execute('''
                INSERT INTO Student 
                (regNo, firstName, lastName, birthDate, email, phone, address, gender, 
                 type, branch, semester, cgpa, date_added)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURDATE())
            ''', (
                session['username'], firstName, lastName, birthDate, email, 
                phone, address, gender, education_type, branch, semester, cgpa
            ))
            
            # Insert into education type specific table (UG or PG)
            if education_type == 'UG':
                cursor.execute('''
                    INSERT INTO UG (regNo, branch, semester, date_added)
                    VALUES (%s, %s, %s, CURDATE())
                ''', (session['username'], branch, semester))
            else:
                cursor.execute('''
                    INSERT INTO PG (regNo, branch, semester, date_added)
                    VALUES (%s, %s, %s, CURDATE())
                ''', (session['username'], branch, semester))
            
            conn.commit()
            flash('Profile created successfully!', 'success')
            return redirect(url_for('student_dashboard'))
            
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f'Error creating profile: {err}', 'danger')
    
    return render_template('create_profile.html', user_email=user_email)


@app.route('/edit/')
def edit_profile():
    if session.get('role') != 'student':
        return redirect(url_for('login'))
    
    cursor = conn.cursor(dictionary=True, buffered=True)
    
    # Get student basic information
    cursor.execute('SELECT * FROM Student WHERE regNo = %s', (session['username'],))
    student = cursor.fetchone()
    
    if not student:
        flash('Please complete your profile first', 'warning')
        return redirect(url_for('create_profile'))
    
    # Get branch and semester based on education type
    branch = ""
    semester = 0
    
    if student['type'] == 'UG':
        cursor.execute('SELECT branch, semester FROM UG WHERE regNo = %s', (session['username'],))
        edu_details = cursor.fetchone()
        if edu_details:
            branch = edu_details['branch']
            semester = edu_details['semester']
    else:
        cursor.execute('SELECT branch, semester FROM PG WHERE regNo = %s', (session['username'],))
        edu_details = cursor.fetchone()
        if edu_details:
            branch = edu_details['branch']
            semester = edu_details['semester']
    
    return render_template('edit_profile.html', 
                           student=student, 
                           branch=branch, 
                           semester=semester)


@app.route('/update', methods=['GET', 'POST'])
def update():
    if 'loggedin' not in session or session.get('role') != 'student':
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Get form data
        cgpa = request.form['cgpa']
        phone = request.form['phone']
        address = request.form['address']
        
        # Get current semester based on education type
        cursor = conn.cursor(dictionary=True, buffered=True)
        try:
            # Get student type first
            cursor.execute('SELECT type FROM Student WHERE regNo = %s', (session['username'],))
            student_type = cursor.fetchone()
            
            if not student_type:
                flash('Student record not found', 'danger')
                return redirect(url_for('student_profile'))
            
            # Update student basic info
            cursor.execute('''
                UPDATE Student 
                SET phone = %s, address = %s, cgpa = %s
                WHERE regNo = %s
            ''', (phone, address, cgpa, session['username']))
            
            # Update semester in the appropriate education table
            if 'cursem' in request.form:
                semester = request.form['cursem']
                if student_type['type'] == 'UG':
                    cursor.execute('''
                        UPDATE UG 
                        SET semester = %s
                        WHERE regNo = %s
                    ''', (semester, session['username']))
                else:
                    cursor.execute('''
                        UPDATE PG 
                        SET semester = %s
                        WHERE regNo = %s
                    ''', (semester, session['username']))
            
            # Explicitly commit changes to the database
            conn.commit()
            print(f"Profile updated: phone={phone}, address={address}, cgpa={cgpa}")
            flash('Profile updated successfully!', 'success')
            
        except mysql.connector.Error as err:
            conn.rollback()
            print(f"Database error in update(): {err}")
            flash(f'Error updating profile: {err}', 'danger')
        finally:
            cursor.close()
        
        # Redirect to student profile to see the changes
        return redirect(url_for('student_profile'))
    
    # If not POST, redirect to edit profile
    return redirect(url_for('edit_profile'))


@app.route('/update_profile', methods=['POST'])
def update_profile():
    if session.get('role') != 'student':
        return redirect(url_for('login'))
    
    if request.method != 'POST':
        return redirect(url_for('student_profile'))
    
    # Extract form data
    phone = request.form['phone']
    address = request.form['address']
    semester = request.form['semester']
    cgpa = request.form['cgpa']
    
    cursor = conn.cursor(dictionary=True, buffered=True)
    
    try:
        # Get student education type
        cursor.execute('SELECT type FROM Student WHERE regNo = %s', (session['username'],))
        student_type = cursor.fetchone()
        
        if not student_type:
            flash('Student record not found', 'danger')
            return redirect(url_for('student_profile'))
        
        # Update student basic info
        cursor.execute('''
            UPDATE Student 
            SET phone = %s, address = %s, cgpa = %s
            WHERE regNo = %s
        ''', (phone, address, cgpa, session['username']))
        
        # Also update the phone in users table if needed
        cursor.execute('''
            UPDATE users 
            SET email = (SELECT email FROM Student WHERE regNo = %s)
            WHERE username = %s
        ''', (session['username'], session['username']))
        
        # Update education table based on type
        if student_type['type'] == 'UG':
            cursor.execute('''
                UPDATE UG 
                SET semester = %s
                WHERE regNo = %s
            ''', (semester, session['username']))
        else:
            cursor.execute('''
                UPDATE PG 
                SET semester = %s
                WHERE regNo = %s
            ''', (semester, session['username']))
        
        conn.commit()
        flash('Profile updated successfully!', 'success')
        
    except mysql.connector.Error as err:
        conn.rollback()
        flash(f'Error updating profile: {err}', 'danger')
    
    return redirect(url_for('student_profile'))


@app.route('/student/profile', methods=['GET', 'POST'])
def student_profile():
    if session.get('role') != 'student':
        return redirect(url_for('login'))
    
    cursor = conn.cursor(dictionary=True, buffered=True)
    
    try:
        # Get student basic information with proper date formatting
        cursor.execute('''
            SELECT s.*, 
                   DATE_FORMAT(s.birthDate, '%%d-%%m-%%Y') as formatted_dob
            FROM Student s 
            WHERE s.regNo = %s
        ''', (session['username'],))
        student = cursor.fetchone()
        
        if not student:
            flash('Please complete your profile first', 'warning')
            return redirect(url_for('create_profile'))
        
        # Convert student to list format expected by the template
        details = [[
            student['regNo'],
            student['firstName'],
            student['lastName'],
            student.get('formatted_dob') or student.get('birthDate'),
            student['email'],
            student['phone'],
            student['address'],
            student['gender'],
            student['type'],
            student['cgpa'],
            student['branch']  # Include branch directly from Student table
        ]]
        
        # Initialize both education details variables as None
        ug_details = None
        pg_details = None
        
        # Fetch the appropriate education details based on type
        if student['type'] == 'UG':
            cursor.execute('SELECT * FROM UG WHERE regNo = %s', (session['username'],))
            ug_details = cursor.fetchall()
            
            # Update student object with semester from UG table if available
            if ug_details and len(ug_details) > 0:
                student['semester'] = ug_details[0]['semester']  # Access by dictionary key, not index
        else:
            cursor.execute('SELECT * FROM PG WHERE regNo = %s', (session['username'],))
            pg_details = cursor.fetchall()
            
            # Update student object with semester from PG table if available
            if pg_details and len(pg_details) > 0:
                student['semester'] = pg_details[0]['semester']  # Access by dictionary key, not index
        
        # Ensure birthDate is properly formatted
        if 'birthDate' in student and student['birthDate'] and not student.get('formatted_dob'):
            from datetime import datetime
            if isinstance(student['birthDate'], datetime):
                student['formatted_dob'] = student['birthDate'].strftime('%d-%m-%Y')
        
        # Pass both variables to the template, even if one is None
        return render_template('view.html', 
                           details=details, 
                           ugdetails=ug_details, 
                           pgdetails=pg_details,
                           student=student)  # Pass the complete student object for easier access
                           
    except mysql.connector.Error as err:
        flash(f'Error retrieving profile: {err}', 'danger')
        return redirect(url_for('student_dashboard'))


@app.route('/student/dashboard')
def student_dashboard():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    if session.get('role') != 'student':
        flash('Access denied. Student privileges required.')
        return redirect(url_for('login'))
    
    # Fetch available jobs for student
    cursor = conn.cursor(dictionary=True, buffered=True)
    
    # Get student info
    cursor.execute('SELECT * FROM Student WHERE regNo = %s', (session['username'],))
    student = cursor.fetchone()
    
    if not student:
        flash('Please complete your profile first', 'warning')
        return redirect(url_for('create_profile'))
    
    # Initialize variables in case of errors
    eligible_jobs = []
    applications = []
    interviews = []
    feedback = []
    
    try:
        # Get student's education type and branch for job matching
        if student['type'] == 'UG':
            cursor.execute('SELECT branch FROM UG WHERE regNo = %s', (session['username'],))
        else:
            cursor.execute('SELECT branch FROM PG WHERE regNo = %s', (session['username'],))
        
        branch_result = cursor.fetchone()
        student_branch = branch_result['branch'] if branch_result else ""
        
        # Check if job table exists
        cursor.execute("SHOW TABLES LIKE 'job'")
        job_table_exists = cursor.fetchone() is not None
        
        if job_table_exists:
            # Get eligible jobs matching student's qualifications
            cursor.execute('''
                SELECT j.*, DATE(j.posted_date) as post_date 
                FROM job j 
                WHERE j.cgpa <= %s 
                ORDER BY j.posted_date DESC
            ''', (student['cgpa'],))
            all_jobs = cursor.fetchall()
            
            eligible_jobs = []
            for job in all_jobs:
                # Check if student's branch matches job eligibility
                eligibilities = job['eligibility'].split('#')
                if any(student_branch in eligibility for eligibility in eligibilities):
                    job_details = dict(job)
                    
                    # Add compensation details based on job type
                    if job['type'] == 'Fulltime':
                        cursor.execute('SELECT package FROM fulltime WHERE job_Id = %s', (job['job_Id'],))
                        package = cursor.fetchone()
                        if package:
                            job_details['compensation'] = f"Package: ₹{package['package']}"
                    else:
                        cursor.execute('SELECT salary, duration FROM internship WHERE job_Id = %s', (job['job_Id'],))
                        internship = cursor.fetchone()
                        if internship:
                            job_details['compensation'] = f"Stipend: ₹{internship['salary']} | Duration: {internship['duration']} months"
                    
                    eligible_jobs.append(job_details)
        else:
            flash('No jobs have been posted yet.', 'info')
            
        # Check if applications table exists
        cursor.execute("SHOW TABLES LIKE 'applications'")
        applications_table_exists = cursor.fetchone() is not None
        
        if applications_table_exists:
            # Get student's applications
            cursor.execute('''
                SELECT j.company, j.position, a.status, a.id, a.applied_date 
                FROM applications a 
                JOIN job j ON a.job_id = j.job_Id 
                WHERE a.student_id = %s
                ORDER BY a.applied_date DESC
            ''', (session['username'],))
            applications = cursor.fetchall()
            
            # Check if interviews table exists
            cursor.execute("SHOW TABLES LIKE 'interviews'")
            interviews_table_exists = cursor.fetchone() is not None
            
            if interviews_table_exists:
                # Get interview schedule if any
                cursor.execute('''
                    SELECT i.schedule_time, i.meeting_link, j.company, j.position 
                    FROM interviews i 
                    JOIN applications a ON i.application_id = a.id 
                    JOIN job j ON a.job_id = j.job_Id 
                    WHERE a.student_id = %s AND a.status = 'shortlisted'
                ''', (session['username'],))
                interviews = cursor.fetchall()
        
        # Check if feedback table exists
        cursor.execute("SHOW TABLES LIKE 'feedback'")
        feedback_table_exists = cursor.fetchone() is not None
        
        if feedback_table_exists:
            # Get faculty feedback with flag for recent feedback
            cursor.execute('''
                SELECT f.message, u.fullname, f.created_at,
                    CASE WHEN f.created_at > DATE_SUB(NOW(), INTERVAL 7 DAY) THEN 1 ELSE 0 END as is_new
                FROM feedback f 
                JOIN users u ON f.faculty_id = u.username 
                WHERE f.student_id = %s 
                ORDER BY f.created_at DESC
            ''', (session['username'],))
            feedback = cursor.fetchall()
            
            # Check for new unread feedback and mark it
            cursor.execute('''
                SELECT COUNT(*) as new_count
                FROM feedback 
                WHERE student_id = %s AND created_at > DATE_SUB(NOW(), INTERVAL 7 DAY)
            ''', (session['username'],))
            new_feedback_count = cursor.fetchone()['new_count']
            
            if new_feedback_count > 0:
                flash(f'You have {new_feedback_count} new feedback message(s)', 'info')
    
    except mysql.connector.Error as err:
        flash(f'Database error: {err}', 'danger')
    
    return render_template('student_dashboard.html', 
                          jobs=eligible_jobs,
                          applications=applications,
                          student=student,
                          interviews=interviews,
                          feedback=feedback)


@app.route('/view_jobs')
def view_jobs():
    """View all jobs that match student's qualifications"""
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    if session.get('role') != 'student':
        flash('Access denied. Student privileges required.')
        return redirect(url_for('login'))
    
    cursor = conn.cursor(dictionary=True, buffered=True)
    
    # Get student info
    cursor.execute('SELECT * FROM Student WHERE regNo = %s', (session['username'],))
    student = cursor.fetchone()
    
    if not student:
        flash('Please complete your profile first', 'warning')
        return redirect(url_for('create_profile'))
    
    # Get student's branch for job matching
    if student['type'] == 'UG':
        cursor.execute('SELECT branch FROM UG WHERE regNo = %s', (session['username'],))
    else:
        cursor.execute('SELECT branch FROM PG WHERE regNo = %s', (session['username'],))
    
    branch_result = cursor.fetchone()
    student_branch = branch_result['branch'] if branch_result else ""
    
    # Check if job table exists and get all eligible jobs
    eligible_jobs = []
    
    try:
        cursor.execute("SHOW TABLES LIKE 'job'")
        if cursor.fetchone():
            cursor.execute('''
                SELECT j.*, DATE(j.posted_date) as post_date 
                FROM job j 
                WHERE j.cgpa <= %s 
                ORDER BY j.posted_date DESC
            ''', (student['cgpa'],))
            all_jobs = cursor.fetchall()
            
            for job in all_jobs:
                # Check if student's branch matches job eligibility
                eligibilities = job['eligibility'].split('#')
                if any(student_branch in eligibility for eligibility in eligibilities):
                    job_details = dict(job)
                    
                    # Add compensation details based on job type
                    if job['type'] == 'Fulltime':
                        cursor.execute('SELECT package FROM fulltime WHERE job_Id = %s', (job['job_Id'],))
                        package = cursor.fetchone()
                        if package:
                            job_details['compensation'] = f"Package: ₹{package['package']}"
                    else:
                        cursor.execute('SELECT salary, duration FROM internship WHERE job_Id = %s', (job['job_Id'],))
                        internship = cursor.fetchone()
                        if internship:
                            job_details['compensation'] = f"Stipend: ₹{internship['salary']} | Duration: {internship['duration']} months"
                    
                    eligible_jobs.append(job_details)
    except mysql.connector.Error as err:
        flash(f'Database error: {err}', 'danger')
    
    # Get student's applied jobs for comparison
    applied_companies = []
    cursor.execute("SHOW TABLES LIKE 'applications'")
    if cursor.fetchone():
        cursor.execute('SELECT j.job_Id FROM applications a JOIN job j ON a.job_id = j.job_Id WHERE a.student_id = %s', 
                      (session['username'],))
        applied_jobs = cursor.fetchall()
        applied_companies = [job['job_Id'] for job in applied_jobs]
    
    return render_template('view_jobs.html', 
                          jobs=eligible_jobs, 
                          applied_jobs=applied_companies,
                          student=student)


@app.route('/apply_job/<job_id>', methods=['GET', 'POST'])
def apply_job(job_id):
    if session.get('role') != 'student':
        return redirect(url_for('login'))
    
    cursor = conn.cursor(dictionary=True, buffered=True)
    
    # Check if already applied
    cursor.execute('SELECT * FROM applications WHERE student_id = %s AND job_id = %s', 
                  (session['username'], job_id))
    existing_application = cursor.fetchone()
    
    if existing_application:
        flash('You have already applied for this job')
        return redirect(url_for('student_dashboard'))
    
    # Insert application
    cursor.execute("""
        INSERT INTO applications (student_id, job_id, status, applied_date)
        VALUES (%s, %s, 'applied', CURDATE())
    """, (session['username'], job_id))
    
    # Update in applied table for backward compatibility
    cursor.execute('SELECT companies FROM applied WHERE regno = %s', (session['username'],))
    applied_result = cursor.fetchone()
    
    # Get company name
    cursor.execute('SELECT company FROM job WHERE job_Id = %s', (job_id,))
    company_result = cursor.fetchone()
    
    if applied_result:
        companies = applied_result['companies'] + ' ' + company_result['company'] if applied_result['companies'] else company_result['company']
        cursor.execute('UPDATE applied SET companies = %s WHERE regno = %s', 
                      (companies, session['username']))
    else:
        cursor.execute('INSERT INTO applied (regno, companies) VALUES (%s, %s)', 
                      (session['username'], company_result['company']))
    
    conn.commit()
    flash('Application submitted successfully')
    return redirect(url_for('student_dashboard'))


@app.route('/delete/<job_id>', methods=['GET'])
def delete_job(job_id):
    if 'loggedin' not in session or session.get('role') not in ['admin', 'recruiter']:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('login'))
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM job WHERE job_Id = %s', (job_id,))
        conn.commit()
        flash('Job deleted successfully!', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error deleting job: {e}', 'danger')
    return redirect(url_for('view_database'))


@app.route('/recruiter/dashboard')
def recruiter_dashboard():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    if session.get('role') != 'recruiter':
        flash('Access denied. Recruiter privileges required.')
        return redirect(url_for('login'))
    
    cursor = conn.cursor(dictionary=True, buffered=True)
    
    # Get jobs posted by this recruiter
    cursor.execute('''
        SELECT j.*, 
               COUNT(a.id) AS application_count,
               CASE 
                   WHEN j.type = 'Fulltime' THEN (SELECT package FROM fulltime WHERE job_Id = j.job_Id)
                   ELSE (SELECT salary FROM internship WHERE job_Id = j.job_Id)
               END AS compensation
        FROM job j
        LEFT JOIN applications a ON j.job_Id = a.job_id
        WHERE j.recruiter_id = %s
        GROUP BY j.job_Id
    ''', (session['username'],))
    jobs = cursor.fetchall()
    
    # Get all applications for recruiter's jobs
    cursor.execute('''
        SELECT a.*, j.company, j.position, j.type, s.firstName, s.lastName, s.email, s.cgpa
        FROM applications a
        JOIN job j ON a.job_id = j.job_Id
        JOIN Student s ON a.student_id = s.regNo
        WHERE j.recruiter_id = %s
        ORDER BY a.applied_date DESC
    ''', (session['username'],))
    applications = cursor.fetchall()
    
    return render_template('recruiter_dashboard.html', jobs=jobs, applications=applications)


@app.route('/post_job', methods=['GET', 'POST'])
def post_job():
    """Handle job posting by recruiter"""
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    if session.get('role') != 'recruiter':
        flash('Access denied. Recruiter privileges required.')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Extract form data
        job_id = request.form['job_Id']
        company = request.form['Company']
        position = request.form['Position']
        cgpa = request.form['CGPA']
        location = request.form['Location']
        job_type = request.form['type']
        
        # Convert eligibility checkboxes to string
        eligibility_values = request.form.getlist('Eligibility')
        eligibility = '#'.join(eligibility_values)
        
        # Additional fields if available
        description = request.form.get('description', '')
        requirements = request.form.get('requirements', '')
        
        cursor = conn.cursor(dictionary=True, buffered=True)
        
        # Check if job ID already exists
        cursor.execute('SELECT job_Id FROM job WHERE job_Id = %s', (job_id,))
        existing_job = cursor.fetchone()
        
        if existing_job:
            flash('Job ID already exists. Please use a different ID.')
            return render_template('post_job.html')
        
        try:
            # Insert into job table
            cursor.execute('''
                INSERT INTO job (job_Id, company, position, eligibility, cgpa, loc, type, recruiter_id, posted_date, description, requirements)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURDATE(), %s, %s)
            ''', (job_id, company, position, eligibility, cgpa, location, job_type, session['username'], description, requirements))
            
            # Add specific details based on job type
            if job_type == 'Fulltime':
                bond = request.form.get('bond', '0')
                package = request.form.get('package', '0')
                
                cursor.execute('''
                    INSERT INTO fulltime (job_Id, bond, package)
                    VALUES (%s, %s, %s)
                ''', (job_id, bond, package))
            else:  # Internship
                duration = request.form.get('duration', '0')
                ppo = request.form.get('ppo', 'no')
                salary = request.form.get('salary', '0')
                
                cursor.execute('''
                    INSERT INTO internship (job_Id, duration, ppo, salary)
                    VALUES (%s, %s, %s, %s)
                ''', (job_id, duration, ppo, salary))
            
            conn.commit()
            flash('Job posted successfully!')
            return redirect(url_for('recruiter_dashboard'))
            
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f'Error adding job: {err}', 'danger')
            return render_template('post_job.html')
    
    # GET request - show job posting form
    return render_template('post_job.html')


@app.route('/admin/post_job', methods=['GET', 'POST'])
def admin_post_job():
    # This page is disabled/removed
    return redirect(url_for('admin_dashboard'))


@app.route('/update_application/<int:app_id>', methods=['POST'])
def update_application(app_id):
    if session.get('role') != 'recruiter':
        return redirect(url_for('login'))
    
    status = request.form['status']
    
    cursor = conn.cursor(dictionary=True, buffered=True)
    cursor.execute('UPDATE applications SET status = %s WHERE id = %s', (status, app_id))
    conn.commit()
    
    flash('Application status updated successfully')
    return redirect(url_for('recruiter_dashboard'))


@app.route('/schedule_interview/<int:app_id>', methods=['POST'])
def schedule_interview(app_id):
    if session.get('role') != 'recruiter':
        return redirect(url_for('login'))
    
    interview_date = request.form['interview_date']
    interview_time = request.form['interview_time']
    meeting_link = request.form['meeting_link']
    
    # Combine date and time
    schedule_time = f"{interview_date} {interview_time}"
    
    cursor = conn.cursor(dictionary=True, buffered=True)
    
    # Update application status
    cursor.execute('UPDATE applications SET status = %s WHERE id = %s', ('shortlisted', app_id))
    
    # Create interview entry
    cursor.execute('''
        INSERT INTO interviews (application_id, schedule_time, meeting_link)
        VALUES (%s, %s, %s)
    ''', (app_id, schedule_time, meeting_link))
    
    # Get student and job details for email
    cursor.execute('''
        SELECT s.firstName, s.lastName, s.email, j.company, j.position
        FROM applications a
        JOIN Student s ON a.student_id = s.regNo
        JOIN job j ON a.job_id = j.job_Id
        WHERE a.id = %s
    ''', (app_id,))
    
    student_info = cursor.fetchone()
    conn.commit()
    
    if student_info:
        # Send email notification
        try:
            msg = Message(
                f'Interview Scheduled with {student_info["company"]}',
                sender=app.config['MAIL_USERNAME'],
                recipients=[student_info['email']]
            )
            
            msg.html = render_template(
                'interview_email.html',
                student={'name': f"{student_info['firstName']} {student_info['lastName']}"},
                company=student_info['company'],
                position=student_info['position'],
                interview_date=interview_date,
                interview_time=interview_time,
                interview_link=meeting_link
            )
            
            mail.send(msg)
            flash('Interview scheduled and notification sent to student')
        except Exception as e:
            flash(f'Interview scheduled but email notification failed: {str(e)}')
    else:
        flash('Interview scheduled')
    
    return redirect(url_for('recruiter_dashboard'))


@app.route('/faculty/dashboard')
def faculty_dashboard():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    if session.get('role') != 'faculty':
        flash('Access denied. Faculty privileges required.')
        return redirect(url_for('login'))
    
    # Fetch data for faculty dashboard
    cursor = conn.cursor(dictionary=True, buffered=True)
    
    # Initialize stats
    stats = {
        'total_students': 0,
        'placed_students': 0,
        'placement_rate': 0
    }
    
    # Initialize application stats
    app_stats = {
        'total': 0,
        'shortlisted': 0,
        'interviewed': 0,
        'selected': 0,
        'accepted': 0,
        'rejected': 0
    }
    
    # Get total students count
    cursor.execute('SELECT COUNT(*) as count FROM Student')
    result = cursor.fetchone()
    if result:
        stats['total_students'] = result['count']
    
    # Get placed students count (students who have been accepted for a job)
    cursor.execute('''
        SELECT COUNT(DISTINCT student_id) as count 
        FROM applications 
        WHERE status = 'accepted'
    ''')
    result = cursor.fetchone()
    if result:
        stats['placed_students'] = result['count']
    
    # Calculate placement rate
    if stats['total_students'] > 0:
        stats['placement_rate'] = round((stats['placed_students'] / stats['total_students']) * 100)
    
    # Get application statistics
    cursor.execute('''
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN status = 'shortlisted' THEN 1 ELSE 0 END) as shortlisted,
            SUM(CASE WHEN status = 'interviewed' THEN 1 ELSE 0 END) as interviewed,
            SUM(CASE WHEN status = 'selected' THEN 1 ELSE 0 END) as selected,
            SUM(CASE WHEN status = 'accepted' THEN 1 ELSE 0 END) as accepted,
            SUM(CASE WHEN status = 'rejected' THEN 1 ELSE 0 END) as rejected
        FROM applications
    ''')
    
    app_stat_result = cursor.fetchone()
    if app_stat_result:
        app_stats['total'] = app_stat_result['total'] or 0
        app_stats['shortlisted'] = app_stat_result['shortlisted'] or 0
        app_stats['interviewed'] = app_stat_result['interviewed'] or 0
        app_stats['selected'] = app_stat_result['selected'] or 0
        app_stats['accepted'] = app_stat_result['accepted'] or 0
        app_stats['rejected'] = app_stat_result['rejected'] or 0
    
    # Get students with their application statistics
    cursor.execute('''
        SELECT s.*, 
            COUNT(DISTINCT a.id) as application_count,
            SUM(CASE WHEN a.status = 'shortlisted' OR a.status = 'interviewed' OR a.status = 'selected' OR a.status = 'accepted' THEN 1 ELSE 0 END) as shortlisted_count,
            MAX(CASE WHEN a.status = 'accepted' THEN 1 ELSE 0 END) as is_placed
        FROM Student s
        LEFT JOIN applications a ON s.regNo = a.student_id
        GROUP BY s.regNo
        ORDER BY s.firstName
    ''')
    students = cursor.fetchall()
    
    # Get recent feedback provided by this faculty
    cursor.execute('''
        SELECT f.*, s.firstName, s.lastName
        FROM feedback f
        JOIN Student s ON f.student_id = s.regNo
        WHERE f.faculty_id = %s
        ORDER BY f.created_at DESC
        LIMIT 5
    ''', (session['username'],))
    feedback_history = cursor.fetchall()
    
    return render_template('faculty_dashboard.html', 
                          stats=stats,
                          app_stats=app_stats,
                          students=students,
                          feedback_history=feedback_history)


@app.route('/student/progress/<student_id>')
def student_progress(student_id):
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    if session.get('role') != 'faculty':
        flash('Access denied. Faculty privileges required.')
        return redirect(url_for('login'))
    
    cursor = conn.cursor(dictionary=True, buffered=True)
    
    # Get student details with proper date formatting
    cursor.execute('''
        SELECT s.*, 
               DATE_FORMAT(s.birthDate, '%%d-%%m-%%Y') as formatted_dob
        FROM Student s 
        WHERE s.regNo = %s
    ''', (student_id,))
    student = cursor.fetchone()
    
    if not student:
        flash('Student not found', 'danger')
        return redirect(url_for('faculty_dashboard'))
    
    # Ensure proper date formatting for display
    if student and student['birthDate']:
        try:
            from datetime import datetime
            # Convert string to date if needed
            if isinstance(student['birthDate'], str):
                student['birthDate'] = datetime.strptime(student['birthDate'], '%Y-%m-%d')
        except Exception as e:
            print(f"Error formatting date: {e}")
            # Set to None if there's a formatting error
            student['birthDate'] = None
    
    # Get student's applications
    cursor.execute('''
        SELECT j.company, j.position, a.status, a.applied_date, a.id
        FROM applications a 
        JOIN job j ON a.job_id = j.job_Id 
        WHERE a.student_id = %s
        ORDER BY a.applied_date DESC
    ''', (student_id,))
    applications = cursor.fetchall()
    
    # Get interview schedule if any
    cursor.execute('''
        SELECT i.schedule_time, i.meeting_link, j.company, j.position 
        FROM interviews i 
        JOIN applications a ON i.application_id = a.id 
        JOIN job j ON a.job_id = j.job_Id 
        WHERE a.student_id = %s AND (a.status = 'shortlisted' OR a.status = 'interviewed')
    ''', (student_id,))
    interviews = cursor.fetchall()
    
    # Get feedback history
    cursor.execute('''
        SELECT f.message, u.fullname, f.created_at
        FROM feedback f 
        JOIN users u ON f.faculty_id = u.username 
        WHERE f.student_id = %s 
        ORDER BY f.created_at DESC
    ''', (student_id,))
    feedback = cursor.fetchall()
    
    return render_template('student_progress.html', 
                          student=student,
                          applications=applications,
                          interviews=interviews,
                          feedback=feedback)


@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    if 'loggedin' not in session or session.get('role') != 'faculty':
        flash('Access denied', 'danger')
        return redirect(url_for('login'))
    
    student_id = request.form.get('student_id')
    message = request.form.get('message')
    
    if not student_id or not message:
        flash('Missing required information', 'danger')
        return redirect(url_for('faculty_dashboard'))
    
    cursor = conn.cursor(dictionary=True, buffered=True)
    
    # Check if feedback table exists, create if not
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INT AUTO_INCREMENT PRIMARY KEY,
            student_id VARCHAR(20) NOT NULL,
            faculty_id VARCHAR(20) NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES Student(regNo),
            FOREIGN KEY (faculty_id) REFERENCES users(username)
        )
    ''')
    
    # Insert new feedback
    cursor.execute('''
        INSERT INTO feedback (student_id, faculty_id, message)
        VALUES (%s, %s, %s)
    ''', (student_id, session['username'], message))
    
    conn.commit()
    
    flash('Feedback submitted successfully', 'success')
    
    # Redirect back to student progress page if coming from there
    if 'student_id' in request.referrer:
        return redirect(url_for('student_progress', student_id=student_id))
    else:
        return redirect(url_for('faculty_dashboard'))


@app.route('/adminHome')
def adminHome():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    if session.get('role') != 'admin':
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('login'))
    
    return render_template('adminhome.html')


@app.route('/admin/dashboard')
def admin_dashboard():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    if session.get('role') != 'admin':
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('login'))
    
    cursor = conn.cursor(dictionary=True, buffered=True)
    
    # Initialize stats
    stats = {
        'total_students': 0,
        'total_jobs': 0,
        'placement_rate': 0,
        'unique_companies': 0,
    }
    
    # Initialize application stats
    app_stats = {
        'total': 0,
        'shortlisted': 0,
        'interviewed': 0,
        'selected': 0,
        'accepted': 0,
        'rejected': 0
    }
    
    # Get student count
    cursor.execute('SELECT COUNT(*) as count FROM Student')
    result = cursor.fetchone()
    if result:
        stats['total_students'] = result['count']
    
    # Get job count
    cursor.execute('SELECT COUNT(*) as count FROM job')
    result = cursor.fetchone()
    if result:
        stats['total_jobs'] = result['count']
    
    # Get unique companies count
    cursor.execute('SELECT COUNT(DISTINCT company) as count FROM job')
    result = cursor.fetchone()
    if result:
        stats['unique_companies'] = result['count']
    
    # Get placed students count and calculate rate
    cursor.execute('''
        SELECT COUNT(DISTINCT student_id) as count 
        FROM applications 
        WHERE status = 'accepted'
    ''')
    result = cursor.fetchone()
    if result:
        placed_students = result['count']
        if stats['total_students'] > 0:
            stats['placement_rate'] = round((placed_students / stats['total_students']) * 100)
    
    # Get application statistics
    cursor.execute('''
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN status = 'shortlisted' THEN 1 ELSE 0 END) as shortlisted,
            SUM(CASE WHEN status = 'interviewed' THEN 1 ELSE 0 END) as interviewed,
            SUM(CASE WHEN status = 'selected' THEN 1 ELSE 0 END) as selected,
            SUM(CASE WHEN status = 'accepted' THEN 1 ELSE 0 END) as accepted,
            SUM(CASE WHEN status = 'rejected' THEN 1 ELSE 0 END) as rejected
        FROM applications
    ''')
    
    app_stat_result = cursor.fetchone()
    if app_stat_result:
        app_stats['total'] = app_stat_result['total'] or 0
        app_stats['shortlisted'] = app_stat_result['shortlisted'] or 0
        app_stats['interviewed'] = app_stat_result['interviewed'] or 0
        app_stats['selected'] = app_stat_result['selected'] or 0
        app_stats['accepted'] = app_stat_result['accepted'] or 0
        app_stats['rejected'] = app_stat_result['rejected'] or 0
    
    # Get latest jobs
    cursor.execute('''
        SELECT j.*, COUNT(a.id) as application_count
        FROM job j
        LEFT JOIN applications a ON j.job_Id = a.job_id
        GROUP BY j.job_Id
        ORDER BY j.posted_date DESC
        LIMIT 5
    ''')
    latest_jobs = cursor.fetchall()
    
    # Get recent activities (simplistic implementation)
    recent_activities = []
    
    # Get recent applications
    cursor.execute('''
        SELECT a.applied_date, a.status, s.firstName, s.lastName, j.company, j.position
        FROM applications a
        JOIN Student s ON a.student_id = s.regNo
        JOIN job j ON a.job_id = j.job_Id
        ORDER BY a.applied_date DESC
        LIMIT 5
    ''')
    
    recent_apps = cursor.fetchall()
    for app in recent_apps:
        activity = {
            'date': app['applied_date'].strftime('%Y-%m-%d'),
            'time': app['applied_date'].strftime('%H:%M'),
            'description': f"{app['firstName']} {app['lastName']} applied for {app['position']} at {app['company']}"
        }
        recent_activities.append(activity)
    
    return render_template('admin_dashboard.html', 
                          stats=stats,
                          app_stats=app_stats,
                          latest_jobs=latest_jobs,
                          recent_activities=recent_activities)


@app.route('/admin_manage_users', methods=['GET', 'POST'])
def admin_manage_users():
    """Handle admin user management - add faculty and recruiter users"""
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    if session.get('role') != 'admin':
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('login'))
    
    # Handle form submissions
    if request.method == 'POST':
        action = request.form.get('action')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Hash the password for security
        hashed_password = generate_password_hash(password)
        
        try:
            cursor = conn.cursor(dictionary=True, buffered=True)
            
            # Check if the username or email already exist
            cursor.execute('SELECT * FROM users WHERE username = %s OR email = %s', 
                           (username, email))
            account = cursor.fetchone()
            
            if account:
                flash('Account already exists with that username or email!', 'danger')
            else:
                # Add faculty user
                if action == 'add_faculty':
                    cursor.execute(
                        'INSERT INTO users (username, password, email, role, fullname) VALUES (%s, %s, %s, %s, %s)',
                        (username, hashed_password, email, 'faculty', username)
                    )
                    conn.commit()
                    flash('Faculty account created successfully!', 'success')
                
                # Add recruiter user
                elif action == 'add_recruiter':
                    cursor.execute(
                        'INSERT INTO users (username, password, email, role, fullname) VALUES (%s, %s, %s, %s, %s)',
                        (username, hashed_password, email, 'recruiter', username)
                    )
                    conn.commit()
                    flash('Recruiter account created successfully!', 'success')
        
        except Exception as e:
            conn.rollback()
            flash(f'Error creating account: {str(e)}', 'danger')
        finally:
            cursor.close()
    
    # Render the user management template
    return render_template('admin_manage_users.html')


@app.route('/edit_user', methods=['POST'])
def edit_user():
    if 'loggedin' not in session or session.get('role') != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('login'))

    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')

    cursor = conn.cursor()
    # Update email
    cursor.execute('UPDATE users SET email = %s WHERE username = %s', (email, username))
    # Update password if provided
    if password:
        hashed_password = generate_password_hash(password)
        cursor.execute('UPDATE users SET password = %s WHERE username = %s', (hashed_password, username))
    conn.commit()
    cursor.close()
    flash('User credentials updated successfully!', 'success')
    return redirect(url_for('view_database'))


@app.route('/db/', methods=['GET', 'POST'])
def view_database():
    """Handle database viewing and management for admin"""
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    if session.get('role') != 'admin':
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('login'))

    # Use dictionary=True for users so template can access user.username etc.
    cursor = conn.cursor()
    cursor_dict = conn.cursor(dictionary=True)

    cursor.execute('SELECT * FROM Student ORDER BY regNo')
    students = cursor.fetchall()
    cursor.execute('SELECT * FROM UG ORDER BY regNo')
    ugs = cursor.fetchall()
    cursor.execute('SELECT * FROM PG ORDER BY regNo')
    pgs = cursor.fetchall()
    cursor.execute('SELECT * FROM job ORDER BY job_Id')
    job = cursor.fetchall()
    cursor.execute('SELECT * FROM fulltime ORDER BY job_Id')
    fulltime = cursor.fetchall()
    cursor.execute('SELECT * FROM internship ORDER BY job_Id')
    intern = cursor.fetchall()
    cursor.execute('SELECT * FROM applied ORDER BY regno')
    applied = cursor.fetchall()

    # Fetch users as dictionaries for template
    cursor_dict.execute('SELECT * FROM users WHERE role != "admin" ORDER BY username')
    users = cursor_dict.fetchall()

    # Handle add faculty/recruiter POST forms (if any)
    if request.method == 'POST':
        action = request.form.get('action')
        username = request.form.get('username')
        email = request.form.get('email')
        fullname = request.form.get('fullname')
        password = request.form.get('password')
        from werkzeug.security import generate_password_hash
        hashed_password = generate_password_hash(password)
        cursor2 = conn.cursor()
        # Check if the username or email already exist
        cursor2.execute('SELECT * FROM users WHERE username = %s OR email = %s', (username, email))
        account = cursor2.fetchone()
        if account:
            flash('Account already exists with that username or email!', 'danger')
        else:
            if action == 'add_faculty':
                cursor2.execute(
                    'INSERT INTO users (username, password, email, role, fullname) VALUES (%s, %s, %s, %s, %s)',
                    (username, hashed_password, email, 'faculty', fullname)
                )
                conn.commit()
                flash('Faculty account created successfully!', 'success')
            elif action == 'add_recruiter':
                cursor2.execute(
                    'INSERT INTO users (username, password, email, role, fullname) VALUES (%s, %s, %s, %s, %s)',
                    (username, hashed_password, email, 'recruiter', fullname)
                )
                conn.commit()
                flash('Recruiter account created successfully!', 'success')
        cursor2.close()

    return render_template(
        'index.html',
        students=students,
        ugs=ugs,
        pgs=pgs,
        job=job,
        fulltime=fulltime,
        intern=intern,
        applied=applied,
        users=users
    )


@app.route('/logout')
def logout():
    """Handle user logout for all roles except admin"""
    # Remove session data
    session.pop('loggedin', None)
    session.pop('username', None)
    session.pop('role', None)
    # Redirect to login page
    flash('You have been logged out successfully')
    return redirect(url_for('login'))


@app.route('/logoutadmin')
def logoutadmin():
    """Handle admin logout"""
    # Remove session data
    session.pop('loggedin', None)
    session.pop('username', None)
    session.pop('role', None)
    # Redirect to login page
    flash('Admin logged out successfully')
    return redirect(url_for('login'))


@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors by showing a custom page"""
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)