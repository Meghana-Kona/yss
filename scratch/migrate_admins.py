import sqlite3

def migrate_admins():
    conn = sqlite3.connect('instance/database.db')
    c = conn.cursor()
    # Rename old table
    c.execute('ALTER TABLE admins RENAME TO admins_old;')
    # Create new admins table without unique on email
    c.execute('''
    CREATE TABLE admins (
        id INTEGER NOT NULL PRIMARY KEY,
        lesson_no VARCHAR(20) NOT NULL,
        name VARCHAR(100) NOT NULL,
        email VARCHAR(120) NOT NULL,
        mobile VARCHAR(15) NOT NULL,
        password_hash VARCHAR(256) NOT NULL,
        is_main_admin BOOLEAN DEFAULT 0,
        reset_token VARCHAR(100),
        reset_token_expiry DATETIME,
        last_active DATETIME,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    ''')
    # Copy data
    c.execute('INSERT INTO admins (id, lesson_no, name, email, mobile, password_hash, is_main_admin, reset_token, reset_token_expiry, last_active, created_at) SELECT id, lesson_no, name, email, mobile, password_hash, is_main_admin, reset_token, reset_token_expiry, last_active, created_at FROM admins_old;')
    # Drop old table
    c.execute('DROP TABLE admins_old;')
    conn.commit()
    print('Admins table migrated successfully')

migrate_admins()
