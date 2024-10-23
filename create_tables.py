import sqlite3

conn = sqlite3.connect('database.db')
print("Connected to database successfully")

conn.execute(
    'CREATE TABLE leasing (id INTEGER PRIMARY KEY AUTOINCREMENT, agence TEXT, num_ag REAL, num_compte REAL, cle REAL, nom TEXT, prenom TEXT, besoin TEXT, montant REAL)')
print("Created table successfully!")

conn.close()
