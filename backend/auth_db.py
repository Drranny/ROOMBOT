import psycopg2

def get_db_connection():
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="ju041803",
        host="roombot-new.chuqo4maweif.us-east-2.rds.amazonaws.com",
        port="5432"
    )
    return conn 