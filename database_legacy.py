import os
import sqlite3

# Try importing mysql.connector if installed
try:
    import mysql.connector
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False

DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
    'database': os.getenv('MYSQL_DB', 'travel_readiness_db'),
    'port': int(os.getenv('MYSQL_PORT', 3306))
}

SQLITE_PATH = os.path.join(os.path.dirname(__file__), 'travel_readiness.db')

def get_connection():
    """
    Attempts to connect to MySQL. If MySQL is unavailable or fails,
    gracefully falls back to SQLite so the application works seamlessly.
    """
    if MYSQL_AVAILABLE:
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            return conn, 'mysql'
        except Exception:
            pass
    # Fallback to SQLite
    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    return conn, 'sqlite'

def init_db():
    """Initializes tables in the active database engine."""
    conn, engine = get_connection()
    cursor = conn.cursor()
    
    if engine == 'mysql':
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            passenger_name VARCHAR(100),
            destination VARCHAR(100),
            passport_validity_months INT,
            visa_status VARCHAR(20),
            return_ticket VARCHAR(10),
            hotel_booking VARCHAR(10),
            travel_insurance VARCHAR(10),
            vaccination_status VARCHAR(10),
            readiness_prediction VARCHAR(30),
            confidence_score FLOAT,
            missing_items TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        conn.commit()
    else:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            passenger_name TEXT,
            destination TEXT,
            passport_validity_months INTEGER,
            visa_status TEXT,
            return_ticket TEXT,
            hotel_booking TEXT,
            travel_insurance TEXT,
            vaccination_status TEXT,
            readiness_prediction TEXT,
            confidence_score REAL,
            missing_items TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        conn.commit()
    conn.close()

def save_prediction(record):
    """Saves a prediction assessment to the database."""
    conn, engine = get_connection()
    cursor = conn.cursor()
    
    query = """
    INSERT INTO predictions (
        passenger_name, destination, passport_validity_months,
        visa_status, return_ticket, hotel_booking, travel_insurance,
        vaccination_status, readiness_prediction, confidence_score,
        missing_items
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    if engine == 'mysql':
        query = query.replace('?', '%s')
        
    values = (
        record.get('passenger_name', 'Anonymous'),
        record.get('destination', 'International'),
        record.get('passport_validity_months', 0),
        record.get('visa_status', 'No'),
        record.get('return_ticket', 'No'),
        record.get('hotel_booking', 'No'),
        record.get('travel_insurance', 'No'),
        record.get('vaccination_status', 'No'),
        record.get('readiness_prediction', 'Unknown'),
        record.get('confidence_score', 0.0),
        record.get('missing_items', '')
    )
    
    cursor.execute(query, values)
    conn.commit()
    inserted_id = cursor.lastrowid
    conn.close()
    return inserted_id

def get_recent_predictions(limit=50):
    """Fetches past predictions for review and history log."""
    conn, engine = get_connection()
    cursor = conn.cursor()
    
    query = f"SELECT * FROM predictions ORDER BY id DESC LIMIT {limit}"
    cursor.execute(query)
    
    if engine == 'mysql':
        cols = [col[0] for col in cursor.description]
        rows = [dict(zip(cols, r)) for r in cursor.fetchall()]
    else:
        rows = [dict(r) for r in cursor.fetchall()]
        
    conn.close()
    return rows

