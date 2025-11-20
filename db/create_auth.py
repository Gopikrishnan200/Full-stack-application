import mysql.connector
from mysql.connector import Error
import os

try:
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=int(os.getenv("DB_PORT", 3306))
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
