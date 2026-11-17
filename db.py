import os
import sqlite3
from datetime import datetime

# Check for MySQL connector
try:
    import mysql.connector
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False

MYSQL_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
    'database': os.getenv('MYSQL_DB', 'travel_readiness_db'),
    'port': int(os.getenv('MYSQL_PORT', 3306))
}

SQLITE_PATH = os.path.join(os.path.dirname(__file__), 'travel_readiness.db')

def get_db_connection():
    """
    Returns an active database connection and engine identifier ('mysql' or 'sqlite').
    Gracefully falls back to SQLite if MySQL is unavailable or offline.
    """
    if MYSQL_AVAILABLE:
        try:
            conn = mysql.connector.connect(**MYSQL_CONFIG)
            return conn, 'mysql'
        except Exception:
            pass
            
    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    return conn, 'sqlite'

def init_database():
    """Initializes tables in the active database engine."""
    conn, engine = get_db_connection()
    cursor = conn.cursor()
    
    if engine == 'mysql':
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INT AUTO_INCREMENT PRIMARY KEY,
            full_name VARCHAR(100) NOT NULL,
            email VARCHAR(120) NOT NULL UNIQUE,
            phone VARCHAR(25),
            password_hash VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS travel_assessments (
            assessment_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            destination_country VARCHAR(100) NOT NULL,
            travel_date DATE NOT NULL,
            return_date DATE NOT NULL,
            travel_purpose VARCHAR(50) NOT NULL DEFAULT 'Tourism',
            passport_status VARCHAR(20) NOT NULL,
            passport_expiry_date DATE NOT NULL,
            visa_status VARCHAR(30) NOT NULL,
            return_ticket VARCHAR(10) NOT NULL,
            hotel_booking VARCHAR(10) NOT NULL,
            travel_insurance VARCHAR(10) NOT NULL,
            vaccination_status VARCHAR(10) NOT NULL,
            prediction_result VARCHAR(30) NOT NULL,
            readiness_score INT NOT NULL DEFAULT 0,
            missing_requirements TEXT,
            assessment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS travel_reports (
            report_id INT AUTO_INCREMENT PRIMARY KEY,
            assessment_id INT NOT NULL,
            user_id INT NOT NULL,
            report_path VARCHAR(255) NOT NULL,
            generated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (assessment_id) REFERENCES travel_assessments(assessment_id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );
        """)
        conn.commit()
    else:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS travel_assessments (
            assessment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            destination_country TEXT NOT NULL,
            travel_date TEXT NOT NULL,
            return_date TEXT NOT NULL,
            travel_purpose TEXT NOT NULL DEFAULT 'Tourism',
            passport_status TEXT NOT NULL,
            passport_expiry_date TEXT NOT NULL,
            visa_status TEXT NOT NULL,
            return_ticket TEXT NOT NULL,
            hotel_booking TEXT NOT NULL,
            travel_insurance TEXT NOT NULL,
            vaccination_status TEXT NOT NULL,
            prediction_result TEXT NOT NULL,
            readiness_score INTEGER NOT NULL DEFAULT 0,
            missing_requirements TEXT,
            assessment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS travel_reports (
            report_id INTEGER PRIMARY KEY AUTOINCREMENT,
            assessment_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            report_path TEXT NOT NULL,
            generated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (assessment_id) REFERENCES travel_assessments(assessment_id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );
        """)
        conn.commit()
        
    conn.close()

# ----------------- User Queries -----------------

def get_user_by_email(email):
    conn, engine = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE email = ?"
    if engine == 'mysql':
        query = query.replace('?', '%s')
    cursor.execute(query, (email.strip().lower(),))
    
    if engine == 'mysql':
        cols = [col[0] for col in cursor.description]
        row = cursor.fetchone()
        user = dict(zip(cols, row)) if row else None
    else:
        row = cursor.fetchone()
        user = dict(row) if row else None
        
    conn.close()
    return user

def get_user_by_id(user_id):
    conn, engine = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE user_id = ?"
    if engine == 'mysql':
        query = query.replace('?', '%s')
    cursor.execute(query, (user_id,))
    
    if engine == 'mysql':
        cols = [col[0] for col in cursor.description]
        row = cursor.fetchone()
        user = dict(zip(cols, row)) if row else None
    else:
        row = cursor.fetchone()
        user = dict(row) if row else None
        
    conn.close()
    return user

def create_user(full_name, email, phone, password_hash):
    conn, engine = get_db_connection()
    cursor = conn.cursor()
    query = "INSERT INTO users (full_name, email, phone, password_hash) VALUES (?, ?, ?, ?)"
    if engine == 'mysql':
        query = query.replace('?', '%s')
    cursor.execute(query, (full_name.strip(), email.strip().lower(), phone.strip(), password_hash))
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    return user_id

def update_user_profile(user_id, full_name, phone):
    conn, engine = get_db_connection()
    cursor = conn.cursor()
    query = "UPDATE users SET full_name = ?, phone = ? WHERE user_id = ?"
    if engine == 'mysql':
        query = query.replace('?', '%s')
    cursor.execute(query, (full_name.strip(), phone.strip(), user_id))
    conn.commit()
    conn.close()

def update_user_password(user_id, new_password_hash):
    conn, engine = get_db_connection()
    cursor = conn.cursor()
    query = "UPDATE users SET password_hash = ? WHERE user_id = ?"
    if engine == 'mysql':
        query = query.replace('?', '%s')
    cursor.execute(query, (new_password_hash, user_id))
    conn.commit()
    conn.close()

# ----------------- Assessment Queries -----------------

def save_assessment(assessment_data):
    conn, engine = get_db_connection()
    cursor = conn.cursor()
    query = """
    INSERT INTO travel_assessments (
        user_id, destination_country, travel_date, return_date,
        travel_purpose, passport_status, passport_expiry_date,
        visa_status, return_ticket, hotel_booking, travel_insurance,
        vaccination_status, prediction_result, readiness_score,
        missing_requirements
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    if engine == 'mysql':
        query = query.replace('?', '%s')
        
    values = (
        assessment_data['user_id'],
        assessment_data['destination_country'],
        assessment_data['travel_date'],
        assessment_data['return_date'],
        assessment_data['travel_purpose'],
        assessment_data['passport_status'],
        assessment_data['passport_expiry_date'],
        assessment_data['visa_status'],
        assessment_data['return_ticket'],
        assessment_data['hotel_booking'],
        assessment_data['travel_insurance'],
        assessment_data['vaccination_status'],
        assessment_data['prediction_result'],
        assessment_data['readiness_score'],
        assessment_data['missing_requirements']
    )
    cursor.execute(query, values)
    conn.commit()
    assessment_id = cursor.lastrowid
    conn.close()
    return assessment_id

def get_assessment_by_id(assessment_id, user_id=None):
    conn, engine = get_db_connection()
    cursor = conn.cursor()
    if user_id:
        query = "SELECT * FROM travel_assessments WHERE assessment_id = ? AND user_id = ?"
        params = (assessment_id, user_id)
    else:
        query = "SELECT * FROM travel_assessments WHERE assessment_id = ?"
        params = (assessment_id,)
        
    if engine == 'mysql':
        query = query.replace('?', '%s')
        
    cursor.execute(query, params)
    
    if engine == 'mysql':
        cols = [col[0] for col in cursor.description]
        row = cursor.fetchone()
        record = dict(zip(cols, row)) if row else None
    else:
        row = cursor.fetchone()
        record = dict(row) if row else None
        
    conn.close()
    return record

def get_user_assessments(user_id, limit=None):
    conn, engine = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM travel_assessments WHERE user_id = ? ORDER BY assessment_id DESC"
    if limit:
        query += f" LIMIT {int(limit)}"
        
    if engine == 'mysql':
        query = query.replace('?', '%s')
        
    cursor.execute(query, (user_id,))
    
    if engine == 'mysql':
        cols = [col[0] for col in cursor.description]
        records = [dict(zip(cols, r)) for r in cursor.fetchall()]
    else:
        records = [dict(r) for r in cursor.fetchall()]
        
    conn.close()
    return records

def get_user_assessment_stats(user_id):
    conn, engine = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT prediction_result, COUNT(*) FROM travel_assessments WHERE user_id = ? GROUP BY prediction_result"
    if engine == 'mysql':
        query = query.replace('?', '%s')
    cursor.execute(query, (user_id,))
    rows = cursor.fetchall()
    
    stats = {'total': 0, 'ready': 0, 'not_ready': 0}
    for row in rows:
        result = row[0]
        cnt = row[1]
        stats['total'] += cnt
        if 'Ready' in result and 'Not' not in result:
            stats['ready'] += cnt
        else:
            stats['not_ready'] += cnt
            
    conn.close()
    return stats

# ----------------- Report Queries -----------------

def save_report_record(assessment_id, user_id, report_path):
    conn, engine = get_db_connection()
    cursor = conn.cursor()
    query = "INSERT INTO travel_reports (assessment_id, user_id, report_path) VALUES (?, ?, ?)"
    if engine == 'mysql':
        query = query.replace('?', '%s')
    cursor.execute(query, (assessment_id, user_id, report_path))
    conn.commit()
    report_id = cursor.lastrowid
    conn.close()
    return report_id

def get_report_by_assessment(assessment_id):
    conn, engine = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM travel_reports WHERE assessment_id = ? ORDER BY report_id DESC LIMIT 1"
    if engine == 'mysql':
        query = query.replace('?', '%s')
    cursor.execute(query, (assessment_id,))
    
    if engine == 'mysql':
        cols = [col[0] for col in cursor.description]
        row = cursor.fetchone()
        record = dict(zip(cols, row)) if row else None
    else:
        row = cursor.fetchone()
        record = dict(row) if row else None
        
    conn.close()
    return record

