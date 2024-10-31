import sqlite3
from datetime import datetime

def get_db_connection():
    conn = sqlite3.connect('fundtracking.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    with conn:
        # Create friends table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS friends (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
        ''')
        # Create contributions table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS contributions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                friend_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (friend_id) REFERENCES friends (id)
            )
        ''')
        
        # Insert friends if they don't already exist
        for friend in ["Haly", "Gwyna", "Rachelle Ann", "Alexes"]:
            conn.execute("INSERT OR IGNORE INTO friends (name) VALUES (?)", (friend,))
    conn.close()

def add_contribution(friend_id, amount):
    conn = get_db_connection()
    with conn:
        # Insert contribution with current timestamp
        conn.execute('''
            INSERT INTO contributions (friend_id, amount, date)
            VALUES (?, ?, ?)
        ''', (friend_id, amount, datetime.now()))
    conn.close()

def get_contributions_summary():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get detailed contributions
    cursor.execute('''
        SELECT f.name, c.amount, DATE(c.date) as date
        FROM friends f
        JOIN contributions c ON f.id = c.friend_id
        ORDER BY f.name, c.date
    ''')
    detailed_contributions = cursor.fetchall()

    # Get total contributions per friend
    cursor.execute('''
        SELECT f.name, SUM(c.amount) as total_contributed
        FROM friends f
        LEFT JOIN contributions c ON f.id = c.friend_id
        GROUP BY f.name
    ''')
    total_per_friend = cursor.fetchall()

    # Get overall total contributions
    cursor.execute('SELECT SUM(amount) as overall_total FROM contributions')
    overall_total = cursor.fetchone()['overall_total'] or 0

    conn.close()
    return detailed_contributions, total_per_friend, overall_total

def get_friend_id_by_name(name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM friends WHERE name = ?", (name,))
    friend = cursor.fetchone()
    conn.close()
    return friend['id'] if friend else None

def get_contributions_by_date(date):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT f.name, c.amount, c.id  -- Make sure to include c.id in the SELECT
        FROM friends f
        JOIN contributions c ON f.id = c.friend_id
        WHERE DATE(c.date) = ?
        ORDER BY f.name
    ''', (date,))

    contributions = cursor.fetchall()
    conn.close()
    return contributions

def get_contributions_summary_grouped_by_date():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get contributions grouped by date
    cursor.execute('''
        SELECT DATE(c.date) as date, SUM(c.amount) as total_amount
        FROM contributions c
        GROUP BY DATE(c.date)
        ORDER BY DATE(c.date) DESC
    ''')
    contributions_by_date = cursor.fetchall()
    
    conn.close()
    return contributions_by_date

# Initialize the database on the first run
init_db()
