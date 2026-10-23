import sqlite3

print("Running create_db.py...")

conn = sqlite3.connect("users.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'user' CHECK(role IN ('admin','user')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS loan_applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    gender TEXT NOT NULL,
    married TEXT NOT NULL,
    dependents TEXT NOT NULL,
    self_employed TEXT NOT NULL,
    income REAL NOT NULL,
    credit_history INTEGER NOT NULL,
    property_area TEXT NOT NULL,
    loan_status INTEGER NOT NULL,
    loan_amount REAL NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
""")

conn.commit()
conn.close()

print("DB created successfully.")