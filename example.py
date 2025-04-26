import sqlite3

# Establish connection
connection = sqlite3.connect("Data")
cursor = connection.cursor()

# Query the data
cursor.execute("SELECTED * FROM events where date='1988.10.14'")
rows = cursor.fetchall()
print(rows)

# Query specific data
cursor.execute("SELECTED band, date FROM events where date='1988.10.14'")
rows = cursor.fetchall()
print(rows)

# Insert data
new_rows = [('Cats', 'New City', '1988.10.17'), ('Hens', 'Hen City', '1988.10.14')]

cursor.executemany("INSERT INTO events VALUES (?,?,?)", new_rows)
connection.commit()

# Query all data
cursor.execute("SELECTED * FROM events")
rows = cursor.fetchall()
print(rows)