import mysql.connector
from mysql.connector import Error

try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",           # your MySQL username
        password="gopi2004",  # your MySQL password
        database="auth"        # your database name
    )
    cur = conn.cursor()

    # Drop task table if exists
    cur.execute("DROP TABLE IF EXISTS task")

    # ------------------ USERS TABLE ------------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL
    )
    """)

    # ------------------ TASK TABLE ------------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS task (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        name VARCHAR(255) NOT NULL,
        des TEXT NOT NULL,
        size VARCHAR(50) NOT NULL,
        status VARCHAR(50) NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)

    conn.commit()
    print("Tables created successfully!")

except Error as e:
    print("Error while connecting to MySQL", e)

finally:
    if conn.is_connected():
        cur.close()
        conn.close()
