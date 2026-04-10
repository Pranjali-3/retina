import sqlite3
import hashlib
from datetime import datetime

# -------------------------------
# 🔹 DATABASE CONFIG (SQLite is just a file!)
# -------------------------------
DB_NAME = "retino_db.sqlite"

# -------------------------------
# 🔹 CONNECT TO DATABASE
# -------------------------------
def get_connection():
    try:
        # SQLite creates the file automatically if it doesn't exist
        conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        # This makes results behave like a Dictionary (matching your MySQL DictCursor)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print("Error connecting to SQLite:", e)
        return None

# -------------------------------
# 🔹 CREATE TABLES
# -------------------------------
def create_tables():
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        
        # User Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Predictions Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            image_path TEXT,
            prediction TEXT,
            confidence REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """)

        conn.commit()
        conn.close()

# -------------------------------
# 🔐 HASH PASSWORD (Stays the same!)
# -------------------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# -------------------------------
# 👤 REGISTER USER
# -------------------------------
def register_user(name, email, password):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            hashed_pw = hash_password(password)
            # SQLite uses ? instead of %s
            cursor.execute("""
            INSERT INTO users (name, email, password)
            VALUES (?, ?, ?)
            """, (name, email, hashed_pw))
            conn.commit()
            return True
        except Exception as e:
            print("Registration Error:", e)
            return False
        finally:
            conn.close()

# -------------------------------
# 🔑 LOGIN USER
# -------------------------------
def login_user(email, password):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            hashed_pw = hash_password(password)
            cursor.execute("""
            SELECT * FROM users
            WHERE email=? AND password=?
            """, (email, hashed_pw))
            
            row = cursor.fetchone()
            # Convert row to dict to keep your app logic working
            return dict(row) if row else None
        finally:
            conn.close()

# -------------------------------
# 📊 SAVE PREDICTION
# -------------------------------
def save_prediction(user_id, image_path, prediction, confidence):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO predictions (user_id, image_path, prediction, confidence)
            VALUES (?, ?, ?, ?)
            """, (user_id, image_path, prediction, confidence))
            conn.commit()
        finally:
            conn.close()

# -------------------------------
# 📜 GET USER HISTORY
# -------------------------------
def get_user_history(user_id):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT * FROM predictions
            WHERE user_id=?
            ORDER BY created_at DESC
            """, (user_id,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

# -------------------------------
# 🚀 INIT FUNCTION
# -------------------------------
def init_db():
    # SQLite doesn't need a 'create_database' function 
    # as connect() does it automatically.
    create_tables() 

if __name__ == "__main__":
    init_db()
    print("✅ SQLite Database + Tables Ready!")