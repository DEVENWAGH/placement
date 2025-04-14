import mysql.connector

# Database connection parameters
DB_NAME = "placement"
DB_USER = "root"
DB_PASS = "root"
DB_HOST = "127.0.0.1"

try:
    # Try to connect to the database
    conn = mysql.connector.connect(
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST
    )
    
    cursor = conn.cursor(dictionary=True)
    
    # Test query to verify users table
    cursor.execute("SELECT username, email, role FROM users LIMIT 5")
    users = cursor.fetchall()
    
    print("Database connection successful!")
    print("\nSample users in database:")
    for user in users:
        print(f"Username: {user['username']}, Email: {user['email']}, Role: {user['role']}")
    
    # Count users by role
    cursor.execute("SELECT role, COUNT(*) as count FROM users GROUP BY role")
    role_counts = cursor.fetchall()
    
    print("\nUser counts by role:")
    for role_count in role_counts:
        print(f"Role: {role_count['role']}, Count: {role_count['count']}")
    
    # Test password hashing
    cursor.execute("SELECT username, password FROM users LIMIT 1")
    user = cursor.fetchone()
    if user:
        print(f"\nSample hashed password for user '{user['username']}': {user['password'][:20]}...")
    
    cursor.close()
    conn.close()
    
except mysql.connector.Error as err:
    print(f"Database error: {err}")
