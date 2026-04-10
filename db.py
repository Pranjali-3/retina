import pymysql
import hashlib

# -------------------------------
# 🔹 DATABASE CONFIG
# -------------------------------
DB_NAME = "retino_db"

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "cursorclass": pymysql.cursors.DictCursor
}


# -------------------------------
# 🔹 CREATE DATABASE IF NOT EXISTS
# -------------------------------
def create_database():
    try:
        conn = pymysql.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"]
        )

        with conn.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")

        conn.close()

    except Exception as e:
        print("Error creating database:", e)


# -------------------------------
# 🔹 CONNECT TO DATABASE
# -------------------------------
def get_connection():
    try:
        conn = pymysql.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_NAME,
            cursorclass=pymysql.cursors.DictCursor
        )
        return conn

    except Exception as e:
        print("Error connecting to MySQL:", e)
        return None


# -------------------------------
# 🔹 CREATE TABLES
# -------------------------------
def create_tables():
    conn = get_connection()
    if conn:
        with conn.cursor() as cursor:

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100),
                email VARCHAR(100) UNIQUE,
                password VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                image_path VARCHAR(255),
                prediction VARCHAR(50),
                confidence FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """)

        conn.commit()
        conn.close()


# -------------------------------
# 🔐 HASH PASSWORD
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
            with conn.cursor() as cursor:
                hashed_pw = hash_password(password)

                cursor.execute("""
                INSERT INTO users (name, email, password)
                VALUES (%s, %s, %s)
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
            with conn.cursor() as cursor:
                hashed_pw = hash_password(password)

                cursor.execute("""
                SELECT * FROM users
                WHERE email=%s AND password=%s
                """, (email, hashed_pw))

                return cursor.fetchone()

        finally:
            conn.close()


# -------------------------------
# 📊 SAVE PREDICTION
# -------------------------------
def save_prediction(user_id, image_path, prediction, confidence):
    conn = get_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                INSERT INTO predictions (user_id, image_path, prediction, confidence)
                VALUES (%s, %s, %s, %s)
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
            with conn.cursor() as cursor:
                cursor.execute("""
                SELECT * FROM predictions
                WHERE user_id=%s
                ORDER BY created_at DESC
                """, (user_id,))

                return cursor.fetchall()

        finally:
            conn.close()


# -------------------------------
# 🚀 INIT FUNCTION (IMPORTANT)
# -------------------------------
def init_db():
    create_database()   # ✅ Create DB if not exists
    create_tables()     # ✅ Then create tables


# -------------------------------
# ▶️ RUN DIRECTLY
# -------------------------------
if __name__ == "__main__":
    init_db()
    print("✅ Database + Tables Ready!")