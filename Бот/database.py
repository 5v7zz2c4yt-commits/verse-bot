import sqlite3
def init_db():
    conn = sqlite3.connect('subscribers.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            chat_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            subscribed INTEGER DEFAULT 1
        )
    ''')
    conn.commit()
    conn.close()
def add_user(chat_id, username, first_name):
    conn = sqlite3.connect('subscribers.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO users (chat_id, username, first_name) 
        VALUES (?, ?, ?)
    ''', (chat_id, username, first_name))
    conn.commit()
    conn.close()
def get_all_users():
    conn = sqlite3.connect('subscribers.db')
    cursor = conn.cursor()
    cursor.execute('SELECT chat_id FROM users WHERE subscribed = 1')
    users = [row[0] for row in cursor.fetchall()]
    conn.close()
    return users