import sqlite3

conn = sqlite3.connect('users.db')
c = conn.cursor()

# Create users table
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
''')

# Create operations table
c.execute('''
CREATE TABLE IF NOT EXISTS operations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation TEXT NOT NULL,
    matrix1 TEXT NOT NULL,
    matrix2 TEXT,
    result TEXT NOT NULL
)
''')

# Check if admin user exists
c.execute('SELECT COUNT(*) FROM users WHERE username = ?', ('admin',))
admin_exists = c.fetchone()[0]

# Insert admin user if not exists
if not admin_exists:
    c.execute('INSERT INTO users (username, password) VALUES (?, ?)', ('admin', 'password'))
    print("Admin user inserted successfully.")
else:
    print("Admin user already exists.")

conn.commit()
conn.close()
