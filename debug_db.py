import mysql.connector

# Database connection parameters
DB_NAME = "placement"
DB_USER = "root"
DB_PASS = "root"
DB_HOST = "127.0.0.1"

# Connect to the database
conn = mysql.connector.connect(
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASS,
    host=DB_HOST
)
cursor = conn.cursor(dictionary=True)

# Test function to view a specific student
def view_student(reg_no):
    cursor.execute('SELECT * FROM Student WHERE regNo = %s', (reg_no,))
    student = cursor.fetchone()
    print("Student record:")
    for key, value in student.items():
        print(f"  {key}: {value}")
    
    # Get education details
    cursor.execute('SELECT type FROM Student WHERE regNo = %s', (reg_no,))
    student_type = cursor.fetchone()
    
    if student_type['type'] == 'UG':
        cursor.execute('SELECT * FROM UG WHERE regNo = %s', (reg_no,))
        edu = cursor.fetchone()
        print("\nUG details:")
    else:
        cursor.execute('SELECT * FROM PG WHERE regNo = %s', (reg_no,))
        edu = cursor.fetchone()
        print("\nPG details:")
    
    if edu:
        for key, value in edu.items():
            print(f"  {key}: {value}")

# Change this to your student registration number
student_reg_no = "YOUR_REG_NO"  # Replace with actual reg number
view_student(student_reg_no)

cursor.close()
conn.close()
