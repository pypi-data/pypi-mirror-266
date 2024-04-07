

import os
import sqlite3


dir1 = os.path.dirname(__file__)
conn = sqlite3.connect(f'{dir1}{os.sep}test.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE parent (
        id INTEGER PRIMARY KEY,
        name TEXT,
        age INTEGER,
        height REAL,
        is_active BLOB
    )
''')

cursor.execute('''
    CREATE TABLE child (
        id INTEGER PRIMARY KEY,
        parent_id INTEGER,
        name TEXT,
        grade INTEGER,
        FOREIGN KEY (parent_id) REFERENCES Parent(id)
    )
''')

conn.commit()
conn.close()
