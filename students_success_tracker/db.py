import sqlite3
from datetime import datetime
from typing import List, Optional, Dict

DB_NAME = "success_tracker.db"
VALID_STATUSES = ["active", "probation", "graduated"]


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the database and create the students table if it does not exist."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                major TEXT NOT NULL,
                gpa REAL CHECK (gpa BETWEEN 0 AND 4),
                status TEXT CHECK (status IN ('active','probation','graduated')) DEFAULT 'active',
                last_updated TEXT
            );
        """)
        conn.commit()


def add_student(name: str, email: str, major: str, gpa: float, status: str = "active") -> int:
    if gpa < 0 or gpa > 4:
        raise ValueError("GPA must be between 0 and 4")
    if status not in VALID_STATUSES:
        raise ValueError(f"Status must be one of {VALID_STATUSES}")

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO students (name, email, major, gpa, status, last_updated)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, email, major, gpa, status, datetime.utcnow().isoformat()))
        conn.commit()
        return cursor.lastrowid


def get_students(status: Optional[str] = None) -> List[Dict]:
    with get_connection() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM students"
        params = ()
        if status:
            query += " WHERE status = ?"
            params = (status,)
        query += " ORDER BY gpa DESC"
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]


def find_students_by_major(major: str) -> List[Dict]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM students WHERE major = ? ORDER BY gpa DESC
        """, (major,))
        return [dict(row) for row in cursor.fetchall()]


def update_student_gpa(student_id: int, gpa: float) -> int:
    if gpa < 0 or gpa > 4:
        raise ValueError("GPA must be between 0 and 4")
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE students SET gpa = ?, last_updated = ? WHERE id = ?
        """, (gpa, datetime.utcnow().isoformat(), student_id))
        conn.commit()
        return cursor.rowcount


def delete_student(student_id: int) -> int:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
        conn.commit()
        return cursor.rowcount
