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
cursor = conn.cursor()

# Create the stats table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS stats (
    id INT AUTO_INCREMENT PRIMARY KEY,
    regno VARCHAR(10) NOT NULL,
    job_Id VARCHAR(50) NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    company VARCHAR(50),
    position VARCHAR(50),
    type VARCHAR(20),
    compensation INT,
    placement_date DATE DEFAULT CURRENT_DATE,
    FOREIGN KEY (regno) REFERENCES Student(regNo) ON DELETE CASCADE,
    FOREIGN KEY (job_Id) REFERENCES Job(job_Id) ON DELETE CASCADE
)
""")

print("Stats table created successfully")

conn.commit()
cursor.close()
conn.close()
