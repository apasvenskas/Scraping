import sqlite3
import os

db_file = "data.db"


# Match the data you intend to insert: ('Cats', 'New City', '1988.10.17') -> (TEXT, TEXT, TEXT)
create_table_sql = """
CREATE TABLE IF NOT EXISTS events (
    band TEXT,
    city TEXT,
    date TEXT
);
"""
# 'IF NOT EXISTS' prevents errors if the table is already there on subsequent runs

try:
    # Use 'with' for automatic connection management (commit/close)
    with sqlite3.connect(db_file) as connection:
        cursor = connection.cursor()
        print(f"Connected to {db_file}")

        print("Ensuring 'events' table exists...")
        cursor.execute(create_table_sql)
        print("'events' table is ready.")

        # Insert new data (example)
        new_rows = [('Cats', 'New City', '1988.10.17'),
                    ('Hens', 'Hen City', '1988.10.14')]
        print(f"Inserting new rows: {new_rows}")
        # Use executemany for inserting multiple rows
        cursor.executemany("INSERT INTO events (band, city, date) VALUES (?, ?, ?)", new_rows)
        print("Rows inserted.")

        # Query specific data (Corrected SQL: SELECT)
        print("Querying for date '1988.10.14'...")
        cursor.execute("SELECT band, date FROM events WHERE date=?", ('1988.10.14',)) # Use parameterization
        rows = cursor.fetchall()
        print(f"Found specific rows: {rows}")

        # Query all data (Corrected SQL: SELECT)
        print("Querying all data...")
        cursor.execute("SELECT * FROM events")
        rows = cursor.fetchall()
        print(f"All rows in events table: {rows}")

except sqlite3.Error as e:
    print(f"Database error: {e}")
except Exception as e:
    print(f"An error occurred: {e}")