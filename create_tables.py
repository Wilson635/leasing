import psycopg2
from psycopg2 import sql

# Paramètres de connexion à PostgreSQL
db_config = {
    "dbname": "leasing_db",
    "user": "postgres",
    "password": "kally@2003",
    "host": "localhost",
    "port": "5432"  # Exemple: "5432"
}

# Connexion et création de la table dans PostgreSQL
try:
    with psycopg2.connect(**db_config) as conn:
        with conn.cursor() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS leasing_db (
                    id SERIAL PRIMARY KEY,
                    agence varchar(255),
                    num_ag INTEGER,
                    num_compte INTEGER UNIQUE,
                    cle INTEGER UNIQUE,
                    nom varchar(255),
                    prenom varchar(255),
                    besoin varchar(255),
                    montant INTEGER
                )
            ''')
            print("Connected to PostgreSQL and created table successfully!")
except Exception as e:
    print(f"An error occurred: {e}")
