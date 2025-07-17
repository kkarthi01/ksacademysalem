
import sqlite3

# Connect to the database (creates it if it doesn't exist)
conn = sqlite3.connect('data.db')
cur = conn.cursor()

# Drop existing tables (optional - only if reinitializing)
cur.execute('DROP TABLE IF EXISTS students')
cur.execute('DROP TABLE IF EXISTS materials')

# Create students table with category
cur.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        userid TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        category TEXT NOT NULL
    )
''')

# Create materials table with category
cur.execute('''
    CREATE TABLE IF NOT EXISTS materials (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        link TEXT NOT NULL,
        category TEXT NOT NULL
    )
''')

# Commit changes and close connection
conn.commit()
conn.close()

print("✅ Database and tables created successfully.")
