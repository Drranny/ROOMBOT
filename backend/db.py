import psycopg2

def get_db_connection():
    conn = psycopg2.connect(
        dbname="postgres",
        user="jiyu",
        password="",
        host="localhost"
    )
    return conn 