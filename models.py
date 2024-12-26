import sqlite3


def init_db():
    conn = sqlite3.connect("db.sqlite3")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            face_encoding TEXT NOT NULL
        )
    """
    )
    conn.commit()
    conn.close()


def add_user(name, face_encoding):
    conn = sqlite3.connect("db.sqlite3")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (name, face_encoding) VALUES (?, ?)",
        (name, str(face_encoding.tolist())),
    )
    conn.commit()
    conn.close()


def get_all_users():
    conn = sqlite3.connect("db.sqlite3")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, face_encoding FROM users")
    users = cursor.fetchall()
    conn.close()
    return users
