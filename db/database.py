import mysql.connector
from mysql.connector import Error

def get_db():
    """Return a MySQL connection"""
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",           # your MySQL username
            password="gopi2004",   # your MySQL password
            database="auth"        # your database name
        )
        return conn
    except Error as e:
        print("Error connecting to MySQL:", e)
        return None
